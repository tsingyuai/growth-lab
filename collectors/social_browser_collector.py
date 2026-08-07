#!/usr/bin/env python3
"""Shared browser-first social collector used by platform Skill wrappers."""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_LIMIT = 25
MAX_BATCH_SIZE = 30
MAX_VISUAL_CANDIDATES = 8
MAX_ASSET_BYTES = 75 * 1024 * 1024
MAX_RESPONSE_BYTES = 10 * 1024 * 1024
RISK_MARKERS = ("captcha", "challenge", "risk", "rate limit", "too many requests", "verify")
ALLOWED_ENGAGEMENT = {"likes", "comments", "shares", "saves", "views", "plays"}


class CollectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class PlatformSpec:
    platform: str
    endpoint_env: str
    default_endpoint: str
    public_hosts: tuple[str, ...]


def load_repo_env(repo: Path, allowed: set[str]) -> None:
    for filename in (".env.local", ".env"):
        path = repo / filename
        if not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key in allowed and key not in os.environ:
                os.environ[key] = value.strip().strip('"').strip("'")


def validate_local_endpoint(endpoint: str) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise CollectorError("平台服务 endpoint 必须是本机 HTTP 地址")
    if not parsed.port:
        raise CollectorError("平台服务 endpoint 必须包含端口")
    return endpoint.rstrip("/")


def validate_public_url(url: str, hosts: tuple[str, ...]) -> str:
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not any(
        hostname == host or hostname.endswith(f".{host}") for host in hosts
    ):
        raise CollectorError(f"adapter 返回了非目标平台公开 URL: {url[:160]}")
    return url


def validate_content_id(value: Any) -> str:
    content_id = str(value or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,200}", content_id):
        raise CollectorError("adapter 返回了不安全的 content_id")
    return content_id


class LocalSocialClient:
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
                response_body = response.read(MAX_RESPONSE_BYTES + 1)
                if len(response_body) > MAX_RESPONSE_BYTES:
                    raise CollectorError("本机平台服务响应超过 10 MiB 限制")
                raw = response_body.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise CollectorError(self.error_message(exc.code, raw)) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise CollectorError(f"无法连接本机平台服务: {exc}") from exc
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CollectorError("本机平台服务返回了非 JSON 响应") from exc
        if not isinstance(envelope, dict) or not envelope.get("success"):
            raise CollectorError(self.error_message(200, raw))
        return envelope.get("data")

    @staticmethod
    def error_message(status: int, raw: str) -> str:
        try:
            payload = json.loads(raw)
            message = str(payload.get("error") or payload.get("message") or raw)
        except json.JSONDecodeError:
            message = raw[:300]
        prefix = (
            "检测到平台验证或风控，已停止且不会重试"
            if any(marker in message.lower() for marker in RISK_MARKERS)
            else f"本机平台服务错误 (HTTP {status})"
        )
        return f"{prefix}: {message}"

    def check_ready(self) -> None:
        self.request("GET", "/health")
        status = self.request("GET", "/api/v1/login/status")
        if not isinstance(status, dict) or not status.get("is_logged_in"):
            raise CollectorError("本机平台服务可用，但目标平台尚未登录")

    def search(self, keyword: str, limit: int) -> list[dict[str, Any]]:
        data = self.request(
            "POST",
            "/api/v1/content/search",
            {"keyword": keyword, "filters": {}, "max_items": limit, "max_scrolls": 0},
        )
        items = data.get("items") if isinstance(data, dict) else None
        if not isinstance(items, list):
            raise CollectorError("搜索响应缺少 data.items 数组")
        return items

    def detail(self, content_id: str, access_ref: str) -> dict[str, Any]:
        data = self.request(
            "POST",
            "/api/v1/content/detail",
            {"content_id": content_id, "access_ref": access_ref, "load_comments": False},
        )
        if not isinstance(data, dict) or not isinstance(data.get("content"), dict):
            raise CollectorError(f"内容 {content_id} 的详情响应缺少 data.content")
        return data


def sanitize_item(item: dict[str, Any], spec: PlatformSpec) -> dict[str, Any] | None:
    try:
        content_id = validate_content_id(item.get("content_id"))
    except CollectorError:
        return None
    public_url = str(item.get("public_url") or "").strip()
    if not content_id or not public_url:
        return None
    try:
        validate_public_url(public_url, spec.public_hosts)
    except CollectorError:
        return None
    engagement = item.get("visible_engagement") or {}
    if not isinstance(engagement, dict):
        engagement = {}
    return {
        "content_id": content_id,
        "public_url": public_url,
        "title": str(item.get("title") or "")[:1000],
        "content_type": str(item.get("content_type") or ""),
        "author": str(item.get("author") or "")[:300],
        "visible_engagement": {
            str(key): str(value)[:100]
            for key, value in engagement.items()
            if str(key) in ALLOWED_ENGAGEMENT
        },
        "has_cover": bool(item.get("cover_url")),
    }


def build_evidence(
    keyword: str, items: list[dict[str, Any]], limit: int, spec: PlatformSpec
) -> dict[str, Any]:
    sanitized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        clean = sanitize_item(item, spec)
        if not clean or clean["content_id"] in seen:
            continue
        seen.add(clean["content_id"])
        sanitized.append(clean)
        if len(sanitized) >= limit:
            break
    return {
        "schema_version": 1,
        "collected_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "platform": spec.platform,
        "query": keyword,
        "access_mode": "authorized read-only browser session via local platform adapter",
        "scope": "search cards and explicitly selected visual candidates; no account actions",
        "privacy": "session credentials, access refs, signed media URLs, avatars, and raw responses omitted",
        "requested": limit,
        "collected": len(sanitized),
        "items": sanitized,
    }


def _asset_url_allowed(url: str, endpoint: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or ""
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if parsed.scheme == "https" and hostname and not (
        address and (address.is_private or address.is_loopback or address.is_link_local)
    ):
        return True
    endpoint_parsed = urllib.parse.urlparse(endpoint)
    return (
        parsed.scheme == "http"
        and parsed.hostname == endpoint_parsed.hostname
        and parsed.port == endpoint_parsed.port
    )


def download_asset(client: LocalSocialClient, url: str) -> bytes:
    if not _asset_url_allowed(url, client.endpoint):
        raise CollectorError("adapter 返回了不安全的媒体 URL")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with client.opener.open(request, timeout=client.timeout) as response:
        if not _asset_url_allowed(response.geturl(), client.endpoint):
            raise CollectorError("媒体下载被重定向到不安全地址")
        data = response.read(MAX_ASSET_BYTES + 1)
    if len(data) > MAX_ASSET_BYTES:
        raise CollectorError("单个媒体文件超过 75 MiB 限制")
    return data


def asset_extension(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if len(data) > 12 and data[4:8] == b"ftyp":
        return ".mp4"
    return None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_contact_sheets(output_dir: Path, items: list[dict[str, Any]]) -> list[str]:
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        return []
    files: list[str] = []
    for page_start in range(0, len(items), 4):
        page_items = items[page_start : page_start + 4]
        sheet = Image.new("RGB", (1080, 1440), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, item in enumerate(page_items):
            column, row = offset % 2, offset // 2
            left, top = column * 540 + 20, row * 720 + 20
            with Image.open(output_dir / item["cover_file"]) as source:
                image = ImageOps.contain(ImageOps.exif_transpose(source).convert("RGB"), (500, 620))
            sheet.paste(image, (left + (500 - image.width) // 2, top + 55 + (620 - image.height) // 2))
            draw.rectangle((left, top, left + 500, top + 45), fill="#111827")
            draw.text((left + 12, top + 12), f"{page_start + offset + 1:02d}  {item['content_id']}", fill="white")
        path = output_dir / "cover-pool" / f"contact-sheet-{page_start // 4 + 1:02d}.jpg"
        sheet.save(path, "JPEG", quality=90, optimize=True)
        files.append(path.relative_to(output_dir).as_posix())
    return files


def prepare_cover_pool(
    client: LocalSocialClient,
    items: list[dict[str, Any]],
    output_dir: Path,
    count: int,
    spec: PlatformSpec,
) -> dict[str, Any]:
    saved: list[dict[str, Any]] = []
    for item in items:
        if len(saved) >= count:
            break
        clean = sanitize_item(item, spec)
        cover_url = str(item.get("cover_url") or "")
        if not clean or not cover_url:
            continue
        try:
            data = download_asset(client, cover_url)
        except (CollectorError, OSError, urllib.error.URLError, TimeoutError):
            continue
        extension = asset_extension(data)
        if extension not in {".png", ".jpg", ".webp"}:
            continue
        path = output_dir / "cover-pool" / f"{len(saved) + 1:02d}-{clean['content_id']}{extension}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        clean["cover_file"] = path.relative_to(output_dir).as_posix()
        saved.append(clean)
    sheets = build_contact_sheets(output_dir, saved)
    manifest = {
        "schema_version": 1,
        "platform": spec.platform,
        "review_status": "pending_visual_review",
        "selection_policy": "review every cover before requesting 3-8 details; engagement is supporting evidence only",
        "cover_count": len(saved),
        "contact_sheets": sheets,
        "items": saved,
    }
    write_json(output_dir / "cover-pool.json", manifest)
    return manifest


def select_items(items: list[dict[str, Any]], selected_ids: list[str]) -> list[dict[str, Any]]:
    by_id = {str(item.get("content_id")): item for item in items if item.get("content_id")}
    missing = [content_id for content_id in selected_ids if content_id not in by_id]
    if missing:
        raise CollectorError(f"视觉候选未出现在本次搜索结果中: {', '.join(missing)}")
    return [by_id[content_id] for content_id in selected_ids]


def wait_for_review_selection(path: Path, wait_seconds: float) -> list[str]:
    deadline = time.monotonic() + wait_seconds
    print(
        json.dumps(
            {
                "status": "waiting-for-cover-review",
                "selection_file": str(path),
                "selection_format": {"content_ids": ["public-content-id"]},
                "empty_selection_allowed": True,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    while not path.is_file():
        if time.monotonic() >= deadline:
            raise CollectorError(f"等待封面审查超时（{wait_seconds:g} 秒），未请求任何详情")
        time.sleep(0.5)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CollectorError("封面审查文件不是有效 JSON") from exc
    content_ids = payload.get("content_ids") if isinstance(payload, dict) else None
    if not isinstance(content_ids, list) or any(not isinstance(item, str) for item in content_ids):
        raise CollectorError("封面审查文件必须包含 content_ids 字符串数组")
    normalized = [validate_content_id(item) for item in content_ids if item.strip()]
    if len(normalized) != len(set(normalized)):
        raise CollectorError("封面审查文件包含重复 content ID")
    if len(normalized) > MAX_VISUAL_CANDIDATES:
        raise CollectorError(f"视觉候选最多选择 {MAX_VISUAL_CANDIDATES} 条")
    return normalized


def prepare_visual_candidates(
    client: LocalSocialClient,
    items: list[dict[str, Any]],
    output_dir: Path,
    selected_ids: list[str],
    assets_per_candidate: int,
    detail_interval: float,
    spec: PlatformSpec,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for index, item in enumerate(select_items(items, selected_ids)):
        content_id = str(item["content_id"])
        detail = client.detail(content_id, str(item.get("access_ref") or ""))
        content = dict(detail["content"])
        content.setdefault("content_id", content_id)
        content.setdefault("public_url", item.get("public_url"))
        clean = sanitize_item(content, spec)
        if not clean:
            raise CollectorError(f"内容 {content_id} 的详情缺少公开 ID 或 URL")
        clean["description"] = str(content.get("description") or "")
        asset_files: list[str] = []
        for asset_index, asset in enumerate(detail.get("media") or [], start=1):
            if asset_index > assets_per_candidate or not isinstance(asset, dict):
                break
            url = str(asset.get("url") or "")
            if not url:
                continue
            try:
                data = download_asset(client, url)
            except (CollectorError, OSError, urllib.error.URLError, TimeoutError):
                continue
            extension = asset_extension(data)
            if extension is None:
                continue
            path = output_dir / "visual-candidates" / content_id / f"{asset_index:02d}{extension}"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            asset_files.append(path.relative_to(output_dir).as_posix())
        clean["asset_files"] = asset_files
        write_json(output_dir / "visual-candidates" / content_id / "candidate.json", clean)
        if asset_files:
            candidates.append(clean)
        if index < len(selected_ids) - 1:
            time.sleep(detail_interval)
    manifest = {
        "schema_version": 1,
        "platform": spec.platform,
        "selection_policy": "explicit content IDs selected after full cover-pool review",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    write_json(output_dir / "visual-candidates.json", manifest)
    return manifest


def build_parser(spec: PlatformSpec) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Collect sanitized {spec.platform} evidence")
    parser.add_argument("keyword")
    parser.add_argument("--limit", type=int, default=int(os.environ.get("DEFAULT_SAMPLE_LIMIT", "25")))
    parser.add_argument("--endpoint")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cover-pool", type=int, default=0)
    parser.add_argument("--candidate-content-id", action="append", default=[])
    parser.add_argument("--review-selection-file", type=Path)
    parser.add_argument("--selection-wait-seconds", type=float, default=600)
    parser.add_argument("--assets-per-candidate", type=int, default=6)
    parser.add_argument("--detail-interval", type=float, default=2)
    return parser


def main_for(spec: PlatformSpec, repo: Path) -> int:
    load_repo_env(repo, {spec.endpoint_env, "DEFAULT_SAMPLE_LIMIT"})
    args = build_parser(spec).parse_args()
    if args.limit < 1 or args.limit > MAX_BATCH_SIZE:
        print(f"error: --limit 必须在 1 到 {MAX_BATCH_SIZE} 之间", file=os.sys.stderr)
        return 2
    if args.cover_pool < 0 or args.cover_pool > args.limit:
        print("error: --cover-pool 必须在 0 到 --limit 之间", file=os.sys.stderr)
        return 2
    if len(args.candidate_content_id) > MAX_VISUAL_CANDIDATES:
        print(f"error: --candidate-content-id 最多提供 {MAX_VISUAL_CANDIDATES} 个", file=os.sys.stderr)
        return 2
    if args.review_selection_file and args.candidate_content_id:
        print("error: --review-selection-file 不能和 --candidate-content-id 同时使用", file=os.sys.stderr)
        return 2
    if args.review_selection_file and not args.cover_pool:
        print("error: --review-selection-file 必须和 --cover-pool 一起使用", file=os.sys.stderr)
        return 2
    if args.selection_wait_seconds <= 0 or args.selection_wait_seconds > 1800:
        print("error: --selection-wait-seconds 必须在 0 到 1800 秒之间", file=os.sys.stderr)
        return 2
    if args.assets_per_candidate < 1 or args.assets_per_candidate > 20:
        print("error: --assets-per-candidate 必须在 1 到 20 之间", file=os.sys.stderr)
        return 2
    endpoint = args.endpoint or os.environ.get(spec.endpoint_env, spec.default_endpoint)
    print(f"首次默认推荐 25 条；数量可以调整，本次请求 {args.limit} 条。", file=os.sys.stderr)
    try:
        client = LocalSocialClient(endpoint, args.timeout)
        client.check_ready()
        items = client.search(args.keyword, args.limit)
        evidence = build_evidence(args.keyword, items, args.limit, spec)
        if evidence["collected"] == 0:
            raise CollectorError(f"没有获得可用的 {spec.platform} 内容卡片")
        write_json(args.out, evidence)
        cover_manifest = (
            prepare_cover_pool(client, items, args.out.parent, args.cover_pool, spec)
            if args.cover_pool
            else None
        )
        selected_ids = args.candidate_content_id
        if args.review_selection_file:
            selected_ids = wait_for_review_selection(
                args.review_selection_file, args.selection_wait_seconds
            )
        candidate_manifest = (
            prepare_visual_candidates(
                client,
                items,
                args.out.parent,
                selected_ids,
                args.assets_per_candidate,
                args.detail_interval,
                spec,
            )
            if selected_ids
            else None
        )
    except (CollectorError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=os.sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "output": str(args.out),
                "collected": evidence["collected"],
                "cover_pool": cover_manifest["cover_count"] if cover_manifest else 0,
                "visual_candidates": candidate_manifest["candidate_count"] if candidate_manifest else 0,
            },
            ensure_ascii=False,
        )
    )
    return 0
