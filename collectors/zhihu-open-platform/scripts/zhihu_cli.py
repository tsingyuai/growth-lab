#!/usr/bin/env python3
"""Install, inspect, and collect through Zhihu's official CLI."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_URL = "https://developer-cdn.zhihu.com/zhihu-cli/releases/stable/manifest.json"
OFFICIAL_HOST = "developer-cdn.zhihu.com"
MIN_CLI_VERSION = "0.6.1"
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
AUTH_ACTION_URL = "https://developer.zhihu.com/profile"


class ZhihuCliError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_json_output(text: str, context: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ZhihuCliError(
            "INVALID_CLI_OUTPUT",
            f"{context} did not return a JSON object",
            details={"line": exc.lineno, "column": exc.colno},
        ) from exc
    if not isinstance(payload, dict):
        raise ZhihuCliError("INVALID_CLI_OUTPUT", f"{context} returned non-object JSON")
    return payload


def run_binary(
    binary: Path,
    args: list[str],
    *,
    stdin_text: str | None = None,
    timeout: int = 90,
) -> dict[str, Any]:
    command = [str(binary), *args]
    try:
        completed = subprocess.run(
            command,
            input=stdin_text,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ZhihuCliError("CLI_NOT_INSTALLED", f"CLI binary not found: {binary}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ZhihuCliError(
            "CLI_TIMEOUT",
            f"CLI command timed out after {timeout}s: {' '.join(args[:3])}",
        ) from exc

    if completed.returncode != 0:
        try:
            error_payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            error_payload = None
        raise ZhihuCliError(
            "CLI_COMMAND_FAILED",
            f"CLI exited with status {completed.returncode}",
            details={
                "command": " ".join(args[:3]),
                "stdout": error_payload,
                "stderr": completed.stderr.strip()[-4000:],
            },
        )
    return parse_json_output(completed.stdout, "CLI command")


def cli_home() -> Path:
    configured = os.environ.get("ZHIHU_CLI_HOME")
    if configured:
        return Path(configured).expanduser()
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "zhihu-cli"
    if system == "Linux":
        data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        if not data_home.is_absolute():
            raise ZhihuCliError("INVALID_CONFIGURATION", "XDG_DATA_HOME must be absolute")
        return data_home / "zhihu-cli"
    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise ZhihuCliError("INVALID_CONFIGURATION", "LOCALAPPDATA is required")
        return Path(local_app_data) / "ZhihuCLI"
    raise ZhihuCliError("UNSUPPORTED_PLATFORM", f"Unsupported platform: {system}")


def binary_name() -> str:
    return "zhihu-cli.exe" if platform.system() == "Windows" else "zhihu-cli"


def resolve_binary(explicit: str | None) -> Path:
    configured = explicit or os.environ.get("ZHIHU_CLI_BIN")
    binary = Path(configured).expanduser() if configured else cli_home() / "current" / binary_name()
    if not binary.is_file():
        raise ZhihuCliError(
            "CLI_NOT_INSTALLED",
            "Zhihu official CLI is not installed at the expected path",
            details={"expected_binary": str(binary), "install_url": MANIFEST_URL},
        )
    if platform.system() != "Windows" and not os.access(binary, os.X_OK):
        raise ZhihuCliError("CLI_NOT_EXECUTABLE", f"CLI is not executable: {binary}")
    return binary.resolve()


def version_tuple(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z.-]+)?", value)
    if not match:
        raise ZhihuCliError("INVALID_VERSION", f"Invalid version: {value}")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def target_platform() -> str:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Darwin" and machine in {"arm64", "aarch64"}:
        return "darwin-arm64"
    if system == "Darwin" and machine in {"x86_64", "amd64"}:
        return "darwin-amd64"
    if system == "Linux" and machine in {"x86_64", "amd64"}:
        return "linux-amd64"
    if system == "Linux" and machine in {"arm64", "aarch64"}:
        return "linux-arm64"
    if system == "Windows" and machine in {"amd64", "x86_64"}:
        return "windows-amd64"
    raise ZhihuCliError(
        "UNSUPPORTED_PLATFORM",
        f"Unsupported platform: {system}/{machine}",
    )


def download_official(url: str, *, max_bytes: int) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
        raise ZhihuCliError("UNTRUSTED_DOWNLOAD", f"Refusing non-official download: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "growth-lab-zhihu-collector/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        final_url = urllib.parse.urlparse(response.geturl())
        if final_url.scheme != "https" or final_url.hostname != OFFICIAL_HOST:
            raise ZhihuCliError("UNTRUSTED_DOWNLOAD", "Official download redirected off-host")
        length = response.headers.get("Content-Length")
        if length:
            try:
                declared_length = int(length)
            except ValueError as exc:
                raise ZhihuCliError("INVALID_DOWNLOAD", "Invalid Content-Length header") from exc
            if declared_length > max_bytes:
                raise ZhihuCliError("DOWNLOAD_TOO_LARGE", f"Download exceeds {max_bytes} bytes")
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ZhihuCliError("DOWNLOAD_TOO_LARGE", f"Download exceeds {max_bytes} bytes")
    return data


def extract_binary(archive: bytes, platform_id: str) -> bytes:
    expected = binary_name()
    if platform_id == "windows-amd64":
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            names = [entry.filename for entry in bundle.infolist() if not entry.is_dir()]
            if names != [expected]:
                raise ZhihuCliError("INVALID_ARCHIVE", "Official ZIP must contain only zhihu-cli.exe")
            info = bundle.getinfo(expected)
            if info.file_size > MAX_ARCHIVE_BYTES:
                raise ZhihuCliError("INVALID_ARCHIVE", "Official binary is too large")
            return bundle.read(info)

    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        members = bundle.getmembers()
        if len(members) != 1 or members[0].name != expected or not members[0].isfile():
            raise ZhihuCliError("INVALID_ARCHIVE", "Official archive must contain one binary")
        member = members[0]
        if member.size > MAX_ARCHIVE_BYTES:
            raise ZhihuCliError("INVALID_ARCHIVE", "Official binary is too large")
        extracted = bundle.extractfile(member)
        if extracted is None:
            raise ZhihuCliError("INVALID_ARCHIVE", "Unable to read official binary")
        return extracted.read()


def read_cli_version(binary: Path) -> str:
    payload = run_binary(binary, ["version"], timeout=20)
    version = payload.get("version")
    if not isinstance(version, str):
        raise ZhihuCliError("INVALID_CLI_OUTPUT", "CLI version response lacks version")
    version_tuple(version)
    return version


def install_cli(*, force: bool = False) -> dict[str, Any]:
    platform_id = target_platform()
    manifest_bytes = download_official(MANIFEST_URL, max_bytes=MAX_MANIFEST_BYTES)
    manifest = parse_json_output(manifest_bytes.decode("utf-8"), "release manifest")
    if manifest.get("schema_version") != 1:
        raise ZhihuCliError("INVALID_MANIFEST", "Unsupported release manifest schema")

    cli = manifest.get("cli")
    artifacts = cli.get("artifacts") if isinstance(cli, dict) else None
    artifact = artifacts.get(platform_id) if isinstance(artifacts, dict) else None
    if not isinstance(artifact, dict):
        raise ZhihuCliError("INVALID_MANIFEST", f"No official artifact for {platform_id}")

    latest_version = cli.get("latest_version")
    if not isinstance(latest_version, str):
        raise ZhihuCliError("INVALID_MANIFEST", "Release manifest lacks latest version")
    if version_tuple(latest_version) < version_tuple(MIN_CLI_VERSION):
        raise ZhihuCliError("INCOMPATIBLE_VERSION", "Latest official CLI is too old")

    destination_home = cli_home()
    current_binary = destination_home / "current" / binary_name()
    if current_binary.is_file() and not force:
        try:
            current_version = read_cli_version(current_binary)
        except ZhihuCliError:
            current_version = ""
        if current_version == latest_version:
            return {
                "ok": True,
                "installed": True,
                "reused": True,
                "version": current_version,
                "binary_path": str(current_binary.resolve()),
            }

    artifact_url = artifact.get("url")
    expected_sha = artifact.get("sha256")
    expected_size = artifact.get("size")
    if not isinstance(artifact_url, str) or not isinstance(expected_sha, str):
        raise ZhihuCliError("INVALID_MANIFEST", "Release artifact is incomplete")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        raise ZhihuCliError("INVALID_MANIFEST", "Release artifact SHA-256 is invalid")
    if not isinstance(expected_size, int) or not 0 < expected_size <= MAX_ARCHIVE_BYTES:
        raise ZhihuCliError("INVALID_MANIFEST", "Release artifact size is invalid")

    archive = download_official(artifact_url, max_bytes=MAX_ARCHIVE_BYTES)
    if len(archive) != expected_size:
        raise ZhihuCliError("CHECKSUM_MISMATCH", "Official artifact size does not match manifest")
    actual_sha = hashlib.sha256(archive).hexdigest()
    if actual_sha != expected_sha:
        raise ZhihuCliError("CHECKSUM_MISMATCH", "Official artifact SHA-256 does not match manifest")
    binary_bytes = extract_binary(archive, platform_id)

    destination_home.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(destination_home, stat.S_IRWXU)
    except OSError:
        pass
    version_dir = destination_home / "versions" / latest_version
    current_dir = destination_home / "current"
    version_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    current_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    staged = version_dir / f".{binary_name()}.new.{os.getpid()}"
    staged.write_bytes(binary_bytes)
    if platform.system() != "Windows":
        staged.chmod(0o755)
    staged_version = read_cli_version(staged)
    if staged_version != latest_version:
        staged.unlink(missing_ok=True)
        raise ZhihuCliError("INVALID_BINARY", "Downloaded CLI reports an unexpected version")

    installed = version_dir / binary_name()
    staged.replace(installed)
    staged_current = current_dir / f".{binary_name()}.new.{os.getpid()}"
    shutil.copy2(installed, staged_current)
    staged_current.replace(current_binary)

    return {
        "ok": True,
        "installed": True,
        "reused": False,
        "version": latest_version,
        "platform": platform_id,
        "binary_path": str(current_binary.resolve()),
    }


def sanitized_auth_status(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "configured": bool(payload.get("configured")),
        "source": payload.get("source"),
        "backend": payload.get("backend"),
        "last_verified_at": payload.get("last_verified_at"),
    }


def status(explicit_binary: str | None) -> dict[str, Any]:
    try:
        binary = resolve_binary(explicit_binary)
    except ZhihuCliError as exc:
        if exc.code != "CLI_NOT_INSTALLED":
            raise
        return {
            "ok": True,
            "installed": False,
            "next_action": "request_install_consent",
            "official_manifest": MANIFEST_URL,
            "error": {"code": exc.code, "message": exc.message},
        }

    version = read_cli_version(binary)
    capabilities = run_binary(binary, ["capabilities"], timeout=20)
    commands = capabilities.get("commands", [])
    command_names = [
        command.get("name")
        for command in commands
        if isinstance(command, dict) and isinstance(command.get("name"), str)
    ]
    auth = run_binary(binary, ["auth", "status"], timeout=20)
    auth_status = sanitized_auth_status(auth)
    compatible = version_tuple(version) >= version_tuple(MIN_CLI_VERSION)
    if not compatible:
        next_action = "request_cli_upgrade_consent"
    elif not auth_status["configured"]:
        next_action = "request_access_secret"
    else:
        next_action = "ready_unverified"
    return {
        "ok": True,
        "installed": True,
        "binary_path": str(binary),
        "version": version,
        "minimum_version": MIN_CLI_VERSION,
        "compatible": compatible,
        "auth": auth_status,
        "commands": command_names,
        "next_action": next_action,
    }


def safe_slug(value: str, limit: int = 48) -> str:
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", value).strip("-")
    return (slug or "query")[:limit]


def canonical_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    retained = [(key, item) for key, item in query if not key.lower().startswith("utm_")]
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), urllib.parse.urlencode(retained), "")
    )


def clean_summary(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def iso_from_epoch(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (OverflowError, OSError, ValueError):
        return None


def api_data(payload: dict[str, Any], label: str) -> dict[str, Any]:
    code = payload.get("Code", payload.get("code"))
    if code not in (None, 0, "0"):
        message = payload.get("Message", payload.get("message", "Open Platform error"))
        raise ZhihuCliError(
            "ZHIHU_API_ERROR",
            f"{label} failed: {message}",
            details={"code": code, "message": message},
        )
    data = payload.get("Data", payload.get("data"))
    return data if isinstance(data, dict) else payload


def normalize_item(
    item: dict[str, Any],
    *,
    kind: str,
    discovery: dict[str, str],
) -> dict[str, Any] | None:
    url = item.get("Url") or item.get("URL") or ""
    title = item.get("Title") or item.get("QuestionTitle") or ""
    if not isinstance(url, str) or not url:
        return None
    content_id = item.get("ContentID") or item.get("ContentToken")
    summary = clean_summary(item.get("ContentText") or item.get("Summary"))
    identity = str(content_id) if content_id else canonical_url(url)
    return {
        "identity": identity,
        "kind": kind,
        "content_id": str(content_id) if content_id else None,
        "content_type": item.get("ContentType"),
        "title": title if isinstance(title, str) else "",
        "author": item.get("AuthorName"),
        "summary": summary,
        "url": url,
        "canonical_url": canonical_url(url),
        "voteup_count": item.get("VoteUpCount"),
        "comment_count": item.get("CommentCount"),
        "authority_level": item.get("AuthorityLevel"),
        "edit_time": item.get("EditTime"),
        "edit_time_iso": iso_from_epoch(item.get("EditTime")),
        "thumbnail_url": item.get("ThumbnailUrl"),
        "discovery": [discovery],
    }


def merge_record(target: dict[str, Any], incoming: dict[str, Any]) -> None:
    existing = {
        json.dumps(value, ensure_ascii=False, sort_keys=True)
        for value in target.get("discovery", [])
    }
    for value in incoming.get("discovery", []):
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if encoded not in existing:
            target.setdefault("discovery", []).append(value)
            existing.add(encoded)
    for field in ("author", "summary", "voteup_count", "comment_count", "authority_level", "edit_time"):
        if target.get(field) in (None, "", 0) and incoming.get(field) not in (None, "", 0):
            target[field] = incoming[field]


def collect(args: argparse.Namespace) -> dict[str, Any]:
    if not args.query and not args.hot and not args.question_url:
        raise ZhihuCliError(
            "INVALID_ARGUMENTS",
            "Provide at least one --query, --hot, or --question-url",
        )
    if any(not query.strip() for query in args.query):
        raise ZhihuCliError("INVALID_ARGUMENTS", "Queries must not be empty")
    if any(not url.strip() for url in args.question_url):
        raise ZhihuCliError("INVALID_ARGUMENTS", "Question URLs must not be empty")
    if args.source == "zhihu" and args.count > 10:
        raise ZhihuCliError("INVALID_ARGUMENTS", "Zhihu search count must be between 1 and 10")
    if args.source == "global" and args.count > 20:
        raise ZhihuCliError("INVALID_ARGUMENTS", "Global search count must be between 1 and 20")
    if not 1 <= args.answer_limit <= 50:
        raise ZhihuCliError("INVALID_ARGUMENTS", "Answer limit must be between 1 and 50")
    if not 1 <= args.hot_limit <= 30:
        raise ZhihuCliError("INVALID_ARGUMENTS", "Hot-list limit must be between 1 and 30")

    binary = resolve_binary(args.binary)
    auth = sanitized_auth_status(run_binary(binary, ["auth", "status"], timeout=20))
    if not auth["configured"]:
        raise ZhihuCliError(
            "AUTH_REQUIRED",
            "Zhihu Access Secret is not configured",
            details={"action_url": AUTH_ACTION_URL},
        )

    output_dir = Path(args.output).expanduser().resolve()
    if output_dir.exists() and not output_dir.is_dir():
        raise ZhihuCliError(
            "INVALID_OUTPUT",
            "Output path exists and is not a directory",
            details={"output": str(output_dir)},
        )
    if output_dir.exists() and any(output_dir.iterdir()):
        if not args.overwrite:
            raise ZhihuCliError(
                "OUTPUT_NOT_EMPTY",
                "Output directory is not empty; choose a new path or pass --overwrite",
                details={"output": str(output_dir)},
            )
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)

    collected_at = utc_now()
    raw_files: list[str] = []
    failures: list[dict[str, Any]] = []
    records: dict[str, dict[str, Any]] = {}
    source_counts: dict[str, int] = {}
    sequence = 0

    def run_and_save(command: list[str], stem: str, timeout: int = 90) -> dict[str, Any]:
        nonlocal sequence
        sequence += 1
        payload = run_binary(binary, command, timeout=timeout)
        raw_path = raw_dir / f"{sequence:03d}-{safe_slug(stem)}.json"
        raw_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raw_files.append(str(raw_path.relative_to(output_dir)))
        return payload

    def add_items(items: Any, *, kind: str, discovery: dict[str, str]) -> None:
        if not isinstance(items, list):
            raise ZhihuCliError("INVALID_CLI_OUTPUT", f"{kind} response lacks Items")
        added = 0
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized = normalize_item(item, kind=kind, discovery=discovery)
            if normalized is None:
                continue
            identity = normalized.pop("identity")
            if identity in records:
                merge_record(records[identity], normalized)
            else:
                records[identity] = normalized
                added += 1
        source_counts[kind] = source_counts.get(kind, 0) + added

    try:
        for query in args.query:
            label = f"{args.source} search: {query}"
            command = [
                "search",
                args.source,
                "--query",
                query,
                "--count",
                str(args.count),
                "--pretty",
            ]
            payload = run_and_save(command, f"search-{args.source}-{query}")
            data = api_data(payload, label)
            add_items(
                data.get("Items"),
                kind="zhihu_content" if args.source == "zhihu" else "web_content",
                discovery={"source": "search", "query": query, "index": args.source},
            )

        if args.hot:
            command = ["hot", "--limit", str(args.hot_limit), "--pretty"]
            payload = run_and_save(command, "hot-list")
            data = api_data(payload, "hot list")
            add_items(
                data.get("Items"),
                kind="hot_topic",
                discovery={"source": "hot", "query": "", "index": "zhihu"},
            )

        for question_url in args.question_url:
            command = [
                "question",
                "answers",
                "--question-url",
                question_url,
                "--limit",
                str(args.answer_limit),
                "--pretty",
            ]
            payload = run_and_save(command, f"question-answers-{question_url}")
            data = api_data(payload, "question answers")
            add_items(
                data.get("Items"),
                kind="question_answer_summary",
                discovery={"source": "question_answers", "query": question_url, "index": "zhihu"},
            )
    except ZhihuCliError as exc:
        failures.append(
            {"code": exc.code, "message": exc.message, "details": exc.details}
        )
        raise
    finally:
        ordered_records = list(records.values())
        metadata = {
            "collected_at": collected_at,
            "binary_path": str(binary),
            "official_cli": True,
            "manifest_url": MANIFEST_URL,
            "arguments": {
                "queries": args.query,
                "source": args.source,
                "count": args.count,
                "hot": args.hot,
                "hot_limit": args.hot_limit,
                "question_urls": args.question_url,
                "answer_limit": args.answer_limit,
            },
            "record_count": len(ordered_records),
            "source_counts": source_counts,
            "raw_files": raw_files,
            "failures": failures,
            "data_boundary": {
                "search": "excerpt",
                "hot": "topic excerpt",
                "question_answers": "service-provided summary",
                "full_text": "own content only",
            },
        }
        (output_dir / "records.jsonl").write_text(
            "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in ordered_records),
            encoding="utf-8",
        )
        (output_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if not records:
        raise ZhihuCliError(
            "EMPTY_RESULT",
            "Official CLI returned no collectible records",
            details={"output": str(output_dir), "metadata": str(output_dir / "metadata.json")},
        )
    return {
        "ok": True,
        "record_count": len(records),
        "source_counts": source_counts,
        "output": str(output_dir),
        "records": str(output_dir / "records.jsonl"),
        "metadata": str(output_dir / "metadata.json"),
        "raw_files": raw_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Use Zhihu's official CLI to collect public content evidence."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Inspect the official CLI and auth state")
    status_parser.add_argument("--binary", help="Absolute path to the official zhihu-cli binary")

    install_parser = subparsers.add_parser(
        "install", help="Download and install the official CLI from Zhihu's CDN"
    )
    install_parser.add_argument("--yes", action="store_true", help="Confirm the side-effecting install")
    install_parser.add_argument("--force", action="store_true", help="Reinstall even when current")

    collect_parser = subparsers.add_parser(
        "collect", help="Collect search results, hot topics, and question answer summaries"
    )
    collect_parser.add_argument("--binary", help="Absolute path to the official zhihu-cli binary")
    collect_parser.add_argument("--query", action="append", default=[], help="Repeatable search query")
    collect_parser.add_argument(
        "--source",
        choices=("zhihu", "global"),
        default="zhihu",
        help="Search only Zhihu or the broader web",
    )
    collect_parser.add_argument("--count", type=int, default=10)
    collect_parser.add_argument("--hot", action="store_true")
    collect_parser.add_argument("--hot-limit", type=int, default=20)
    collect_parser.add_argument("--question-url", action="append", default=[])
    collect_parser.add_argument("--answer-limit", type=int, default=20)
    collect_parser.add_argument("--output", required=True)
    collect_parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "status":
            emit(status(args.binary))
            return 0
        if args.command == "install":
            if not args.yes:
                raise ZhihuCliError(
                    "CONFIRMATION_REQUIRED",
                    "Pass --yes after the user approves installation of Zhihu's official CLI",
                )
            emit(install_cli(force=args.force))
            return 0
        result = collect(args)
        emit(result)
        return 0
    except ZhihuCliError as exc:
        emit(
            {
                "ok": False,
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
