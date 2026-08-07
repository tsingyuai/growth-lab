#!/usr/bin/env python3
"""Publish an exact reviewed X package through the official X API."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import sys
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import uuid


ROOT = Path(__file__).resolve().parents[3]
API_BASE = "https://api.x.com"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


class PublishError(RuntimeError):
    pass


def read_local_env(root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for filename in (".env", ".env.local"):
        path = root / filename
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "X_USER_ACCESS_TOKEN":
                values[key.strip()] = value.strip().strip('"').strip("'")
    if os.environ.get("X_USER_ACCESS_TOKEN"):
        values["X_USER_ACCESS_TOKEN"] = os.environ["X_USER_ACCESS_TOKEN"]
    return values


def read_copy(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    if lines and lines[0].startswith("# X 文案"):
        text = "\n".join(lines[1:]).strip()
    return text


def resolve_package_file(root: Path, value: Any, suffixes: set[str] | None = None) -> Path:
    if not isinstance(value, str) or not value:
        raise PublishError("发布包文件路径缺失。")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise PublishError("发布包文件必须位于发布包目录内。") from exc
    if not path.is_file() or (suffixes and path.suffix.lower() not in suffixes):
        raise PublishError(f"发布包文件不存在或格式不支持：{value}")
    return path


def publication_digest(text: str, assets: list[Path], root: Path, target_account: str) -> str:
    payload = {
        "text": text,
        "target_account": target_account,
        "assets": [
            {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in assets
        ],
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def read_package(manifest_path: Path) -> tuple[dict[str, Any], str, list[Path]]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublishError("发布清单不存在或不是有效 JSON。") from exc
    if manifest.get("platform") != "x":
        raise PublishError("发布清单平台必须是 x。")
    publish = manifest.get("publish") or {}
    if publish.get("approved") is not True or publish.get("auto_publish") is not True:
        raise PublishError("X 正式发布要求 publish.approved 和 auto_publish 均为 true。")
    if not str(publish.get("confirmed_at") or "").strip():
        raise PublishError("X 正式发布缺少本次确认时间。")
    authorization = manifest.get("content_authorization") or {}
    for key in (
        "rights_confirmed", "final_content_reviewed", "proxy_action_authorized",
        "target_account_confirmed", "distribution_settings_reviewed", "responsibility_accepted",
    ):
        if authorization.get(key) is not True:
            raise PublishError(f"X 正式发布缺少授权：{key}")
    root = manifest_path.parent.resolve()
    copy_path = resolve_package_file(root, manifest.get("copy_file"))
    text = read_copy(copy_path)
    if not text or len(text) > 280:
        raise PublishError("X 文案必须为 1 到 280 个字符。")
    values = manifest.get("asset_files") or []
    if not isinstance(values, list) or len(values) > 4:
        raise PublishError("X 正式发布最多支持 4 张图片。")
    assets = [resolve_package_file(root, value, IMAGE_SUFFIXES) for value in values]
    target_account = str(
        (manifest.get("native_constraints") or {}).get("target_account") or ""
    ).strip().lstrip("@").lower()
    if not target_account:
        raise PublishError("X 正式发布必须写明 native_constraints.target_account。")
    digest = publication_digest(text, assets, root, target_account)
    if authorization.get("publication_sha256") != digest:
        raise PublishError("X 发布内容与 publication_sha256 不一致；必须重新预览并确认。")
    return manifest, text, assets


class XApiClient:
    def __init__(self, token: str):
        if not token:
            raise PublishError("未配置 X_USER_ACCESS_TOKEN。")
        self.token = token

    def request(self, method: str, path: str, body: bytes | None = None, content_type: str = "application/json") -> dict[str, Any]:
        request = Request(
            API_BASE + path,
            data=body,
            method=method,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": content_type},
        )
        try:
            with urlopen(request, timeout=60) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise PublishError(f"X 官方 API 返回 HTTP {exc.code}：{detail}") from exc
        except (URLError, TimeoutError) as exc:
            raise PublishError("无法连接 X 官方 API；未自动重试。") from exc
        try:
            return json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise PublishError("X 官方 API 返回了非 JSON 响应。") from exc

    def upload_image(self, path: Path) -> str:
        boundary = "----growthlab-" + uuid.uuid4().hex
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        parts = [
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"media_category\"\r\n\r\ntweet_image\r\n".encode(),
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"media\"; filename=\"{path.name}\"\r\nContent-Type: {content_type}\r\n\r\n".encode(),
            path.read_bytes(),
            f"\r\n--{boundary}--\r\n".encode(),
        ]
        payload = self.request(
            "POST", "/2/media/upload", b"".join(parts), f"multipart/form-data; boundary={boundary}"
        )
        media_id = str((payload.get("data") or {}).get("id") or payload.get("media_id_string") or "")
        if not media_id:
            raise PublishError("X 图片上传成功响应中缺少 media ID。")
        return media_id

    def create_post(self, text: str, media_ids: list[str]) -> dict[str, Any]:
        payload: dict[str, Any] = {"text": text}
        if media_ids:
            payload["media"] = {"media_ids": media_ids}
        return self.request("POST", "/2/tweets", json.dumps(payload).encode())

    def me(self) -> dict[str, Any]:
        return self.request("GET", "/2/users/me")

    def delete_post(self, post_id: str) -> dict[str, Any]:
        if not post_id.isdigit():
            raise PublishError("本地状态中的 X post ID 无效。")
        return self.request("DELETE", f"/2/tweets/{post_id}")


def state_path(manifest_path: Path) -> Path:
    return manifest_path.with_name("x-publish-state.json")


def publish(manifest_path: Path, client: XApiClient) -> dict[str, Any]:
    manifest, text, assets = read_package(manifest_path)
    state_file = state_path(manifest_path)
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        if state.get("post_id") and state.get("status") == "published":
            raise PublishError("该发布包已有成功记录；为避免重复发帖，已停止。")
    expected = str(
        (manifest.get("native_constraints") or {}).get("target_account") or ""
    ).strip().lstrip("@").lower()
    identity = client.me().get("data") or {}
    actual_values = {
        str(identity.get("id") or "").lower(),
        str(identity.get("username") or "").lower(),
    }
    if expected not in actual_values:
        raise PublishError("X API token 对应账号与发布包 target_account 不一致；未上传或发布。")
    media_ids = [client.upload_image(path) for path in assets]
    response = client.create_post(text, media_ids)
    post_id = str((response.get("data") or {}).get("id") or "")
    if not post_id:
        raise PublishError("X 发帖响应缺少 post ID；请人工检查账号，不要直接重试。")
    state = {
        "platform": "x", "status": "published", "post_id": post_id,
        "url": f"https://x.com/i/web/status/{post_id}", "media_count": len(assets),
        "target_account": expected,
    }
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def delete(manifest_path: Path, client: XApiClient) -> dict[str, Any]:
    state_file = state_path(manifest_path)
    if not state_file.is_file():
        raise PublishError("没有找到该发布包的 X 发布状态，不能自动删除。")
    state = json.loads(state_file.read_text(encoding="utf-8"))
    post_id = str(state.get("post_id") or "")
    response = client.delete_post(post_id)
    deleted = bool((response.get("data") or {}).get("deleted"))
    if not deleted:
        raise PublishError("X 未确认帖子已删除；请人工检查，未自动重试。")
    state["status"] = "deleted"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish reviewed content with the official X API")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--confirm-publish", action="store_true")
    parser.add_argument("--delete-post", action="store_true")
    parser.add_argument("--confirm-delete-post", action="store_true")
    args = parser.parse_args()
    manifest_path = Path(args.manifest).resolve()
    _, text, assets = read_package(manifest_path)
    configured = bool(read_local_env(ROOT).get("X_USER_ACCESS_TOKEN"))
    if args.check:
        print(json.dumps({"status": "ready" if configured else "configuration-required", "characters": len(text), "media_count": len(assets), "credential_displayed": False}, ensure_ascii=False, indent=2))
        return 0 if configured else 2
    client = XApiClient(read_local_env(ROOT).get("X_USER_ACCESS_TOKEN", ""))
    if args.delete_post:
        if not args.confirm_delete_post:
            raise PublishError("删除已发布 X 帖子必须提供 --confirm-delete-post。")
        result = delete(manifest_path, client)
    else:
        if not args.confirm_publish:
            raise PublishError("正式发布到 X 必须提供 --confirm-publish。")
        result = publish(manifest_path, client)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PublishError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
