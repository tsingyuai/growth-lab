#!/usr/bin/env python3
"""Normalize social platform exports into privacy-preserving aggregates."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FIELD_ALIASES = {
    "date": ("date", "day", "publish_date", "created_at", "日期", "时间", "发布时间"),
    "post": ("post_id", "article_id", "note_id", "url", "link", "内容ID", "笔记ID", "文章ID", "链接"),
    "title": ("title", "name", "标题", "内容标题", "文章标题", "笔记标题"),
    "impressions": ("impressions", "exposure", "reach", "曝光", "展现", "推荐曝光"),
    "views": ("views", "reads", "read_count", "阅读", "阅读数", "浏览", "浏览量", "观看"),
    "likes": ("likes", "like_count", "点赞", "点赞数"),
    "comments": ("comments", "comment_count", "评论", "评论数"),
    "saves": ("saves", "favorites", "collects", "收藏", "收藏数"),
    "shares": ("shares", "share_count", "分享", "转发", "分享数"),
    "follows": ("follows", "follow_count", "新增关注", "关注"),
    "clicks": ("clicks", "link_clicks", "跳转", "点击", "链接点击"),
}

METRICS = ("impressions", "views", "likes", "comments", "saves", "shares", "follows", "clicks")


def read_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".csv":
        return [dict(row) for row in csv.DictReader(text.splitlines())]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        records = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number} is not a JSON object")
            records.append(value)
        return records
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        records = next((payload[key] for key in ("posts", "articles", "notes", "data", "results") if isinstance(payload.get(key), list)), None)
        if records is None:
            records = [payload]
    else:
        raise ValueError("JSON input must be an object, an array, or newline-delimited objects")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("every record must be an object")
    return records


def get_value(record: dict[str, Any], field: str | None) -> Any:
    if not field:
        return None
    value: Any = record
    for part in field.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def available_fields(records: list[dict[str, Any]]) -> set[str]:
    fields: set[str] = set()
    for record in records[:100]:
        fields.update(record.keys())
    return fields


def resolve_field(records: list[dict[str, Any]], kind: str, explicit: str | None, required: bool = False) -> str | None:
    if explicit:
        if not any(get_value(record, explicit) not in (None, "") for record in records[:100]):
            raise ValueError(f"field '{explicit}' was not found in the sampled records")
        return explicit
    fields = available_fields(records)
    matches = [alias for alias in FIELD_ALIASES[kind] if alias in fields]
    if len(matches) == 1:
        return matches[0]
    if required and not matches:
        raise ValueError(f"could not find a {kind} field; pass --{kind}-field explicitly")
    if len(matches) > 1:
        raise ValueError(f"multiple possible {kind} fields found ({', '.join(matches)}); pass --{kind}-field explicitly")
    return None


def parse_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)) or str(value).strip().isdigit():
        numeric = float(value)
        if numeric > 10_000_000_000:
            numeric /= 1000
        return datetime.fromtimestamp(numeric, tz=timezone.utc).date().isoformat()
    raw = str(value).strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    for candidate in (raw, raw.replace("/", "-")):
        try:
            return datetime.fromisoformat(candidate).date().isoformat()
        except ValueError:
            pass
    raise ValueError("date is not ISO-8601 or Unix time")


def parse_number(value: Any) -> int:
    if value in (None, ""):
        return 0
    raw = str(value).strip().replace(",", "").replace("%", "")
    if raw in {"-", "--"}:
        return 0
    try:
        return int(float(raw))
    except ValueError as exc:
        raise ValueError(f"not numeric: {value}") from exc


def ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def normalize(records: list[dict[str, Any]], fields: dict[str, str | None], platform: str) -> dict[str, Any]:
    quality = Counter()
    posts: dict[str, dict[str, Any]] = {}
    dates_by_post: dict[str, set[str]] = defaultdict(set)
    for record in records:
        quality["input_rows"] += 1
        post_id = str(get_value(record, fields["post"]) or "").strip()
        if not post_id:
            quality["missing_post"] += 1
            continue
        try:
            date_value = parse_date(get_value(record, fields["date"])) if fields["date"] else None
            metrics = {metric: parse_number(get_value(record, fields[metric])) for metric in METRICS if fields.get(metric)}
        except ValueError:
            quality["invalid_values"] += 1
            continue
        title = str(get_value(record, fields["title"]) or "").strip()
        if post_id not in posts:
            posts[post_id] = {"post": post_id, "title": title, **{metric: 0 for metric in METRICS}}
        elif title and not posts[post_id]["title"]:
            posts[post_id]["title"] = title
        if date_value:
            dates_by_post[post_id].add(date_value)
        for metric, value in metrics.items():
            posts[post_id][metric] += value
        quality["usable_rows"] += 1
    totals = {metric: sum(post[metric] for post in posts.values()) for metric in METRICS}
    post_rows = []
    for post_id, post in posts.items():
        views = post["views"]
        impressions = post["impressions"]
        post_rows.append({
            **post,
            "date_count": len(dates_by_post[post_id]),
            "engagements": post["likes"] + post["comments"] + post["saves"] + post["shares"],
            "view_rate": ratio(views, impressions),
            "engagement_rate_by_view": ratio(post["likes"] + post["comments"] + post["saves"] + post["shares"], views),
            "click_rate_by_view": ratio(post["clicks"], views),
        })
    post_rows.sort(key=lambda item: (item["views"], item["impressions"], item["engagements"]), reverse=True)
    return {
        "schema_version": 1,
        "privacy": "aggregate output; raw user identifiers, comments, messages, and row payloads omitted",
        "platform": platform,
        "field_mapping": fields,
        "quality": {
            "input_rows": quality["input_rows"],
            "usable_rows": quality["usable_rows"],
            "missing_post": quality["missing_post"],
            "invalid_values": quality["invalid_values"],
            "unique_posts": len(posts),
        },
        "totals": {
            **totals,
            "engagements": totals["likes"] + totals["comments"] + totals["saves"] + totals["shares"],
            "view_rate": ratio(totals["views"], totals["impressions"]),
            "engagement_rate_by_view": ratio(totals["likes"] + totals["comments"] + totals["saves"] + totals["shares"], totals["views"]),
            "click_rate_by_view": ratio(totals["clicks"], totals["views"]),
        },
        "posts": post_rows,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize social platform CSV/JSON/NDJSON exports into aggregate evidence.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--platform", required=True, help="Platform name, e.g. xiaohongshu or wechat-official-account")
    parser.add_argument("--date-field")
    parser.add_argument("--post-field")
    parser.add_argument("--title-field")
    for metric in METRICS:
        parser.add_argument(f"--{metric}-field")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--compact", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        records = read_records(args.input)
        if not records:
            raise ValueError("the export contains no records")
        fields = {
            "date": resolve_field(records, "date", args.date_field),
            "post": resolve_field(records, "post", args.post_field, required=True),
            "title": resolve_field(records, "title", args.title_field),
        }
        for metric in METRICS:
            fields[metric] = resolve_field(records, metric, getattr(args, f"{metric}_field"))
        result = normalize(records, fields, args.platform)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2)
    try:
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"error: could not write aggregate output: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
