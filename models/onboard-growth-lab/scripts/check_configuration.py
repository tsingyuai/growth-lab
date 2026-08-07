#!/usr/bin/env python3
"""Report Growth Lab local capability configuration without printing secrets."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[3]
ALLOWED = {
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_IMAGE_MODEL",
    "OPENAI_TEXT_MODEL",
    "GEMINI_API_KEY",
    "GOOGLE_GEMINI_BASE_URL",
    "XHS_MCP_ENDPOINT",
    "XHS_MCP_BINARY",
    "XHS_MCP_LOGIN_BINARY",
    "XHS_MCP_COOKIES_PATH",
    "DEFAULT_SAMPLE_LIMIT",
    "TIKTOK_ACCESS_TOKEN",
    "TIKTOK_API_BASE_URL",
    "TIKTOK_MCP_ENDPOINT",
    "INSTAGRAM_ACCESS_TOKEN",
    "INSTAGRAM_GRAPH_BASE_URL",
    "INSTAGRAM_GRAPH_API_VERSION",
    "INSTAGRAM_USER_ID",
    "INSTAGRAM_PROFILE_FIELDS",
    "INSTAGRAM_MCP_ENDPOINT",
    "SOCIAL_PROXY_MODE",
    "SOCIAL_PROXY_URL",
    "SOCIAL_PROXY_BYPASS",
    "SOCIAL_BROWSER_FAMILY",
    "SOCIAL_BROWSER_PATH",
    "X_BROWSER_PROFILE_DIR",
    "X_BROWSER_PYTHON",
    "X_BROWSER_CDP_PORT",
    "X_CONNECTIVITY_URL",
    "X_USER_ACCESS_TOKEN",
    "WECHAT_APP_ID",
    "WECHAT_APP_SECRET",
    "VIDEO_RENDERER_PYTHON",
    "VIDEO_FFMPEG_PATH",
    "SOCIAL_TTS_PYTHON",
    "ARK_API_KEY",
    "ARK_BASE_URL",
    "SEEDANCE_MODEL_ENDPOINT",
}


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
        if key not in ALLOWED:
            continue
        values[key] = value.strip().strip('"').strip("'")
    return values


def resolved_values(root: Path, environ: Mapping[str, str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for filename in (".env", ".env.local"):
        values.update(read_env_file(root / filename))
    for key in ALLOWED:
        if environ.get(key):
            values[key] = environ[key]
    home_value = environ.get("USERPROFILE") or environ.get("HOME")
    if home_value:
        home = Path(home_value).expanduser()
        client_dir = home / ".growth-lab" / "clients" / "xiaohongshu-mcp"
        defaults = {
            "XHS_MCP_BINARY": client_dir / "xiaohongshu-mcp-windows-amd64.exe",
            "XHS_MCP_LOGIN_BINARY": client_dir / "xiaohongshu-login-windows-amd64.exe",
        }
        for key, candidate in defaults.items():
            if key not in values and candidate.is_file():
                values[key] = str(candidate)
        if "XHS_MCP_COOKIES_PATH" not in values:
            standard_cookie = client_dir / "cookies.json"
            legacy_cookie = home / ".xhs-autopilot" / "xiaohongshu-mcp" / "cookies.json"
            values["XHS_MCP_COOKIES_PATH"] = str(
                standard_cookie if standard_cookie.is_file() or not legacy_cookie.is_file() else legacy_cookie
            )
    return values


def configured_file(value: str) -> bool:
    if not value:
        return False
    expanded = os.path.expandvars(os.path.expanduser(value))
    return Path(expanded).is_file()


def configured_dir(value: str) -> bool:
    if not value:
        return False
    expanded = os.path.expandvars(os.path.expanduser(value))
    return Path(expanded).is_dir()


def external_dir(value: str, root: Path) -> bool:
    if not configured_dir(value):
        return False
    expanded = Path(os.path.expandvars(os.path.expanduser(value))).resolve()
    try:
        expanded.relative_to(root.resolve())
    except ValueError:
        return True
    return False


def configured_browser(values: Mapping[str, str]) -> tuple[str, bool]:
    family = (values.get("SOCIAL_BROWSER_FAMILY") or "auto").strip().lower()
    configured_path = values.get("SOCIAL_BROWSER_PATH", "").strip()
    if family not in {"auto", "chrome", "edge"}:
        return family, False
    if configured_path:
        name = Path(configured_path).name.lower()
        detected = "edge" if name == "msedge.exe" else "chrome"
        return detected, configured_file(configured_path)
    paths = {
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "edge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
    }
    families = ("chrome", "edge") if family == "auto" else (family,)
    for candidate in families:
        if any(configured_file(path) for path in paths[candidate]):
            return candidate, True
    return family, False


def local_service_reachable(endpoint: str, timeout: float = 0.5) -> bool:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        return False
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"{endpoint.rstrip('/')}/health", timeout=timeout) as response:
            payload = json.loads(response.read(1024 * 1024).decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and bool(payload.get("success"))


def audit(root: Path, environ: Mapping[str, str], probe_services: bool = True) -> dict:
    values = resolved_values(root, environ)
    missing: list[str] = []
    for name in ("XHS_MCP_BINARY", "XHS_MCP_LOGIN_BINARY"):
        if not values.get(name):
            missing.append(name)
        elif not configured_file(values[name]):
            missing.append(f"{name} (file not found)")

    cookie_value = values.get("XHS_MCP_COOKIES_PATH", "")
    has_login_state = configured_file(cookie_value)
    if missing:
        xhs_status = "missing-configuration"
    elif not has_login_state:
        xhs_status = "needs-visible-login"
    else:
        xhs_status = "configured-not-verified"

    providers: list[str] = []
    if values.get("OPENAI_API_KEY"):
        providers.append("openai")
    if values.get("GEMINI_API_KEY"):
        providers.append("gemini")
    image_status = "configured-not-verified" if providers else "optional-missing"
    x_publish_configured = bool(values.get("X_USER_ACCESS_TOKEN"))
    wechat_configured = bool(values.get("WECHAT_APP_ID") and values.get("WECHAT_APP_SECRET"))
    video_python = values.get(
        "VIDEO_RENDERER_PYTHON",
        r"%USERPROFILE%\.growth-lab\clients\social-video-venv\Scripts\python.exe",
    )
    video_runtime_present = configured_file(video_python)
    tts_python = values.get(
        "SOCIAL_TTS_PYTHON",
        r"%USERPROFILE%\.growth-lab\clients\social-tts-venv\Scripts\python.exe",
    )
    tts_runtime_present = configured_file(tts_python)
    seedance_missing = [
        key for key in ("ARK_API_KEY", "SEEDANCE_MODEL_ENDPOINT") if not values.get(key)
    ]
    seedance_base_url = values.get(
        "ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"
    )
    video_ffmpeg = values.get("VIDEO_FFMPEG_PATH", "")
    video_ffmpeg_status = (
        "configured-not-verified"
        if video_ffmpeg and configured_file(video_ffmpeg)
        else "runtime-managed"
        if not video_ffmpeg and video_runtime_present
        else "missing"
    )
    tiktok_api_status = (
        "configured-not-verified" if values.get("TIKTOK_ACCESS_TOKEN") else "missing-configuration"
    )
    instagram_api_status = (
        "configured-not-verified"
        if values.get("INSTAGRAM_ACCESS_TOKEN")
        else "missing-configuration"
    )
    tiktok_endpoint = values.get("TIKTOK_MCP_ENDPOINT") or "http://127.0.0.1:18064"
    instagram_endpoint = values.get("INSTAGRAM_MCP_ENDPOINT") or "http://127.0.0.1:18065"
    tiktok_runtime = probe_services and local_service_reachable(tiktok_endpoint)
    instagram_runtime = probe_services and local_service_reachable(instagram_endpoint)
    browser_family, browser_present = configured_browser(values)
    x_profile = values.get(
        "X_BROWSER_PROFILE_DIR", r"%LOCALAPPDATA%\growth-lab\x\browser-profile"
    )
    x_python = values.get(
        "X_BROWSER_PYTHON",
        r"%USERPROFILE%\.growth-lab\clients\x-browser-venv\Scripts\python.exe",
    )
    x_profile_exists = configured_dir(x_profile)
    x_profile_external = external_dir(x_profile, root)
    try:
        x_cdp_port = int(values.get("X_BROWSER_CDP_PORT", "19222"))
        x_cdp_valid = 1024 <= x_cdp_port <= 65535
    except ValueError:
        x_cdp_port = 0
        x_cdp_valid = False
    if not configured_file(x_python):
        x_status = "missing-runtime"
    elif not browser_present:
        x_status = "missing-browser"
    elif not x_cdp_valid:
        x_status = "invalid-cdp-port"
    elif x_profile_exists and not x_profile_external:
        x_status = "invalid-profile-location"
    elif not x_profile_exists:
        x_status = "needs-visible-login"
    else:
        x_status = "configured-not-verified"
    proxy_mode = (values.get("SOCIAL_PROXY_MODE") or "auto").lower()
    proxy_url_present = bool(values.get("SOCIAL_PROXY_URL"))
    bypass_raw = values.get("SOCIAL_PROXY_BYPASS") or "127.0.0.1,localhost,::1"
    bypass_hosts = {item.strip().lower() for item in bypass_raw.split(",") if item.strip()}
    loopback_bypass = {"127.0.0.1", "localhost", "::1"}.issubset(bypass_hosts)
    if proxy_mode not in {"auto", "direct", "system", "explicit"}:
        network_status = "invalid-configuration"
        network_missing = ["SOCIAL_PROXY_MODE must be auto, direct, system, or explicit"]
    elif proxy_mode == "explicit" and not proxy_url_present:
        network_status = "missing-configuration"
        network_missing = ["SOCIAL_PROXY_URL"]
    elif not loopback_bypass:
        network_status = "invalid-configuration"
        network_missing = ["SOCIAL_PROXY_BYPASS must include 127.0.0.1, localhost, and ::1"]
    else:
        network_status = (
            "direct-selected"
            if proxy_mode == "direct"
            else f"{proxy_mode}-configured-not-verified"
        )
        network_missing = []

    try:
        requested_default = int(values.get("DEFAULT_SAMPLE_LIMIT", "25"))
    except ValueError:
        requested_default = 25

    return {
        "schema_version": 1,
        "configuration_precedence": ["process environment", ".env.local", ".env"],
        "configuration_guide": "CONFIGURATION.md",
        "network_access": {
            "status": network_status,
            "mode": proxy_mode,
            "proxy_url": "present-not-displayed" if proxy_url_present else "missing",
            "loopback_bypass": "valid" if loopback_bypass else "invalid",
            "missing": network_missing,
            "must_precede_social_login": True,
            "automatic_proxy_rotation": False,
            "system_mode_uses_os_pac_or_domain_rules": proxy_mode == "system",
        },
        "xiaohongshu": {
            "status": xhs_status,
            "missing": missing,
            "login_state": "present-not-verified" if has_login_state else "missing",
            "first_run_default": requested_default,
            "recommended": 25,
            "requires_api_key": False,
            "publishing": "authorized-browser-automation-separate-approval",
        },
        "image_generation": {
            "status": image_status,
            "configured_providers": providers,
            "required_for_collection": False,
            "missing_when_requested": [] if providers else ["OPENAI_API_KEY or GEMINI_API_KEY"],
            "paid_verification_requires_approval": True,
        },
        "tiktok": {
            "status": "configured-not-verified" if tiktok_runtime else "missing-runtime",
            "missing": [] if tiktok_runtime else ["approved and running TikTok local adapter"],
            "access": "public-content research via local read-only adapter",
            "official_account_api": {
                "status": tiktok_api_status,
                "missing": [] if values.get("TIKTOK_ACCESS_TOKEN") else ["TIKTOK_ACCESS_TOKEN"],
            },
        },
        "instagram": {
            "status": "configured-not-verified" if instagram_runtime else "missing-runtime",
            "missing": [] if instagram_runtime else ["approved and running Instagram local adapter"],
            "access": "public-content research via local read-only adapter",
            "official_account_api": {
                "status": instagram_api_status,
                "missing": (
                    [] if values.get("INSTAGRAM_ACCESS_TOKEN") else ["INSTAGRAM_ACCESS_TOKEN"]
                ),
            },
        },
        "x": {
            "status": x_status,
            "network_mode": proxy_mode,
            "shared_proxy_configured": proxy_url_present,
            "login_state": (
                "profile-present-not-verified" if x_profile_external else "missing"
            ),
            "profile_location": "external" if x_profile_external else (
                "inside-repository-invalid" if x_profile_exists else "missing"
            ),
            "requires_api_key": False,
            "runtime": "present-not-verified" if configured_file(x_python) else "missing",
            "browser_family": browser_family,
            "browser": "present-not-verified" if browser_present else "missing",
            "cdp": {
                "endpoint": f"127.0.0.1:{x_cdp_port}" if x_cdp_valid else "invalid",
                "loopback_only": True,
                "status": "configured-not-verified" if x_cdp_valid else "invalid-configuration",
            },
            "preflight_required": True,
            "publishing": "official-api-available-separate-approval",
            "official_publishing_api": {
                "status": "configured-not-verified" if x_publish_configured else "missing-configuration",
                "missing": [] if x_publish_configured else ["X_USER_ACCESS_TOKEN"],
                "separate_from_browser_login": True,
            },
        },
        "wechat": {
            "official_account_api": {
                "status": "configured-not-verified" if wechat_configured else "missing-configuration",
                "missing": [] if wechat_configured else ["WECHAT_APP_ID", "WECHAT_APP_SECRET"],
                "draft_and_publish_require_separate_approval": True,
            }
        },
        "video_generation": {
            "status": "configured-not-verified" if video_runtime_present else "optional-missing-runtime",
            "runtime": "present-not-verified" if video_runtime_present else "missing",
            "ffmpeg": video_ffmpeg_status,
            "local_tts": "present-not-verified" if tts_runtime_present else "optional-missing",
            "seedance_broll": {
                "status": "configured-not-verified" if not seedance_missing else "optional-missing-configuration",
                "missing": seedance_missing,
                "base_url": "present-not-verified" if seedance_base_url else "missing",
                "paid_generation_requires_confirmation": True,
                "live_generation_verified": False,
            },
            "explicit_request_only": True,
            "platform_publication_separately_gated": True,
        },
    }


def main() -> int:
    print(json.dumps(audit(ROOT, os.environ), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
