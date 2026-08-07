#!/usr/bin/env python3
"""Internal official-account API readiness probes for social collectors."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Mapping


class ProxyConfigurationError(ValueError):
    pass


def load_value(name: str, root: Path, environ: Mapping[str, str]) -> str:
    value = ""
    for filename in (".env", ".env.local"):
        path = root / filename
        if not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, candidate = line.split("=", 1)
            if key.strip() == name:
                value = candidate.strip().strip('"').strip("'")
    return environ.get(name) or value


def build_remote_opener(root: Path, environ: Mapping[str, str]):
    mode = (load_value("SOCIAL_PROXY_MODE", root, environ) or "direct").lower()
    if mode == "direct":
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    if mode == "system":
        return urllib.request.build_opener(urllib.request.ProxyHandler())
    if mode != "explicit":
        raise ProxyConfigurationError("SOCIAL_PROXY_MODE must be direct, system, or explicit")
    proxy_url = load_value("SOCIAL_PROXY_URL", root, environ)
    parsed = urllib.parse.urlparse(proxy_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ProxyConfigurationError("SOCIAL_PROXY_URL must be a valid HTTP(S) proxy URL")
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
    )


def probe_tiktok(root: Path, environ: Mapping[str, str], timeout: float = 20) -> dict:
    token = load_value("TIKTOK_ACCESS_TOKEN", root, environ)
    if not token:
        return {"platform": "tiktok", "status": "missing-configuration", "missing": ["TIKTOK_ACCESS_TOKEN"]}
    base_url = load_value("TIKTOK_API_BASE_URL", root, environ) or "https://open.tiktokapis.com"
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme != "https" or parsed.hostname != "open.tiktokapis.com":
        return {"platform": "tiktok", "status": "invalid-configuration", "invalid": ["TIKTOK_API_BASE_URL"]}
    url = f"{base_url.rstrip('/')}/v2/user/info/?{urllib.parse.urlencode({'fields': 'open_id,display_name'})}"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        opener = build_remote_opener(root, environ)
        with opener.open(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except ProxyConfigurationError:
        return {"platform": "tiktok", "status": "invalid-configuration", "invalid": ["SOCIAL_PROXY_MODE or SOCIAL_PROXY_URL"]}
    except urllib.error.HTTPError as exc:
        return {"platform": "tiktok", "status": "verification-failed", "http_status": exc.code}
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"platform": "tiktok", "status": "verification-failed", "reason": type(exc).__name__}
    error = payload.get("error") or {}
    user = (payload.get("data") or {}).get("user") or {}
    if error.get("code") not in (None, "ok") or not user:
        return {"platform": "tiktok", "status": "verification-failed", "api_error": str(error.get("code") or "empty-user")}
    return {
        "platform": "tiktok",
        "status": "verified",
        "account": {"open_id": str(user.get("open_id") or ""), "display_name": str(user.get("display_name") or "")},
        "scope": "authorized account profile only; not public-content research",
    }


def probe_instagram(root: Path, environ: Mapping[str, str], timeout: float = 20) -> dict:
    token = load_value("INSTAGRAM_ACCESS_TOKEN", root, environ)
    if not token:
        return {"platform": "instagram", "status": "missing-configuration", "missing": ["INSTAGRAM_ACCESS_TOKEN"]}
    base_url = load_value("INSTAGRAM_GRAPH_BASE_URL", root, environ) or "https://graph.instagram.com"
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme != "https" or parsed.hostname not in {"graph.instagram.com", "graph.facebook.com"}:
        return {"platform": "instagram", "status": "invalid-configuration", "invalid": ["INSTAGRAM_GRAPH_BASE_URL"]}
    version = load_value("INSTAGRAM_GRAPH_API_VERSION", root, environ).strip("/")
    account = load_value("INSTAGRAM_USER_ID", root, environ) or "me"
    fields = load_value("INSTAGRAM_PROFILE_FIELDS", root, environ) or "user_id,username"
    prefix = f"/{version}" if version else ""
    url = f"{base_url.rstrip('/')}{prefix}/{urllib.parse.quote(account, safe='')}?{urllib.parse.urlencode({'fields': fields})}"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        opener = build_remote_opener(root, environ)
        with opener.open(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except ProxyConfigurationError:
        return {"platform": "instagram", "status": "invalid-configuration", "invalid": ["SOCIAL_PROXY_MODE or SOCIAL_PROXY_URL"]}
    except urllib.error.HTTPError as exc:
        return {"platform": "instagram", "status": "verification-failed", "http_status": exc.code}
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"platform": "instagram", "status": "verification-failed", "reason": type(exc).__name__}
    account_id = payload.get("user_id") or payload.get("id")
    if payload.get("error") or not account_id:
        error = payload.get("error") or {}
        return {"platform": "instagram", "status": "verification-failed", "api_error": str(error.get("code") or "empty-account")}
    return {
        "platform": "instagram",
        "status": "verified",
        "account": {"user_id": str(account_id), "username": str(payload.get("username") or "")},
        "scope": "authorized account profile only; not public-content research",
    }
