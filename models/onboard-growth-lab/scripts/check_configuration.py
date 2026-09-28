#!/usr/bin/env python3
"""Report Growth Lab local capability configuration without printing secrets."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[3]
ALLOWED = {
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_IMAGE_MODEL",
    "GEMINI_API_KEY",
    "GOOGLE_GEMINI_BASE_URL",
    "XHS_MCP_ENDPOINT",
    "XHS_MCP_BINARY",
    "XHS_MCP_LOGIN_BINARY",
    "XHS_MCP_COOKIES_PATH",
    "DEFAULT_SAMPLE_LIMIT",
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
    return values


def configured_file(value: str) -> bool:
    if not value:
        return False
    expanded = os.path.expandvars(os.path.expanduser(value))
    return Path(expanded).is_file()


def audit(root: Path, environ: Mapping[str, str]) -> dict:
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

    try:
        requested_default = int(values.get("DEFAULT_SAMPLE_LIMIT", "25"))
    except ValueError:
        requested_default = 25

    return {
        "schema_version": 1,
        "configuration_precedence": ["process environment", ".env.local", ".env"],
        "configuration_guide": "CONFIGURATION.md",
        "xiaohongshu": {
            "status": xhs_status,
            "missing": missing,
            "login_state": "present-not-verified" if has_login_state else "missing",
            "first_run_default": requested_default,
            "recommended": 25,
            "requires_api_key": False,
        },
        "image_generation": {
            "status": image_status,
            "configured_providers": providers,
            "required_for_collection": False,
            "missing_when_requested": [] if providers else ["OPENAI_API_KEY or GEMINI_API_KEY"],
            "paid_verification_requires_approval": True,
        },
    }


def main() -> int:
    print(json.dumps(audit(ROOT, os.environ), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
