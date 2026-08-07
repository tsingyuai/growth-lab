#!/usr/bin/env python3
"""Report implemented local Client readiness without exposing secrets."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


def load_repo_env() -> None:
    repo = Path(__file__).resolve().parents[4]
    env_file = repo / ".env"
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> int:
    load_repo_env()

    def present(name: str) -> bool:
        return bool(os.environ.get(name, "").strip())

    bing_present = present("BING_WEBMASTER_API_KEY")
    indexnow_key_present = present("INDEXNOW_KEY")
    site_url_present = present("SITE_URL")
    openai_present = present("OPENAI_API_KEY")
    gemini_present = present("GEMINI_API_KEY")
    wechat_app_id_present = present("WECHAT_OFFICIAL_APP_ID")
    wechat_app_secret_present = present("WECHAT_OFFICIAL_APP_SECRET")
    xhs_binary = os.environ.get("XHS_MCP_BINARY", "").strip()
    xhs_login_binary = os.environ.get("XHS_MCP_LOGIN_BINARY", "").strip()
    report = {
        "node_runtime": {
            "available": shutil.which("node") is not None,
        },
        "bing_webmaster": {
            "implemented": True,
            "environment_variable": "BING_WEBMASTER_API_KEY",
            "credential_present": bing_present,
            "credential_value_read": False,
            "requires_api_verification": bing_present,
        },
        "webmaster_export": {
            "implemented": True,
            "credential_required": False,
            "supported_formats": ["csv", "json"],
        },
        "product_event_export": {
            "implemented": True,
            "credential_required": False,
            "supported_formats": ["csv", "json", "ndjson"],
            "raw_identifiers_in_output": False,
        },
        "social_platform_export": {
            "implemented": True,
            "credential_required": False,
            "supported_formats": ["csv", "json", "ndjson"],
            "raw_private_rows_in_output": False,
        },
        "xiaohongshu_research": {
            "implemented": True,
            "read_only": True,
            "default_items": 25,
            "endpoint": os.environ.get("XHS_MCP_ENDPOINT", "http://127.0.0.1:18063"),
            "service_binary_configured": bool(xhs_binary),
            "service_binary_exists": bool(xhs_binary and Path(xhs_binary).is_file()),
            "login_binary_configured": bool(xhs_login_binary),
            "login_binary_exists": bool(xhs_login_binary and Path(xhs_login_binary).is_file()),
            "login_state_value_read": False,
            "requires_low_impact_verification": True,
            "note": "A visible QR login is offered only after user approval; collection performs no account actions.",
        },
        "seo_content_inventory": {
            "implemented": True,
            "credential_required": False,
            "supported_inputs": ["sitemap_xml", "url_list", "html_snapshots"],
            "automatic_page_actions": False,
        },
        "image_generation": {
            "implemented": True,
            "providers": {
                "openai": {
                    "environment_variable": "OPENAI_API_KEY",
                    "credential_present": openai_present,
                },
                "gemini": {
                    "environment_variable": "GEMINI_API_KEY",
                    "credential_present": gemini_present,
                },
            },
            "credential_value_read": False,
            "requires_api_verification": openai_present or gemini_present,
        },
        "indexnow": {
            "implemented": True,
            "environment_variables": ["INDEXNOW_KEY", "SITE_URL"],
            "indexnow_key_present": indexnow_key_present,
            "site_url_present": site_url_present,
            "credential_value_read": False,
            "requires_live_url_and_key_file_verification": indexnow_key_present and site_url_present,
        },
        "wechat_official_account_publishing": {
            "implemented": False,
            "method_boundary_documented": True,
            "environment_variables": ["WECHAT_OFFICIAL_APP_ID", "WECHAT_OFFICIAL_APP_SECRET"],
            "app_id_present": wechat_app_id_present,
            "app_secret_present": wechat_app_secret_present,
            "credential_value_read": False,
            "note": "Publishing Client is not implemented; human-assisted publishing remains the default.",
        },
        "xiaohongshu_publishing": {
            "implemented": False,
            "method_boundary_documented": True,
            "credential_required_for_default_handoff": False,
            "note": "Default is human-assisted publishing; do not assume ordinary notes can be server-side auto-published.",
        },
        "note": "Credential presence is not proof of authorization or usable data.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
