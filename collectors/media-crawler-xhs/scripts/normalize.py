#!/usr/bin/env python3
"""把 MediaCrawler 的 contents.jsonl 标准化成 index.json，并生成跨主题 INDEX.md。

用法：
  python3 collectors/media-crawler-xhs/scripts/normalize.py memory/<loop>/samples/xhs/<主题>
  python3 collectors/media-crawler-xhs/scripts/normalize.py --all memory/<loop>/samples/xhs
  python3 collectors/media-crawler-xhs/scripts/normalize.py --library-root memory/<loop>/libraries/xhs <主题目录>

可选的 --library-root 会派生通用候选样本库，供 Model 把产品能力证据映射到内容机会；
它不绑定产品名、不下载图片，也不假设任何产品 schema。
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path


def parse_count(value: object) -> int:
    """把 10万+、6.1万、5k 等互动数字符串转换为整数。"""
    if value is None:
        return 0
    text = str(value).strip().replace("+", "")
    if not text:
        return 0
    try:
        if text[-1] in ("万", "w", "W"):
            return int(float(text[:-1]) * 10_000)
        if text[-1] in ("k", "K"):
            return int(float(text[:-1]) * 1_000)
        return int(float(text))
    except (ValueError, IndexError):
        return 0


def normalize_topic(topic_dir: Path, now: dt.datetime) -> dict | None:
    source = topic_dir / "contents.jsonl"
    if not source.exists():
        return None

    notes = []
    for line_no, raw in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{source}:{line_no}: JSON 无效：{exc}") from exc

        published = ""
        age_days = None
        timestamp = item.get("time")
        if timestamp:
            published_at = dt.datetime.fromtimestamp(float(timestamp) / 1000)
            published = published_at.date().isoformat()
            age_days = round((now - published_at).total_seconds() / 86_400, 1)

        notes.append({
            "note_id": item.get("note_id", ""),
            "type": item.get("type", ""),
            "title": item.get("title", ""),
            "desc": item.get("desc", ""),
            "user_nickname": item.get("nickname", ""),
            "published": published,
            "age_days": age_days,
            "in_30d": age_days is not None and age_days <= 30,
            "likes": parse_count(item.get("liked_count")),
            "collected": parse_count(item.get("collected_count")),
            "comments": parse_count(item.get("comment_count")),
            "shares": parse_count(item.get("share_count")),
            "ip_location": item.get("ip_location", ""),
            "tag_list": item.get("tag_list", ""),
            "note_url": item.get("note_url", ""),
            "image_list": item.get("image_list", ""),
            "video_url": item.get("video_url", ""),
        })

    notes.sort(key=lambda note: note["likes"], reverse=True)

    def within(days: int) -> int:
        return sum(1 for note in notes if note["age_days"] is not None and note["age_days"] <= days)

    result = {
        "topic": topic_dir.name,
        "platform": "xhs",
        "tool": "MediaCrawler",
        "normalized_at": now.date().isoformat(),
        "raw_count": len(notes),
        "windows": {"30d": within(30), "60d": within(60), "90d": within(90)},
        "notes": notes,
    }
    (topic_dir / "index.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def build_master_index(base: Path, results: list[dict], now: dt.datetime) -> None:
    lines = [
        f"# {base.name} · 小红书样本总索引",
        f"> 由 normalize.py 生成于 {now.date().isoformat()}。",
        "",
        "| 主题 | 样本数 | 近30天 | TOP3 标题（赞） |",
        "|---|---:|---:|---|",
    ]
    for result in sorted(results, key=lambda item: -item["raw_count"]):
        top3 = " / ".join(
            f"{note['title'][:10]}({note['likes']})" for note in result["notes"][:3]
        )
        lines.append(
            f"| {result['topic']} | {result['raw_count']} | {result['windows']['30d']} | {top3} |"
        )
    (base / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def derive_library(result: dict, library_root: Path) -> int:
    """把标准化结果派生为可人工策展的通用候选样本条目。"""
    count = 0
    candidates = library_root / "candidates"
    for note in result["notes"]:
        note_id = note.get("note_id")
        if not note_id:
            continue
        entry_dir = candidates / note_id
        entry_file = entry_dir / "entry.json"
        human = {
            "curation": "candidate",
            "why_selected": "",
            "product_capability_refs": [],
            "analysis": "",
        }
        if entry_file.exists():
            try:
                previous = json.loads(entry_file.read_text(encoding="utf-8"))
                for key in human:
                    if key in previous:
                        human[key] = previous[key]
            except (json.JSONDecodeError, OSError):
                pass

        entry = {
            "schema": "growth-lab/xhs-library-entry/v1",
            "platform": "xhs",
            "note_id": note_id,
            "source_topic": result["topic"],
            "source_tool": result["tool"],
            "title": note.get("title", ""),
            "content": note.get("desc", ""),
            "content_incomplete": note.get("type") == "video" or not note.get("desc", "").strip(),
            "type": note.get("type", ""),
            "author": note.get("user_nickname", ""),
            "published": note.get("published", ""),
            "metrics": {
                "likes": note.get("likes", 0),
                "collected": note.get("collected", 0),
                "comments": note.get("comments", 0),
                "shares": note.get("shares", 0),
            },
            "tags": [tag for tag in str(note.get("tag_list", "")).split(",") if tag],
            "canonical_url": note.get("note_url", ""),
            "media_urls": [url for url in str(note.get("image_list", "")).split(",") if url],
            "video_url": note.get("video_url", ""),
            **human,
        }
        entry_dir.mkdir(parents=True, exist_ok=True)
        entry_file.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        count += 1
    return count


def main() -> None:
    raw = sys.argv[1:]
    now = dt.datetime.now()
    if not raw:
        print(__doc__)
        return

    library_root = None
    args = []
    index = 0
    while index < len(raw):
        value = raw[index]
        if value == "--library-root":
            index += 1
            if index >= len(raw):
                raise SystemExit("--library-root 后必须提供目录")
            library_root = Path(raw[index])
        else:
            args.append(value)
        index += 1

    if args[0] == "--all":
        if len(args) != 2:
            raise SystemExit("用法：normalize.py --all <samples/xhs 目录>")
        base = Path(args[1])
        if not base.is_dir():
            raise SystemExit(f"目录不存在：{base}")
        results = []
        for topic_dir in sorted(path for path in base.iterdir() if path.is_dir()):
            result = normalize_topic(topic_dir, now)
            if result:
                results.append(result)
                if library_root:
                    derive_library(result, library_root)
                print(f"✓ {topic_dir.name}: {result['raw_count']} 条")
        if results:
            build_master_index(base, results, now)
        return

    for value in args:
        topic_dir = Path(value)
        result = normalize_topic(topic_dir, now)
        if result and library_root:
            derived = derive_library(result, library_root)
            print(f"  ↳ 候选样本库：{derived} 条")
        print(f"✓ {value}: {result['raw_count']} 条" if result else f"✗ {value}: 无 contents.jsonl")


if __name__ == "__main__":
    main()
