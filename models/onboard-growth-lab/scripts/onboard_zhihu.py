#!/usr/bin/env python3
"""Onboard Zhihu through Growth Lab without storing credentials."""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ZHIHU_SCRIPTS = ROOT / "collectors" / "zhihu-open-platform" / "scripts"
sys.path.insert(0, str(ZHIHU_SCRIPTS))

import zhihu_cli as official  # noqa: E402


ONBOARD = Path(__file__).relative_to(ROOT)


def action(next_action: str, command: str | None = None) -> dict[str, Any]:
    return {"next_action": next_action, "command": command}


def status(binary: str | None) -> dict[str, Any]:
    payload = official.status(binary)
    if not payload.get("installed"):
        return {
            **payload,
            "capability": "zhihu-content-collection",
            "readiness": "missing-cli",
            "action": action(
                "request_install_consent",
                f"python3 {ONBOARD} install --yes",
            ),
        }
    if not payload.get("compatible"):
        return {
            **payload,
            "capability": "zhihu-content-collection",
            "readiness": "incompatible-cli",
            "action": action(
                "request_cli_upgrade_consent",
                f"python3 {ONBOARD} install --yes",
            ),
        }
    auth = payload.get("auth") if isinstance(payload.get("auth"), dict) else {}
    if not auth.get("configured"):
        return {
            **payload,
            "capability": "zhihu-content-collection",
            "readiness": "needs-access-secret",
            "action": action(
                "request_access_secret",
                f"python3 {ONBOARD} auth",
            ),
        }
    return {
        **payload,
        "capability": "zhihu-content-collection",
        "readiness": "ready-to-verify",
        "action": action(
            "run_minimal_content_read",
            f'python3 {ONBOARD} verify --query "<真实研究查询>" --yes',
        ),
    }


def install(*, confirmed: bool, force: bool) -> dict[str, Any]:
    if not confirmed:
        raise official.ZhihuCliError(
            "CONFIRMATION_REQUIRED",
            "Pass --yes after the user approves installation of Zhihu's official CLI",
        )
    installed = official.install_cli(force=force)
    return {
        "ok": True,
        "capability": "zhihu-content-collection",
        "installation": installed,
        "status": status(installed["binary_path"]),
    }


def configure_auth(binary_path: str | None) -> dict[str, Any]:
    binary = official.resolve_binary(binary_path)
    if sys.stdin.isatty():
        secret = getpass.getpass("Zhihu Access Secret: ")
    else:
        secret = sys.stdin.readline()
    if not secret.strip():
        raise official.ZhihuCliError("AUTH_REQUIRED", "Access Secret input was empty")
    try:
        result = official.run_binary(
            binary,
            ["auth", "set", "--secret-stdin"],
            stdin_text=secret.strip(),
            timeout=30,
        )
    finally:
        del secret
    return {
        "ok": True,
        "capability": "zhihu-content-collection",
        "auth": official.sanitized_auth_status(result),
        "status": status(str(binary)),
    }


def verify(
    *,
    binary_path: str | None,
    confirmed: bool,
    query: str | None,
    hot: bool,
) -> dict[str, Any]:
    if not confirmed:
        raise official.ZhihuCliError(
            "CONFIRMATION_REQUIRED",
            "Pass --yes after the user approves the online verification request",
        )
    if query is not None and not query.strip():
        raise official.ZhihuCliError("INVALID_ARGUMENTS", "Verification query must not be empty")
    binary = official.resolve_binary(binary_path)
    official.run_binary(binary, ["auth", "status", "--verify"], timeout=30)

    if query:
        command = ["search", "zhihu", "--query", query, "--count", "1", "--pretty"]
        payload = official.run_binary(binary, command, timeout=30)
        data = official.api_data(payload, "Zhihu onboarding search")
        items = data.get("Items")
        read_type = "search"
        read_input = {"query": query, "count": 1}
    else:
        payload = official.run_binary(binary, ["hot", "--limit", "1", "--pretty"], timeout=30)
        data = official.api_data(payload, "Zhihu onboarding hot list")
        items = data.get("Items")
        read_type = "hot"
        read_input = {"limit": 1}

    if not isinstance(items, list) or not items:
        raise official.ZhihuCliError(
            "EMPTY_READ",
            "The verification request succeeded but returned no content",
            details={"verification_type": read_type, "input": read_input},
        )
    first = items[0] if isinstance(items[0], dict) else {}
    post_status = status(str(binary))
    post_status["readiness"] = "ready"
    post_status["action"] = None
    return {
        "ok": True,
        "capability": "zhihu-content-collection",
        "readiness": "ready",
        "auth_verified": True,
        "content_read": {
            "type": read_type,
            "input": read_input,
            "count": len(items),
            "title": first.get("Title"),
            "url": first.get("Url"),
        },
        "status": post_status,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Onboard Zhihu content collection through the official CLI."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Inspect readiness without changing state")
    status_parser.add_argument("--binary", help="Absolute path to the official zhihu-cli binary")

    install_parser = subparsers.add_parser("install", help="Install the official CLI")
    install_parser.add_argument("--yes", action="store_true", help="Confirm installation")
    install_parser.add_argument("--force", action="store_true", help="Reinstall current version")

    auth_parser = subparsers.add_parser(
        "auth",
        help="Read an Access Secret without echo and pass it to official CLI stdin",
    )
    auth_parser.add_argument("--binary", help="Absolute path to the official zhihu-cli binary")

    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify credentials and perform one minimal real content read",
    )
    verify_parser.add_argument("--binary", help="Absolute path to the official zhihu-cli binary")
    verify_parser.add_argument("--yes", action="store_true", help="Confirm online API calls")
    group = verify_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", help="Use one real research query for verification")
    group.add_argument("--hot", action="store_true", help="Read one hot-list item instead")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "status":
            result = status(args.binary)
        elif args.command == "install":
            result = install(confirmed=args.yes, force=args.force)
        elif args.command == "auth":
            result = configure_auth(args.binary)
        else:
            result = verify(
                binary_path=args.binary,
                confirmed=args.yes,
                query=args.query,
                hot=args.hot,
            )
        official.emit(result)
        return 0
    except official.ZhihuCliError as exc:
        official.emit(
            {
                "ok": False,
                "capability": "zhihu-content-collection",
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            }
        )
        return 2 if exc.code in {"AUTH_REQUIRED", "CONFIRMATION_REQUIRED"} else 1


if __name__ == "__main__":
    sys.exit(main())
