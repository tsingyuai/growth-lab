#!/usr/bin/env python3
"""微信公众号远程发布服务客户端。

本地只负责把文章目录打包并调用远端固定 IP 服务;微信 AppSecret 留在远端。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from cli import load_state, save_state
from client import load_dotenv


DEFAULT_INCLUDE_NAMES = {
    "article.md",
    "article.html",
    "wechat.yml",
    "cover.png",
    "cover.jpg",
    "cover.jpeg",
    "cover.webp",
}
DEFAULT_INCLUDE_DIRS = {"assets"}
MAX_FILE_BYTES = 8 * 1024 * 1024


class RemoteClientError(RuntimeError):
    """远程发布客户端错误。"""



def collect_files(post_dir: Path) -> list[Path]:
    """收集需要上传到远端的文章文件。"""
    files: list[Path] = []
    for child in sorted(post_dir.iterdir()):
        if child.is_file() and child.name in DEFAULT_INCLUDE_NAMES:
            files.append(child)
        elif child.is_dir() and child.name in DEFAULT_INCLUDE_DIRS:
            files.extend(path for path in sorted(child.rglob("*")) if path.is_file())
    missing = [name for name in ("article.md", "wechat.yml") if not (post_dir / name).exists()]
    if missing:
        raise RemoteClientError(f"缺少必需文件: {', '.join(missing)}")
    if not files:
        raise RemoteClientError("没有可上传文件")
    return files


def encode_file(post_dir: Path, path: Path) -> dict[str, str]:
    """把单个文件编码成上传对象。"""
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise RemoteClientError(f"文件过大: {path} ({size} bytes)")
    rel = path.relative_to(post_dir).as_posix()
    return {
        "path": rel,
        "content_base64": base64.b64encode(path.read_bytes()).decode("ascii"),
    }


def build_upload_payload(post_dir: Path, slug: str) -> dict[str, object]:
    """构建上传 payload。"""
    encoded_files = [encode_file(post_dir, path) for path in collect_files(post_dir)]
    return {"slug": slug, "files": encoded_files}


def build_publish_upload_payload(post_dir: Path, slug: str) -> dict[str, object]:
    """构建发布前审批配置同步 payload。"""
    config_path = post_dir / "wechat.yml"
    if not config_path.exists():
        raise RemoteClientError("缺少 wechat.yml")
    return {"slug": slug, "files": [encode_file(post_dir, config_path)]}


def call_api(base_url: str, token: str, method: str, path: str, payload: dict[str, object] | None) -> dict[str, object]:
    """调用远程发布服务。"""
    url = f"{base_url.rstrip('/')}{path}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "growth-lab-wechat-remote-client/1.0",
    }
    if body is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RemoteClientError(f"远端 HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RemoteClientError(f"远端请求失败: {exc}") from exc
    if not isinstance(data, dict):
        raise RemoteClientError("远端响应不是 JSON object")
    if data.get("ok") is not True:
        raise RemoteClientError(str(data.get("error", data)))
    return data


def resolve_slug(post_dir: Path, explicit: str | None) -> str:
    """解析远端文章 slug。"""
    if explicit:
        return explicit.strip()
    return post_dir.resolve().name


def load_remote_config() -> tuple[str, str]:
    """读取远程服务地址与 token。"""
    load_dotenv()
    base_url = os.environ.get("WECHAT_PUBLISH_SERVICE_URL", "").strip().rstrip("/")
    token = os.environ.get("WECHAT_PUBLISH_SERVICE_TOKEN", "").strip()
    if not base_url or not token:
        raise RemoteClientError("缺少 WECHAT_PUBLISH_SERVICE_URL / WECHAT_PUBLISH_SERVICE_TOKEN")
    return base_url, token


def sync_state(post_dir: Path, response: dict[str, object]) -> None:
    """把远端状态同步到本地 publish-state.json。"""
    state = response.get("state")
    if not isinstance(state, dict):
        return
    updates: dict[str, object] = {
        "remote_slug": response.get("slug", ""),
        "remote_state": state,
        "remote_status": state.get("status", ""),
    }
    for key in ("draft_media_id", "publish_id", "article_id", "article_url"):
        if key in state:
            updates[key] = state[key]
    save_state(post_dir, updates)


def command_draft(args: argparse.Namespace) -> int:
    """上传文章并创建远程草稿。"""
    post_dir = Path(args.post_dir)
    base_url, token = load_remote_config()
    payload = build_upload_payload(post_dir, resolve_slug(post_dir, args.slug))
    response = call_api(base_url, token, "POST", "/v1/wechat/draft", payload)
    sync_state(post_dir, response)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def command_publish(args: argparse.Namespace) -> int:
    """提交远程发布。"""
    post_dir = Path(args.post_dir)
    base_url, token = load_remote_config()
    if args.upload:
        payload = build_publish_upload_payload(post_dir, resolve_slug(post_dir, args.slug))
    else:
        payload = {"slug": resolve_slug(post_dir, args.slug)}
    payload["confirm_publish"] = bool(args.confirm_publish)
    response = call_api(base_url, token, "POST", "/v1/wechat/publish", payload)
    sync_state(post_dir, response)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def command_status(args: argparse.Namespace) -> int:
    """查询远程发布状态。"""
    post_dir = Path(args.post_dir)
    base_url, token = load_remote_config()
    slug = resolve_slug(post_dir, args.slug)
    query = urllib.parse.urlencode({"slug": slug})
    response = call_api(base_url, token, "GET", f"/v1/wechat/status?{query}", None)
    sync_state(post_dir, response)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """构建参数解析器。"""
    parser = argparse.ArgumentParser(description="微信公众号远程发布服务客户端")
    sub = parser.add_subparsers(dest="command", required=True)

    draft = sub.add_parser("draft", help="上传并创建远程草稿")
    draft.add_argument("post_dir")
    draft.add_argument("--slug")
    draft.set_defaults(func=command_draft)

    publish = sub.add_parser("publish", help="提交远程发布")
    publish.add_argument("post_dir")
    publish.add_argument("--slug")
    publish.add_argument("--upload", action="store_true", help="发布前同步本地 wechat.yml 等文件")
    publish.add_argument("--confirm-publish", action="store_true")
    publish.set_defaults(func=command_publish)

    status = sub.add_parser("status", help="查询远程发布状态")
    status.add_argument("post_dir")
    status.add_argument("--slug")
    status.set_defaults(func=command_status)
    return parser


def main() -> int:
    """命令行入口。"""
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except RemoteClientError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
