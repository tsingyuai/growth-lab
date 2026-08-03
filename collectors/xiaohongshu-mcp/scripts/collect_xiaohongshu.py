#!/usr/bin/env python3
"""Collect sanitized Xiaohongshu search evidence through a local MCP service."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ENDPOINT = "http://127.0.0.1:18063"
DEFAULT_LIMIT = 25
MAX_BATCH_SIZE = 30
MAX_VISUAL_CANDIDATES = 8
RISK_CODES = ("460", "461", "471")


class CollectorError(RuntimeError):
    pass


def load_repo_env() -> None:
    repo = Path(__file__).resolve().parents[3]
    for filename in (".env.local", ".env"):
        env_file = repo / filename
        if not env_file.exists():
            continue
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key in {"XHS_MCP_ENDPOINT", "XHS_MCP_TIMEOUT_SECONDS", "DEFAULT_SAMPLE_LIMIT"} and key not in os.environ:
                os.environ[key] = value.strip().strip('"').strip("'")


def validate_local_endpoint(endpoint: str) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise CollectorError("XHS_MCP_ENDPOINT 必须是本机 HTTP 地址")
    if not parsed.port:
        raise CollectorError("XHS_MCP_ENDPOINT 必须包含端口")
    return endpoint.rstrip("/")


class XiaohongshuClient:
    def __init__(self, endpoint: str, timeout: float) -> None:
        self.endpoint = validate_local_endpoint(endpoint)
        self.timeout = timeout
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.endpoint}{path}", data=body, headers=headers, method=method
        )
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise CollectorError(self.error_message(exc.code, raw)) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise CollectorError(f"无法连接本机 xiaohongshu-mcp: {exc}") from exc
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CollectorError("xiaohongshu-mcp 返回了非 JSON 响应") from exc
        if not envelope.get("success"):
            raise CollectorError(self.error_message(200, raw))
        return envelope.get("data")

    @staticmethod
    def error_message(status: int, raw: str) -> str:
        try:
            payload = json.loads(raw)
            message = payload.get("error") or payload.get("message") or raw
            details = payload.get("details")
            if details:
                message = f"{message}: {details}"
        except json.JSONDecodeError:
            message = raw[:300]
        prefix = "检测到平台风控，已停止且不会重试" if any(
            code in str(message) for code in RISK_CODES
        ) else f"xiaohongshu-mcp API 错误 (HTTP {status})"
        return f"{prefix}: {message}"

    def check_ready(self) -> None:
        self.request("GET", "/health")
        status = self.request("GET", "/api/v1/login/status")
        if not isinstance(status, dict) or not status.get("is_logged_in"):
            raise CollectorError("xiaohongshu-mcp 服务可用，但小红书尚未登录")

    def search(self, keyword: str, limit: int) -> list[dict[str, Any]]:
        data = self.request(
            "POST",
            "/api/v1/feeds/search",
            {"keyword": keyword, "filters": {}, "max_items": limit, "max_scrolls": 0},
        )
        feeds = data.get("feeds") if isinstance(data, dict) else None
        if not isinstance(feeds, list):
            raise CollectorError("搜索响应缺少 data.feeds 数组")
        return feeds

    def detail(self, feed_id: str, xsec_token: str) -> dict[str, Any]:
        data = self.request(
            "POST",
            "/api/v1/feeds/detail",
            {"feed_id": feed_id, "xsec_token": xsec_token, "load_all_comments": False},
        )
        detail = data.get("data") if isinstance(data, dict) else None
        note = detail.get("note") if isinstance(detail, dict) else None
        if not isinstance(note, dict):
            raise CollectorError(f"笔记 {feed_id} 的详情响应缺少 note")
        return note


def sanitize_feed(feed: dict[str, Any]) -> dict[str, Any] | None:
    if feed.get("modelType") != "note":
        return None
    note_id = str(feed.get("id") or "").strip()
    if not note_id:
        return None
    card = feed.get("noteCard") or {}
    user = card.get("user") or {}
    interaction = card.get("interactInfo") or {}
    return {
        "note_id": note_id,
        "public_url": f"https://www.xiaohongshu.com/explore/{note_id}",
        "title": str(card.get("displayTitle") or ""),
        "note_type": str(card.get("type") or ""),
        "author": str(user.get("nickname") or user.get("nickName") or ""),
        "visible_engagement": {
            "likes": str(interaction.get("likedCount") or "0"),
            "comments": str(interaction.get("commentCount") or "0"),
            "saves": str(interaction.get("collectedCount") or "0"),
            "shares": str(interaction.get("sharedCount") or "0"),
        },
        "has_cover": bool(card.get("cover")),
    }


def build_evidence(keyword: str, feeds: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for feed in feeds:
        item = sanitize_feed(feed)
        if not item or item["note_id"] in seen:
            continue
        seen.add(item["note_id"])
        items.append(item)
        if len(items) >= limit:
            break
    return {
        "schema_version": 1,
        "collected_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "platform": "xiaohongshu",
        "query": keyword,
        "access_mode": "authorized read-only browser session via local xiaohongshu-mcp",
        "scope": "search cards only; no detail pages, comments, image files, or account actions",
        "privacy": "session tokens, credential-bearing URLs, avatar URLs, and raw response fields omitted",
        "requested": limit,
        "collected": len(items),
        "items": items,
    }


def parse_count(value: Any) -> int:
    raw = str(value or "0").strip().replace(",", "").replace("+", "")
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([万wWkK]?)", raw)
    if not match:
        return 0
    multiplier = {"万": 10_000, "w": 10_000, "W": 10_000, "k": 1_000, "K": 1_000}.get(
        match.group(2), 1
    )
    return int(float(match.group(1)) * multiplier)


def extract_cover_url(feed: dict[str, Any]) -> str | None:
    cover = (feed.get("noteCard") or {}).get("cover") or {}
    if not isinstance(cover, dict):
        return None
    for key in ("urlDefault", "urlPre", "url", "url_default", "url_pre"):
        value = cover.get(key)
        if value:
            return str(value)
    for item in cover.get("infoList") or []:
        if isinstance(item, dict) and item.get("url"):
            return str(item["url"])
    return None


def select_visual_feeds(
    feeds: list[dict[str, Any]], selected_note_ids: list[str]
) -> list[dict[str, Any]]:
    by_id = {
        str(feed.get("id")): feed
        for feed in feeds
        if feed.get("modelType") == "note" and feed.get("id") and feed.get("xsecToken")
    }
    missing = [note_id for note_id in selected_note_ids if note_id not in by_id]
    if missing:
        raise CollectorError(f"视觉审查选中的笔记未出现在本次搜索结果中: {', '.join(missing)}")
    return [by_id[note_id] for note_id in selected_note_ids]


def detail_to_candidate(note: dict[str, Any], fallback_id: str) -> tuple[dict[str, Any], list[str]]:
    note_id = str(note.get("noteId") or note.get("id") or fallback_id)
    user = note.get("user") or {}
    interaction = note.get("interactInfo") or {}
    image_urls: list[str] = []
    for image in note.get("imageList") or []:
        url = image.get("urlDefault") or image.get("urlPre")
        if url and url not in image_urls:
            image_urls.append(str(url))
    candidate = {
        "note_id": note_id,
        "public_url": f"https://www.xiaohongshu.com/explore/{note_id}",
        "title": str(note.get("title") or ""),
        "description": str(note.get("desc") or ""),
        "note_type": str(note.get("type") or ""),
        "author": str(user.get("nickname") or user.get("nickName") or ""),
        "visible_engagement": {
            "likes": str(interaction.get("likedCount") or "0"),
            "comments": str(interaction.get("commentCount") or "0"),
            "saves": str(interaction.get("collectedCount") or "0"),
            "shares": str(interaction.get("sharedCount") or "0"),
        },
    }
    return candidate, image_urls


def image_extension(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    return ".bin"


def download_image(opener: urllib.request.OpenerDirector, url: str, timeout: float) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(request, timeout=timeout) as response:
        if response.status != 200:
            raise CollectorError(f"图片下载返回 HTTP {response.status}")
        return response.read()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_cover_contact_sheets(output_dir: Path, items: list[dict[str, Any]]) -> list[str]:
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        print("warning: Pillow 不可用，已保留首图文件但未生成联系表", file=sys.stderr)
        return []

    sheet_files: list[str] = []
    sheet_dir = output_dir / "cover-pool"
    for page_start in range(0, len(items), 4):
        page_items = items[page_start : page_start + 4]
        sheet = Image.new("RGB", (1080, 1440), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, item in enumerate(page_items):
            column = offset % 2
            row = offset // 2
            left = column * 540 + 20
            top = row * 720 + 20
            image_path = output_dir / item["cover_file"]
            with Image.open(image_path) as source:
                source = ImageOps.exif_transpose(source).convert("RGB")
                fitted = ImageOps.contain(source, (500, 620))
            image_left = left + (500 - fitted.width) // 2
            image_top = top + 55 + (620 - fitted.height) // 2
            sheet.paste(fitted, (image_left, image_top))
            draw.rectangle((left, top, left + 500, top + 45), fill="#111827")
            draw.text(
                (left + 12, top + 12),
                f"{page_start + offset + 1:02d}  {item['note_id']}",
                fill="white",
            )
        sheet_path = sheet_dir / f"contact-sheet-{page_start // 4 + 1:02d}.jpg"
        sheet.save(sheet_path, "JPEG", quality=90, optimize=True)
        sheet_files.append(sheet_path.relative_to(output_dir).as_posix())
    return sheet_files


def prepare_cover_pool(
    client: XiaohongshuClient,
    feeds: list[dict[str, Any]],
    output_dir: Path,
    cover_count: int,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for feed in feeds:
        if len(items) >= cover_count:
            break
        public_item = sanitize_feed(feed)
        cover_url = extract_cover_url(feed)
        if not public_item or not cover_url:
            continue
        try:
            data = download_image(client.opener, cover_url, client.timeout)
        except (CollectorError, OSError, urllib.error.URLError, TimeoutError) as exc:
            print(f"warning: {public_item['note_id']} 首图下载失败: {exc}", file=sys.stderr)
            continue
        extension = image_extension(data)
        if extension == ".bin":
            print(f"warning: {public_item['note_id']} 首图格式未知，已跳过", file=sys.stderr)
            continue
        cover_path = output_dir / "cover-pool" / f"{len(items) + 1:02d}-{public_item['note_id']}{extension}"
        cover_path.parent.mkdir(parents=True, exist_ok=True)
        cover_path.write_bytes(data)
        public_item["cover_file"] = cover_path.relative_to(output_dir).as_posix()
        items.append(public_item)
    contact_sheets = build_cover_contact_sheets(output_dir, items)
    manifest = {
        "schema_version": 1,
        "platform": "xiaohongshu",
        "review_status": "pending_visual_review",
        "selection_policy": (
            "Review every downloaded cover for promotional layout quality before requesting details; "
            "engagement is supporting evidence only, and zero qualifying covers is valid."
        ),
        "cover_count": len(items),
        "contact_sheets": contact_sheets,
        "items": items,
    }
    write_json(output_dir / "cover-pool.json", manifest)
    return manifest


def wait_for_review_selection(selection_file: Path, wait_seconds: float) -> list[str]:
    deadline = time.monotonic() + wait_seconds
    print(
        json.dumps(
            {
                "status": "waiting-for-cover-review",
                "selection_file": str(selection_file),
                "selection_format": {"note_ids": ["public-note-id"]},
                "empty_selection_allowed": True,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    while not selection_file.is_file():
        if time.monotonic() >= deadline:
            raise CollectorError(f"等待首图审查超时（{wait_seconds:g} 秒），未请求任何详情")
        time.sleep(0.5)
    payload = json.loads(selection_file.read_text(encoding="utf-8"))
    note_ids = payload.get("note_ids") if isinstance(payload, dict) else None
    if not isinstance(note_ids, list) or any(not isinstance(item, str) for item in note_ids):
        raise CollectorError("首图审查文件必须是包含 note_ids 字符串数组的 JSON 对象")
    normalized = [item.strip() for item in note_ids if item.strip()]
    if len(normalized) != len(set(normalized)):
        raise CollectorError("首图审查文件包含重复 note ID")
    if len(normalized) > MAX_VISUAL_CANDIDATES:
        raise CollectorError(f"首图审查最多选择 {MAX_VISUAL_CANDIDATES} 篇")
    return normalized


def prepare_visual_candidates(
    client: XiaohongshuClient,
    feeds: list[dict[str, Any]],
    output_dir: Path,
    selected_note_ids: list[str],
    images_per_candidate: int,
    detail_interval: float,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    shortlisted = select_visual_feeds(feeds, selected_note_ids)
    for index, feed in enumerate(shortlisted):
        note = client.detail(str(feed["id"]), str(feed["xsecToken"]))
        candidate, image_urls = detail_to_candidate(note, str(feed["id"]))
        candidate_dir = output_dir / "visual-candidates" / candidate["note_id"]
        image_files: list[str] = []
        for image_index, url in enumerate(image_urls[:images_per_candidate], start=1):
            try:
                data = download_image(client.opener, url, client.timeout)
            except (CollectorError, OSError, urllib.error.URLError, TimeoutError) as exc:
                print(f"warning: {candidate['note_id']} 图片 {image_index} 下载失败: {exc}", file=sys.stderr)
                continue
            extension = image_extension(data)
            if extension == ".bin":
                print(f"warning: {candidate['note_id']} 图片 {image_index} 格式未知，已跳过", file=sys.stderr)
                continue
            image_path = candidate_dir / f"{image_index:02d}{extension}"
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(data)
            image_files.append(image_path.relative_to(output_dir).as_posix())
        candidate["image_files"] = image_files
        write_json(candidate_dir / "candidate.json", candidate)
        if image_files:
            candidates.append(candidate)
        if index < len(shortlisted) - 1:
            time.sleep(detail_interval)
    manifest = {
        "schema_version": 1,
        "platform": "xiaohongshu",
        "selection_policy": "explicit note IDs selected after full cover-pool visual review",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    write_json(output_dir / "visual-candidates.json", manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect sanitized Xiaohongshu research evidence")
    parser.add_argument("keyword")
    try:
        configured_limit = int(os.environ.get("DEFAULT_SAMPLE_LIMIT", str(DEFAULT_LIMIT)))
    except ValueError:
        configured_limit = DEFAULT_LIMIT
    parser.add_argument("--limit", type=int, default=configured_limit)
    parser.add_argument("--endpoint")
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cover-pool", type=int, default=0)
    parser.add_argument("--candidate-note-id", action="append", default=[])
    parser.add_argument("--review-selection-file", type=Path)
    parser.add_argument("--selection-wait-seconds", type=float, default=600)
    parser.add_argument("--images-per-candidate", type=int, default=6)
    parser.add_argument("--detail-interval", type=float, default=2)
    return parser


def main() -> int:
    load_repo_env()
    args = build_parser().parse_args()
    if args.limit < 1 or args.limit > MAX_BATCH_SIZE:
        print(f"error: --limit 必须在 1 到 {MAX_BATCH_SIZE} 之间", file=sys.stderr)
        return 2
    if args.cover_pool < 0 or args.cover_pool > args.limit:
        print("error: --cover-pool 必须在 0 到 --limit 之间", file=sys.stderr)
        return 2
    if len(args.candidate_note_id) > MAX_VISUAL_CANDIDATES:
        print(f"error: --candidate-note-id 最多提供 {MAX_VISUAL_CANDIDATES} 个", file=sys.stderr)
        return 2
    if args.review_selection_file and args.candidate_note_id:
        print("error: --review-selection-file 不能和 --candidate-note-id 同时使用", file=sys.stderr)
        return 2
    if args.review_selection_file and not args.cover_pool:
        print("error: --review-selection-file 必须和 --cover-pool 一起使用", file=sys.stderr)
        return 2
    if args.selection_wait_seconds <= 0 or args.selection_wait_seconds > 1800:
        print("error: --selection-wait-seconds 必须在 0 到 1800 秒之间", file=sys.stderr)
        return 2
    if args.images_per_candidate < 1 or args.images_per_candidate > 20:
        print("error: --images-per-candidate 必须在 1 到 20 之间", file=sys.stderr)
        return 2
    endpoint = args.endpoint or os.environ.get("XHS_MCP_ENDPOINT", DEFAULT_ENDPOINT)
    timeout = args.timeout or float(os.environ.get("XHS_MCP_TIMEOUT_SECONDS", "60"))
    print(
        f"首次默认推荐 25 条；数量可以调整，本次请求 {args.limit} 条。",
        file=sys.stderr,
    )
    try:
        client = XiaohongshuClient(endpoint, timeout)
        client.check_ready()
        feeds = client.search(args.keyword, args.limit)
        evidence = build_evidence(args.keyword, feeds, args.limit)
        if evidence["collected"] == 0:
            raise CollectorError("没有获得可用的小红书笔记卡片")
        write_json(args.out, evidence)
        cover_manifest = None
        if args.cover_pool:
            cover_manifest = prepare_cover_pool(client, feeds, args.out.parent, args.cover_pool)
        selected_note_ids = args.candidate_note_id
        if args.review_selection_file:
            selected_note_ids = wait_for_review_selection(
                args.review_selection_file, args.selection_wait_seconds
            )
        candidate_manifest = None
        if selected_note_ids:
            candidate_manifest = prepare_visual_candidates(
                client,
                feeds,
                args.out.parent,
                selected_note_ids,
                args.images_per_candidate,
                args.detail_interval,
            )
    except (CollectorError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "output": str(args.out),
        "collected": evidence["collected"],
        "cover_pool": cover_manifest["cover_count"] if cover_manifest else 0,
        "visual_candidates": candidate_manifest["candidate_count"] if candidate_manifest else 0,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
