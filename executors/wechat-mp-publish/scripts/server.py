#!/usr/bin/env python3
"""微信公众号远程发布服务。

服务部署在固定公网 IP 的服务器上,只在服务器环境变量里保存微信密钥。
本地内容工作流把文章目录打包上传后,由服务端完成合规检查、素材上传、
草稿创建和受控发布。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Callable, cast
from urllib.parse import parse_qs, urlparse

from client import WechatAPIError, WechatConfigError, load_dotenv
from cli import command_draft, command_publish, command_status, load_state, save_state


REPO = Path(__file__).resolve().parents[3]
LINT_SCRIPT = REPO / "executors/wechat-article-compose/scripts/check-wechat-compliance.py"
DEFAULT_WORKDIR = Path("/data/wechat-posts")
MAX_BODY_BYTES = int(os.environ.get("WECHAT_PUBLISH_MAX_BODY_BYTES", str(25 * 1024 * 1024)))
TOKEN_ENV = "WECHAT_PUBLISH_SERVICE_TOKEN"
PUBLIC_ENDPOINTS = {("GET", "/healthz")}


class ServiceError(RuntimeError):
    """可返回给调用方的服务错误。"""

    def __init__(self, status: HTTPStatus, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


@dataclass
class ServerConfig:
    host: str
    port: int
    workdir: Path
    token: str


def load_server_config() -> ServerConfig:
    """读取服务配置。"""
    load_dotenv()
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise ServiceError(HTTPStatus.INTERNAL_SERVER_ERROR, f"缺少 {TOKEN_ENV}")
    return ServerConfig(
        host=os.environ.get("WECHAT_PUBLISH_HOST", "0.0.0.0"),
        port=int(os.environ.get("WECHAT_PUBLISH_PORT", "8080")),
        workdir=Path(os.environ.get("WECHAT_PUBLISH_WORKDIR", str(DEFAULT_WORKDIR))).expanduser(),
        token=token,
    )


def json_response(handler: BaseHTTPRequestHandler, status: HTTPStatus, payload: dict[str, object]) -> None:
    """写 JSON 响应。"""
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def slug_to_dirname(slug: str) -> str:
    """把调用方 slug 收敛成安全目录名。"""
    cleaned = slug.strip().replace("\\", "/").rstrip("/")
    if not cleaned:
        raise ServiceError(HTTPStatus.BAD_REQUEST, "slug 不能为空")
    cleaned = cleaned.split("/")[-1]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,120}", cleaned):
        raise ServiceError(HTTPStatus.BAD_REQUEST, "slug 只能包含字母、数字、点、下划线和短横线")
    return cleaned


def safe_relative_path(path: str) -> Path:
    """校验上传文件路径,禁止写出文章目录。"""
    pure = PurePosixPath(path.strip())
    if pure.is_absolute() or ".." in pure.parts:
        raise ServiceError(HTTPStatus.BAD_REQUEST, f"非法文件路径: {path}")
    if not pure.parts:
        raise ServiceError(HTTPStatus.BAD_REQUEST, "文件路径不能为空")
    return Path(*pure.parts)


def decode_payload(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    """读取并解析请求 JSON。"""
    raw_length = handler.headers.get("Content-Length", "0")
    try:
        length = int(raw_length)
    except ValueError as exc:
        raise ServiceError(HTTPStatus.BAD_REQUEST, "Content-Length 不合法") from exc
    if length <= 0:
        raise ServiceError(HTTPStatus.BAD_REQUEST, "请求体不能为空")
    if length > MAX_BODY_BYTES:
        raise ServiceError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "请求体超过大小限制")
    try:
        payload = json.loads(handler.rfile.read(length).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ServiceError(HTTPStatus.BAD_REQUEST, "请求体不是合法 JSON") from exc
    if not isinstance(payload, dict):
        raise ServiceError(HTTPStatus.BAD_REQUEST, "请求体必须是 JSON object")
    return payload


def require_auth(handler: BaseHTTPRequestHandler, config: ServerConfig) -> None:
    """校验内部调用 token。"""
    expected = f"Bearer {config.token}"
    actual = handler.headers.get("Authorization", "")
    if actual != expected:
        raise ServiceError(HTTPStatus.UNAUTHORIZED, "Authorization token 不正确")


def write_uploaded_files(config: ServerConfig, payload: dict[str, object]) -> Path:
    """把上传文件写入远端工作目录。"""
    slug = slug_to_dirname(str(payload.get("slug", "")))
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise ServiceError(HTTPStatus.BAD_REQUEST, "files 必须是非空数组")

    post_dir = config.workdir / slug
    existing_state = post_dir / "publish-state.json"
    staging_dir = config.workdir / f".staging-{slug}-{int(time.time())}"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    try:
        for item in files:
            if not isinstance(item, dict):
                raise ServiceError(HTTPStatus.BAD_REQUEST, "files 数组元素必须是 object")
            rel = safe_relative_path(str(item.get("path", "")))
            content_b64 = item.get("content_base64")
            if not isinstance(content_b64, str):
                raise ServiceError(HTTPStatus.BAD_REQUEST, f"{rel} 缺少 content_base64")
            try:
                content = base64.b64decode(content_b64, validate=True)
            except ValueError as exc:
                raise ServiceError(HTTPStatus.BAD_REQUEST, f"{rel} 不是合法 base64") from exc
            target = staging_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        if not (staging_dir / "article.md").exists() or not (staging_dir / "wechat.yml").exists():
            raise ServiceError(HTTPStatus.BAD_REQUEST, "上传包必须包含 article.md 和 wechat.yml")
        if existing_state.exists() and not (staging_dir / "publish-state.json").exists():
            shutil.copy2(existing_state, staging_dir / "publish-state.json")
        if post_dir.exists():
            shutil.rmtree(post_dir)
        staging_dir.rename(post_dir)
    except Exception:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        raise
    return post_dir


def merge_uploaded_files(config: ServerConfig, payload: dict[str, object]) -> Path:
    """把少量配置文件合并进已有远端文章目录。"""
    slug = slug_to_dirname(str(payload.get("slug", "")))
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise ServiceError(HTTPStatus.BAD_REQUEST, "files 必须是非空数组")
    post_dir = config.workdir / slug
    if not post_dir.exists():
        raise ServiceError(HTTPStatus.NOT_FOUND, "远端文章不存在,请先创建草稿")

    for item in files:
        if not isinstance(item, dict):
            raise ServiceError(HTTPStatus.BAD_REQUEST, "files 数组元素必须是 object")
        rel = safe_relative_path(str(item.get("path", "")))
        if rel.as_posix() != "wechat.yml":
            raise ServiceError(HTTPStatus.BAD_REQUEST, "发布前只允许同步 wechat.yml 审批配置")
        content_b64 = item.get("content_base64")
        if not isinstance(content_b64, str):
            raise ServiceError(HTTPStatus.BAD_REQUEST, f"{rel} 缺少 content_base64")
        try:
            content = base64.b64decode(content_b64, validate=True)
        except ValueError as exc:
            raise ServiceError(HTTPStatus.BAD_REQUEST, f"{rel} 不是合法 base64") from exc
        (post_dir / rel).write_bytes(content)
    return post_dir


def run_lint(post_dir: Path) -> None:
    """运行微信公众号合规检查。"""
    result = subprocess.run(
        [sys.executable, str(LINT_SCRIPT), str(post_dir)],
        cwd=str(REPO),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise ServiceError(HTTPStatus.UNPROCESSABLE_ENTITY, f"合规检查未通过:\n{detail}")


def make_args(post_dir: Path, confirm_publish: bool = False) -> argparse.Namespace:
    """构造复用 CLI command_* 所需的参数对象。"""
    return argparse.Namespace(post_dir=str(post_dir), confirm_publish=confirm_publish)


def redact_state(state: dict[str, object]) -> dict[str, object]:
    """返回可给本地看的状态,不暴露内部路径和 token。"""
    allowed = {
        "status",
        "draft_media_id",
        "publish_id",
        "article_id",
        "article_url",
        "account",
        "image_mapping",
        "publish_status_response",
        "updated_at",
    }
    return {key: value for key, value in state.items() if key in allowed}


class WechatPublishHandler(BaseHTTPRequestHandler):
    """HTTP 路由处理器。"""

    server_version = "growth-lab-wechat-publisher/1.0"

    def do_GET(self) -> None:
        self.dispatch("GET")

    def do_POST(self) -> None:
        self.dispatch("POST")

    def log_message(self, fmt: str, *args: object) -> None:
        """输出访问日志到 stdout。"""
        print(f"{self.address_string()} - {fmt % args}", flush=True)

    @property
    def config(self) -> ServerConfig:
        return cast(ConfiguredServer, self.server).config

    def dispatch(self, method: str) -> None:
        parsed = urlparse(self.path)
        route = parsed.path.rstrip("/") or "/"
        try:
            if (method, route) not in PUBLIC_ENDPOINTS:
                require_auth(self, self.config)
            routes: dict[tuple[str, str], Callable[[dict[str, list[str]]], dict[str, object]]] = {
                ("GET", "/healthz"): self.handle_health,
                ("POST", "/v1/wechat/draft"): self.handle_draft,
                ("POST", "/v1/wechat/publish"): self.handle_publish,
                ("GET", "/v1/wechat/status"): self.handle_status,
            }
            handler = routes.get((method, route))
            if handler is None:
                raise ServiceError(HTTPStatus.NOT_FOUND, "接口不存在")
            payload = handler(parse_qs(parsed.query))
            json_response(self, HTTPStatus.OK, {"ok": True, **payload})
        except ServiceError as exc:
            json_response(self, exc.status, {"ok": False, "error": exc.message})
        except (FileNotFoundError, PermissionError, ValueError, WechatConfigError, WechatAPIError) as exc:
            json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
        except Exception as exc:
            json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(exc)})

    def handle_health(self, _: dict[str, list[str]]) -> dict[str, object]:
        return {"status": "ok"}

    def handle_draft(self, _: dict[str, list[str]]) -> dict[str, object]:
        payload = decode_payload(self)
        post_dir = write_uploaded_files(self.config, payload)
        run_lint(post_dir)
        command_draft(make_args(post_dir))
        state = redact_state(load_state(post_dir))
        return {"slug": post_dir.name, "state": state}

    def handle_publish(self, _: dict[str, list[str]]) -> dict[str, object]:
        payload = decode_payload(self)
        slug = slug_to_dirname(str(payload.get("slug", "")))
        confirm = payload.get("confirm_publish") is True
        if isinstance(payload.get("files"), list):
            post_dir = merge_uploaded_files(self.config, payload)
        else:
            post_dir = self.config.workdir / slug
        if not post_dir.exists():
            raise ServiceError(HTTPStatus.NOT_FOUND, "远端文章不存在,请先创建草稿")
        run_lint(post_dir)
        command_publish(make_args(post_dir, confirm_publish=confirm))
        state = redact_state(load_state(post_dir))
        return {"slug": slug, "state": state}

    def handle_status(self, query: dict[str, list[str]]) -> dict[str, object]:
        slug_values = query.get("slug", [])
        slug = slug_to_dirname(slug_values[0] if slug_values else "")
        post_dir = self.config.workdir / slug
        if not post_dir.exists():
            raise ServiceError(HTTPStatus.NOT_FOUND, "远端文章不存在")
        state = load_state(post_dir)
        if state.get("publish_id"):
            command_status(make_args(post_dir))
            state = load_state(post_dir)
        return {"slug": slug, "state": redact_state(state)}


class ConfiguredServer(ThreadingHTTPServer):
    """携带服务配置的 HTTPServer。"""

    def __init__(self, server_address: tuple[str, int], handler: type[BaseHTTPRequestHandler], config: ServerConfig) -> None:
        super().__init__(server_address, handler)
        self.config = config


def main() -> int:
    """启动服务。"""
    try:
        config = load_server_config()
    except ServiceError as exc:
        print(f"ERROR: {exc.message}", file=sys.stderr)
        return 1
    config.workdir.mkdir(parents=True, exist_ok=True)
    server = ConfiguredServer((config.host, config.port), WechatPublishHandler, config)
    print(f"wechat publish service listening on {config.host}:{config.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("wechat publish service stopped", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
