#!/usr/bin/env python3
"""Ensure the local Xiaohongshu runtime is authenticated, then run collection."""

from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
COLLECTOR = Path(__file__).with_name("collect_xiaohongshu.py")
DEFAULT_ENDPOINT = "http://127.0.0.1:18063"
DEFAULT_CLIENT_RELATIVE = Path(".growth-lab") / "clients" / "xiaohongshu-mcp"
LEGACY_COOKIE_RELATIVE = Path(".xhs-autopilot") / "xiaohongshu-mcp" / "cookies.json"
ENV_KEYS = {
    "XHS_MCP_ENDPOINT",
    "XHS_MCP_BINARY",
    "XHS_MCP_LOGIN_BINARY",
    "XHS_MCP_COOKIES_PATH",
}


class RuntimeError(Exception):
    """Expected runtime failure that can be shown without a traceback."""


class LoginCheckTimeout(RuntimeError):
    pass


def emit(status: str, message: str, **extra: Any) -> None:
    print(
        json.dumps({"status": status, "message": message, **extra}, ensure_ascii=False),
        file=sys.stderr,
        flush=True,
    )


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in ENV_KEYS:
            values[key] = value.strip().strip('"').strip("'")
    return values


def resolved_config(root: Path, environ: Mapping[str, str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for filename in (".env", ".env.local"):
        values.update(read_env_file(root / filename))
    for key in ENV_KEYS:
        if environ.get(key):
            values[key] = environ[key]
    home_value = environ.get("USERPROFILE") or environ.get("HOME")
    if home_value:
        home = Path(home_value).expanduser()
        client_dir = home / DEFAULT_CLIENT_RELATIVE
        defaults = {
            "XHS_MCP_BINARY": client_dir / "xiaohongshu-mcp-windows-amd64.exe",
            "XHS_MCP_LOGIN_BINARY": client_dir / "xiaohongshu-login-windows-amd64.exe",
        }
        for key, candidate in defaults.items():
            if key not in values and candidate.is_file():
                values[key] = str(candidate)
        if "XHS_MCP_COOKIES_PATH" not in values:
            standard_cookie = client_dir / "cookies.json"
            legacy_cookie = home / LEGACY_COOKIE_RELATIVE
            values["XHS_MCP_COOKIES_PATH"] = str(
                standard_cookie if standard_cookie.is_file() or not legacy_cookie.is_file() else legacy_cookie
            )
    return values


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def validate_endpoint(endpoint: str) -> tuple[str, int]:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("XHS_MCP_ENDPOINT 必须是本机 HTTP 地址")
    if not parsed.port:
        raise RuntimeError("XHS_MCP_ENDPOINT 必须包含端口")
    return endpoint.rstrip("/"), parsed.port


def request_json(endpoint: str, path: str, timeout: float) -> dict[str, Any]:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(f"{endpoint}{path}", headers={"Accept": "application/json"})
    try:
        with opener.open(request, timeout=timeout) as response:
            payload = json.loads(response.read(1024 * 1024).decode("utf-8"))
    except (TimeoutError, urllib.error.URLError) as exc:
        if isinstance(getattr(exc, "reason", None), TimeoutError) or isinstance(exc, TimeoutError):
            raise LoginCheckTimeout(f"{path} 在 {timeout:g} 秒内未响应") from exc
        raise RuntimeError(f"无法连接本机 xiaohongshu-mcp: {exc}") from exc
    except (urllib.error.HTTPError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"xiaohongshu-mcp 返回无效响应: {exc}") from exc
    if not isinstance(payload, dict) or not payload.get("success"):
        raise RuntimeError("xiaohongshu-mcp 返回失败状态")
    data = payload.get("data")
    return data if isinstance(data, dict) else {}


def service_healthy(endpoint: str, timeout: float = 2) -> bool:
    try:
        data = request_json(endpoint, "/health", timeout)
    except RuntimeError:
        return False
    return data.get("status") == "healthy"


def login_status(endpoint: str, timeout: float) -> bool:
    results: queue.Queue[tuple[bool | None, BaseException | None]] = queue.Queue(maxsize=1)

    def request() -> None:
        try:
            data = request_json(endpoint, "/api/v1/login/status", timeout)
            results.put((bool(data.get("is_logged_in")), None))
        except BaseException as exc:
            results.put((None, exc))

    threading.Thread(target=request, daemon=True).start()
    deadline = time.monotonic() + timeout
    next_notice = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            value, error = results.get(timeout=min(1, max(0.1, deadline - time.monotonic())))
        except queue.Empty:
            if time.monotonic() >= next_notice:
                remaining = max(0, int(deadline - time.monotonic()))
                emit("login-checking", "仍在检查小红书登录状态", remaining_seconds=remaining)
                next_notice += 5
            continue
        if error:
            raise error
        return bool(value)
    raise LoginCheckTimeout(f"登录状态在 {timeout:g} 秒内未响应")


def normalized_child_env(environ: Mapping[str, str], cookie_path: Path) -> dict[str, str]:
    child: dict[str, str] = {}
    for key, value in environ.items():
        if key.casefold() == "path":
            continue
        child[key] = value
    path_value = next((value for key, value in environ.items() if key == "Path"), None)
    if path_value is None:
        path_value = next((value for key, value in environ.items() if key.casefold() == "path"), "")
    child["Path"] = path_value
    child["COOKIES_PATH"] = str(cookie_path)
    return child


def require_file(value: str, field: str) -> Path:
    if not value:
        raise RuntimeError(f"缺少 {field}；请在 .env.local 中配置")
    path = expand_path(value)
    if not path.is_file():
        raise RuntimeError(f"{field} 指向的文件不存在")
    return path


def wait_until(
    predicate: Callable[[], bool],
    timeout: float,
    waiting_message: str,
    interval: float = 0.5,
) -> bool:
    deadline = time.monotonic() + timeout
    next_notice = time.monotonic() + 5
    while time.monotonic() < deadline:
        if predicate():
            return True
        if time.monotonic() >= next_notice:
            remaining = max(0, int(deadline - time.monotonic()))
            emit("waiting", waiting_message, remaining_seconds=remaining)
            next_notice += 5
        time.sleep(interval)
    return False


class RuntimeManager:
    def __init__(
        self,
        endpoint: str,
        service_binary: Path,
        login_binary: Path,
        cookie_path: Path,
        environ: Mapping[str, str],
        log_dir: Path,
    ) -> None:
        self.endpoint, self.port = validate_endpoint(endpoint)
        self.service_binary = service_binary
        self.login_binary = login_binary
        self.cookie_path = cookie_path
        self.child_env = normalized_child_env(environ, cookie_path)
        self.log_dir = log_dir
        self.service_process: subprocess.Popen[bytes] | None = None
        self._stdout = None
        self._stderr = None

    def start_service(self, timeout: float) -> bool:
        if service_healthy(self.endpoint):
            emit("service-ready", "检测到已运行的小红书服务", owned=False)
            return False
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.cookie_path.parent.mkdir(parents=True, exist_ok=True)
        self._stdout = (self.log_dir / "service.stdout.log").open("ab")
        self._stderr = (self.log_dir / "service.stderr.log").open("ab")
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self.service_process = subprocess.Popen(
            [str(self.service_binary), "-port", f":{self.port}", "-headless=true"],
            stdin=subprocess.DEVNULL,
            stdout=self._stdout,
            stderr=self._stderr,
            env=self.child_env,
            creationflags=creationflags,
        )
        emit("service-starting", "正在启动小红书只读服务", pid=self.service_process.pid)

        def ready() -> bool:
            if self.service_process and self.service_process.poll() is not None:
                raise RuntimeError(f"xiaohongshu-mcp 启动失败，退出码 {self.service_process.returncode}")
            return service_healthy(self.endpoint)

        if not wait_until(ready, timeout, "仍在等待小红书服务启动"):
            self.stop_service()
            raise RuntimeError(f"xiaohongshu-mcp 未在 {timeout:g} 秒内通过健康检查")
        emit("service-ready", "小红书服务已就绪", owned=True)
        return True

    def stop_service(self) -> None:
        process = self.service_process
        self.service_process = None
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        for handle_name in ("_stdout", "_stderr"):
            handle = getattr(self, handle_name)
            if handle:
                handle.close()
                setattr(self, handle_name, None)

    def run_visible_login(self, timeout: float) -> None:
        if self.service_process is None and service_healthy(self.endpoint):
            raise RuntimeError(
                "检测到不是本协调器启动的小红书服务；请先停止该服务，再打开登录窗口"
            )
        self.stop_service()
        emit(
            "login-required",
            "已打开小红书登录窗口，请由用户本人扫码；不会执行点赞、收藏、评论或发布",
        )
        login = subprocess.Popen([str(self.login_binary)], env=self.child_env)

        def finished() -> bool:
            return login.poll() is not None

        if not wait_until(finished, timeout, "等待用户完成小红书登录", interval=1):
            login.terminate()
            try:
                login.wait(timeout=3)
            except subprocess.TimeoutExpired:
                login.kill()
            raise RuntimeError(f"用户未在 {timeout:g} 秒内完成小红书登录")
        if login.returncode != 0:
            raise RuntimeError(f"小红书登录程序退出码为 {login.returncode}")
        emit("login-window-complete", "登录程序已完成，正在验证登录态")


def check_login_with_one_restart(
    manager: RuntimeManager,
    auth_timeout: float,
    service_timeout: float,
) -> bool:
    try:
        return login_status(manager.endpoint, auth_timeout)
    except LoginCheckTimeout:
        if manager.service_process is None:
            raise RuntimeError("已有小红书服务的登录检查超时；请停止该服务后重试")
        emit("service-restarting", "浏览器冷启动超时，正在重启一次小红书服务")
        manager.stop_service()
        manager.start_service(service_timeout)
        try:
            return login_status(manager.endpoint, auth_timeout)
        except LoginCheckTimeout as exc:
            raise RuntimeError("小红书浏览器初始化连续两次超时，已停止且不会继续重试") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="自动准备小红书本机运行时和登录态，然后恢复只读采集",
        epilog="未识别参数会原样传给 collect_xiaohongshu.py。",
    )
    parser.add_argument("--allow-visible-login", action="store_true")
    parser.add_argument("--runtime-service-timeout", type=float, default=20)
    parser.add_argument("--runtime-auth-timeout", type=float, default=45)
    parser.add_argument("--runtime-login-timeout", type=float, default=180)
    parser.add_argument("--runtime-collection-timeout", type=float, default=180)
    parser.add_argument("--keep-service-running", action="store_true")
    return parser


def validate_timeouts(args: argparse.Namespace) -> None:
    values = {
        "--runtime-service-timeout": (args.runtime_service_timeout, 5, 60),
        "--runtime-auth-timeout": (args.runtime_auth_timeout, 5, 90),
        "--runtime-login-timeout": (args.runtime_login_timeout, 30, 600),
        "--runtime-collection-timeout": (args.runtime_collection_timeout, 30, 1800),
    }
    for name, (value, minimum, maximum) in values.items():
        if value < minimum or value > maximum:
            raise RuntimeError(f"{name} 必须在 {minimum} 到 {maximum} 秒之间")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args, collector_args = parser.parse_known_args(argv)
    manager: RuntimeManager | None = None
    try:
        validate_timeouts(args)
        if not collector_args or collector_args[0].startswith("-"):
            raise RuntimeError("请提供要采集的小红书关键词")
        config = resolved_config(ROOT, os.environ)
        endpoint = config.get("XHS_MCP_ENDPOINT", DEFAULT_ENDPOINT)
        service_binary = require_file(config.get("XHS_MCP_BINARY", ""), "XHS_MCP_BINARY")
        login_binary = require_file(config.get("XHS_MCP_LOGIN_BINARY", ""), "XHS_MCP_LOGIN_BINARY")
        cookie_path = expand_path(config.get("XHS_MCP_COOKIES_PATH", "cookies.json"))
        log_dir = cookie_path.parent / "runtime-logs"
        manager = RuntimeManager(
            endpoint, service_binary, login_binary, cookie_path, os.environ, log_dir
        )
        manager.start_service(args.runtime_service_timeout)
        logged_in = check_login_with_one_restart(
            manager, args.runtime_auth_timeout, args.runtime_service_timeout
        )
        if not logged_in:
            if not args.allow_visible_login:
                raise RuntimeError(
                    "小红书尚未登录；获得用户同意后使用 --allow-visible-login 打开二维码窗口"
                )
            manager.run_visible_login(args.runtime_login_timeout)
            manager.start_service(args.runtime_service_timeout)
            if not check_login_with_one_restart(
                manager, args.runtime_auth_timeout, args.runtime_service_timeout
            ):
                raise RuntimeError("登录程序完成，但小红书登录态仍未生效")
        emit("login-ready", "小红书登录状态有效，正在继续原采集任务")
        collection_env = dict(os.environ)
        collection_env["XHS_MCP_ENDPOINT"] = manager.endpoint
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(COLLECTOR),
                    "--runtime-authenticated",
                    *collector_args,
                ],
                env=collection_env,
                timeout=args.runtime_collection_timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"小红书采集超过 {args.runtime_collection_timeout:g} 秒，已停止"
            ) from exc
        return completed.returncode
    except RuntimeError as exc:
        emit("stopped", str(exc))
        return 2
    finally:
        if manager and not args.keep_service_running:
            manager.stop_service()


if __name__ == "__main__":
    raise SystemExit(main())
