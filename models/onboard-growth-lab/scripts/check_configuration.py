#!/usr/bin/env python3
"""Report Growth Lab local capability configuration without printing secrets."""

from __future__ import annotations

import json
import os
import subprocess
import sys
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
    "ZHIHU_CLI_BIN",
    "ZHIHU_CLI_HOME",
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


def audit_zhihu(values: Mapping[str, str], environ: Mapping[str, str]) -> dict:
    script = ROOT / "models" / "onboard-growth-lab" / "scripts" / "onboard_zhihu.py"
    command = [sys.executable, str(script), "status"]
    configured_binary = values.get("ZHIHU_CLI_BIN", "")
    if configured_binary and not configured_file(configured_binary):
        return {
            "status": "configured-binary-not-found",
            "provenance": "zhihu-official-cli",
        }
    if configured_binary:
        command.extend(["--binary", os.path.expanduser(values["ZHIHU_CLI_BIN"])])

    process_env = os.environ.copy()
    process_env.pop("ZHIHU_CLI_BIN", None)
    process_env.pop("ZHIHU_CLI_HOME", None)
    process_env.update(environ)
    if values.get("ZHIHU_CLI_HOME"):
        process_env["ZHIHU_CLI_HOME"] = values["ZHIHU_CLI_HOME"]
    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
            env=process_env,
        )
        payload = json.loads(completed.stdout) if completed.stdout.strip() else {}
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        return {
            "status": "inspection-error",
            "error": type(exc).__name__,
            "provenance": "zhihu-official-cli",
        }

    if completed.returncode != 0 or not payload.get("ok"):
        return {
            "status": "inspection-error",
            "error": payload.get("error", {}).get("code", f"exit-{completed.returncode}"),
            "provenance": "zhihu-official-cli",
        }
    readiness = payload.get("readiness")
    auth = payload.get("auth") if isinstance(payload.get("auth"), dict) else {}
    mapped_status = {
        "missing-cli": "missing-cli",
        "incompatible-cli": "incompatible-cli",
        "needs-access-secret": "needs-access-secret",
        "ready-to-verify": "configured-not-verified",
        "ready": "ready",
    }.get(readiness, "inspection-error")
    action = payload.get("action") if isinstance(payload.get("action"), dict) else {}
    return {
        "status": mapped_status,
        "readiness": readiness,
        "version": payload.get("version"),
        "minimum_version": payload.get("minimum_version"),
        "binary_path": payload.get("binary_path"),
        "auth_source": auth.get("source"),
        "next_action": action.get("next_action"),
        "command": action.get("command"),
        "provenance": "zhihu-official-cli",
    }


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
        "zhihu": audit_zhihu(values, environ),
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
