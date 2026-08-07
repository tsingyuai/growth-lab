#!/usr/bin/env python3
"""Publish an exact reviewed image note through local xiaohongshu-mcp."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ENDPOINT = "http://127.0.0.1:18063"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


class PublishError(RuntimeError):
    pass


def read_endpoint() -> str:
    value = os.environ.get("XHS_MCP_ENDPOINT", "")
    if not value:
        for filename in (".env", ".env.local"):
            path = ROOT / filename
            if not path.is_file():
                continue
            for raw in path.read_text(encoding="utf-8").splitlines():
                if raw.strip().startswith("XHS_MCP_ENDPOINT="):
                    value = raw.split("=", 1)[1].strip().strip('"').strip("'")
    endpoint = value or DEFAULT_ENDPOINT
    parsed = urlsplit(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or not parsed.port:
        raise PublishError("XHS_MCP_ENDPOINT 必须是包含端口的本机 HTTP 地址。")
    return endpoint.rstrip("/")


def package_file(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise PublishError("小红书发布包包含无效文件路径。")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise PublishError("小红书发布素材必须位于发布包目录内。") from exc
    if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
        raise PublishError(f"小红书图片不存在或格式不支持：{value}")
    return path


def publication_digest(title: str, content: str, assets: list[Path], root: Path, settings: dict[str, Any]) -> str:
    payload = {
        "title": title, "content": content, "settings": settings,
        "assets": [{"path": str(path.relative_to(root)).replace("\\", "/"), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in assets],
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def read_package(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublishError("小红书发布清单不存在或不是有效 JSON。") from exc
    if manifest.get("platform") != "xiaohongshu":
        raise PublishError("发布清单平台必须是 xiaohongshu。")
    publish = manifest.get("publish") or {}
    if publish.get("approved") is not True or publish.get("auto_publish") is not True or not publish.get("confirmed_at"):
        raise PublishError("小红书正式发布必须单独批准并记录确认时间。")
    authorization = manifest.get("content_authorization") or {}
    for key in ("rights_confirmed", "final_content_reviewed", "proxy_action_authorized", "target_account_confirmed", "distribution_settings_reviewed", "responsibility_accepted"):
        if authorization.get(key) is not True:
            raise PublishError(f"小红书正式发布缺少授权：{key}")
    root = path.parent.resolve()
    copy_value = manifest.get("copy_file")
    if not isinstance(copy_value, str):
        raise PublishError("小红书发布包缺少 copy_file。")
    copy_path = (root / copy_value).resolve()
    try:
        copy_path.relative_to(root)
        content = copy_path.read_text(encoding="utf-8").strip()
    except (ValueError, OSError) as exc:
        raise PublishError("无法安全读取小红书文案。") from exc
    native = manifest.get("native_constraints") or {}
    title = str(native.get("title") or "").strip()
    if not title or len(title) > 20:
        raise PublishError("小红书标题必须为 1 到 20 个字符。")
    values = manifest.get("asset_files") or []
    if not isinstance(values, list) or not 1 <= len(values) <= 18:
        raise PublishError("小红书图文发布需要 1 到 18 张图片。")
    assets = [package_file(root, value) for value in values]
    settings = {
        "tags": native.get("tags") or [], "schedule_at": native.get("schedule_at") or "",
        "is_original": bool(native.get("is_original", False)),
        "visibility": native.get("visibility") or "公开可见", "products": native.get("products") or [],
        "target_account": str(native.get("target_account") or "").strip(),
    }
    if not settings["target_account"]:
        raise PublishError("小红书正式发布必须写明 native_constraints.target_account。")
    digest = publication_digest(title, content, assets, root, settings)
    if authorization.get("publication_sha256") != digest:
        raise PublishError("小红书发布内容或设置与 publication_sha256 不一致。")
    return manifest, {"title": title, "content": content, "images": [str(asset) for asset in assets], **settings}


def request_json(endpoint: str, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request = Request(endpoint + path, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=180) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise PublishError(f"xiaohongshu-mcp 返回 HTTP {exc.code}：{detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise PublishError("无法连接本机 xiaohongshu-mcp；未自动重试。") from exc
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PublishError("xiaohongshu-mcp 返回了非 JSON 响应。") from exc
    if result.get("success") is False:
        raise PublishError("xiaohongshu-mcp 报告发布失败；请人工检查，未自动重试。")
    return result


def state_path(manifest_path: Path) -> Path:
    return manifest_path.with_name("xiaohongshu-publish-state.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a reviewed note through local xiaohongshu-mcp")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--confirm-publish", action="store_true")
    args = parser.parse_args()
    path = Path(args.manifest).resolve()
    _, payload = read_package(path)
    endpoint = read_endpoint()
    if args.check:
        print(json.dumps({"status": "package-ready", "endpoint": endpoint, "title": payload["title"], "media_count": len(payload["images"]), "external_action": False}, ensure_ascii=False, indent=2))
        return 0
    if not args.confirm_publish:
        raise PublishError("正式发布到小红书必须提供 --confirm-publish。")
    state_file = state_path(path)
    if state_file.exists() and json.loads(state_file.read_text(encoding="utf-8")).get("status") == "published":
        raise PublishError("该发布包已有成功记录；为避免重复发布，已停止。")
    login = request_json(endpoint, "GET", "/api/v1/login/status")
    data = login.get("data") or {}
    if not data.get("is_logged_in"):
        raise PublishError("xiaohongshu-mcp 尚未登录；发布授权不会自动打开登录。")
    if str(data.get("username") or "").strip() != payload["target_account"]:
        raise PublishError("当前小红书登录账号与发布包 target_account 不一致；未发布。")
    request_payload = {key: value for key, value in payload.items() if key != "target_account"}
    result = request_json(endpoint, "POST", "/api/v1/publish", request_payload)
    state = {"platform": "xiaohongshu", "status": "published", "account": data.get("username", ""), "result": result.get("data") or {}}
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PublishError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
