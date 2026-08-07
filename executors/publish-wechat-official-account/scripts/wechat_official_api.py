#!/usr/bin/env python3
"""Thin, approval-gated WeChat Official Account API client."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import uuid


ROOT = Path(__file__).resolve().parents[3]
API_BASE = "https://api.weixin.qq.com"


class WeChatError(RuntimeError):
    pass


def read_credentials(root: Path) -> tuple[str, str]:
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
            if key.strip() in {"WECHAT_APP_ID", "WECHAT_APP_SECRET"}:
                values[key.strip()] = value.strip().strip('"').strip("'")
    for key in ("WECHAT_APP_ID", "WECHAT_APP_SECRET"):
        if os.environ.get(key):
            values[key] = os.environ[key]
    return values.get("WECHAT_APP_ID", ""), values.get("WECHAT_APP_SECRET", "")


def request_json(request: Request, timeout: int = 60) -> dict[str, Any]:
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise WeChatError(f"微信官方 API 返回 HTTP {exc.code}：{detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise WeChatError("无法连接微信官方 API；未自动重试。") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise WeChatError("微信官方 API 返回了非 JSON 响应。") from exc
    if payload.get("errcode") not in (None, 0):
        raise WeChatError(
            f"微信官方 API 错误 {payload.get('errcode')}：{payload.get('errmsg', '')}"
        )
    return payload


class WeChatClient:
    def __init__(self, app_id: str, app_secret: str):
        if not app_id or not app_secret:
            raise WeChatError("未配置 WECHAT_APP_ID 和 WECHAT_APP_SECRET。")
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token = ""

    def token(self) -> str:
        if self._access_token:
            return self._access_token
        query = urlencode({"grant_type": "client_credential", "appid": self.app_id, "secret": self.app_secret})
        payload = request_json(Request(f"{API_BASE}/cgi-bin/token?{query}"))
        token = str(payload.get("access_token") or "")
        if not token:
            raise WeChatError("微信 token 响应缺少 access_token。")
        self._access_token = token
        return token

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        query = urlencode({"access_token": self.token()})
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return request_json(Request(f"{API_BASE}{path}?{query}", data=body, method="POST", headers={"Content-Type": "application/json"}))

    def upload_thumb(self, path: Path) -> dict[str, Any]:
        boundary = "----growthlab-" + uuid.uuid4().hex
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = b"".join([
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"media\"; filename=\"{path.name}\"\r\nContent-Type: {content_type}\r\n\r\n".encode(),
            path.read_bytes(), f"\r\n--{boundary}--\r\n".encode(),
        ])
        query = urlencode({"access_token": self.token(), "type": "thumb"})
        request = Request(
            f"{API_BASE}/cgi-bin/material/add_material?{query}", data=body, method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        return request_json(request, timeout=120)

    def add_draft(self, article: dict[str, Any]) -> dict[str, Any]:
        return self.post("/cgi-bin/draft/add", {"articles": [article]})

    def submit_publish(self, media_id: str) -> dict[str, Any]:
        return self.post("/cgi-bin/freepublish/submit", {"media_id": media_id})

    def publish_status(self, publish_id: str) -> dict[str, Any]:
        return self.post("/cgi-bin/freepublish/get", {"publish_id": publish_id})


def article_digest(article: dict[str, Any]) -> str:
    canonical = json.dumps(article, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def package_digest(article: dict[str, Any], target_app_id: str) -> str:
    canonical = json.dumps(
        {"article": article, "target_app_id": target_app_id},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def read_package(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WeChatError("微信发布清单不存在或不是有效 JSON。") from exc
    if manifest.get("platform") != "wechat":
        raise WeChatError("发布清单平台必须是 wechat。")
    root = path.parent.resolve()
    copy_value = manifest.get("copy_file")
    if not isinstance(copy_value, str) or not copy_value:
        raise WeChatError("微信发布包缺少 copy_file。")
    copy_path = (root / copy_value).resolve()
    try:
        copy_path.relative_to(root)
    except ValueError as exc:
        raise WeChatError("微信正文必须位于发布包目录内。") from exc
    if copy_path.suffix.lower() not in {".html", ".htm"} or not copy_path.is_file():
        raise WeChatError("微信官方草稿正文必须是发布包内已审核的 HTML 文件。")
    content = copy_path.read_text(encoding="utf-8").strip()
    native = manifest.get("native_constraints") or {}
    article = {
        "title": str(native.get("title") or "").strip(),
        "author": str(native.get("author") or "").strip(),
        "digest": str(native.get("digest") or "").strip(),
        "content": content,
        "content_source_url": str(native.get("content_source_url") or "").strip(),
        "thumb_media_id": str(native.get("thumb_media_id") or "").strip(),
        "need_open_comment": int(bool(native.get("need_open_comment", False))),
        "only_fans_can_comment": int(bool(native.get("only_fans_can_comment", False))),
    }
    if not article["title"] or not article["content"] or not article["thumb_media_id"]:
        raise WeChatError("微信草稿需要 title、HTML content 和 thumb_media_id。")
    target_app_id = str(native.get("target_app_id") or "").strip()
    if not target_app_id:
        raise WeChatError("微信发布包必须写明 native_constraints.target_app_id。")
    authorization = manifest.get("content_authorization") or {}
    for key in ("rights_confirmed", "final_content_reviewed", "target_account_confirmed", "responsibility_accepted"):
        if authorization.get(key) is not True:
            raise WeChatError(f"微信草稿缺少授权：{key}")
    if authorization.get("draft_sha256") != package_digest(article, target_app_id):
        raise WeChatError("微信草稿内容与 draft_sha256 不一致；必须重新预览并确认。")
    return manifest, article


def state_path(manifest_path: Path) -> Path:
    return manifest_path.with_name("wechat-publish-state.json")


def load_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="WeChat Official Account API Client")
    parser.add_argument("--manifest")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--upload-thumb")
    parser.add_argument("--confirm-upload", action="store_true")
    parser.add_argument("--create-draft", action="store_true")
    parser.add_argument("--confirm-create-draft", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--confirm-publish", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    app_id, secret = read_credentials(ROOT)
    if args.check:
        print(json.dumps({"status": "configured-not-verified" if app_id and secret else "configuration-required", "credential_displayed": False}, ensure_ascii=False, indent=2))
        return 0 if app_id and secret else 2
    client = WeChatClient(app_id, secret)
    if args.upload_thumb:
        if not args.confirm_upload:
            raise WeChatError("上传微信缩略图必须提供 --confirm-upload。")
        thumb = Path(args.upload_thumb).resolve()
        if not thumb.is_file() or thumb.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            raise WeChatError("微信缩略图必须是存在的 JPG 或 PNG 文件。")
        result = client.upload_thumb(thumb)
        print(json.dumps({"status": "uploaded", "media_id": result.get("media_id", ""), "url": result.get("url", "")}, ensure_ascii=False, indent=2))
        return 0
    if not args.manifest:
        raise WeChatError("草稿、发布和状态查询必须提供 --manifest。")
    manifest_path = Path(args.manifest).resolve()
    manifest, article = read_package(manifest_path)
    expected_app_id = str(
        (manifest.get("native_constraints") or {}).get("target_app_id") or ""
    ).strip()
    if expected_app_id != app_id:
        raise WeChatError("配置的 WECHAT_APP_ID 与发布包 target_app_id 不一致。")
    state_file = state_path(manifest_path)
    state = load_state(state_file)
    if args.create_draft:
        if not args.confirm_create_draft or (manifest.get("draft_staging") or {}).get("approved") is not True:
            raise WeChatError("创建微信草稿需要发布包批准和 --confirm-create-draft。")
        if state.get("draft_media_id"):
            raise WeChatError("该发布包已有 draft media ID；为避免重复草稿，已停止。")
        result = client.add_draft(article)
        media_id = str(result.get("media_id") or "")
        if not media_id:
            raise WeChatError("微信创建草稿响应缺少 media_id。")
        state = {"platform": "wechat", "status": "draft-created", "draft_media_id": media_id}
        save_state(state_file, state)
    elif args.publish:
        publish = manifest.get("publish") or {}
        authorization = manifest.get("content_authorization") or {}
        if not args.confirm_publish or publish.get("approved") is not True or publish.get("auto_publish") is not True or not publish.get("confirmed_at"):
            raise WeChatError("微信正式发布需要单独批准、确认时间和 --confirm-publish。")
        if authorization.get("publication_sha256") != package_digest(article, expected_app_id):
            raise WeChatError("微信正式发布哈希不匹配；必须重新确认。")
        if not state.get("draft_media_id"):
            raise WeChatError("尚无已登记的微信草稿 media ID，不能提交发布。")
        if state.get("publish_id"):
            raise WeChatError("该草稿已有 publish ID；请查询状态，不要重复提交。")
        result = client.submit_publish(str(state["draft_media_id"]))
        publish_id = str(result.get("publish_id") or "")
        if not publish_id:
            raise WeChatError("微信提交发布响应缺少 publish_id。")
        state.update({"status": "publish-submitted", "publish_id": publish_id})
        save_state(state_file, state)
    elif args.status:
        if not state.get("publish_id"):
            raise WeChatError("本地状态没有 publish_id。")
        result = client.publish_status(str(state["publish_id"]))
        state.update({"status": "status-checked", "publish_status": result.get("publish_status"), "article_id": result.get("article_id", ""), "article_detail": result.get("article_detail") or {}})
        save_state(state_file, state)
    else:
        raise WeChatError("请选择 --check、--upload-thumb、--create-draft、--publish 或 --status。")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WeChatError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
