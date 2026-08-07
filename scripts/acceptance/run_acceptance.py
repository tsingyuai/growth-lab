#!/usr/bin/env python3
"""Run bounded Growth Lab acceptance tiers and persist a redacted report."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ROOT = ROOT / "workspaces" / "_acceptance"
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[A-Za-z0-9_-]{20,}"),
    re.compile(r'"(?:xsecToken|cookie|access_token|refresh_token)"\s*:', re.I),
)


@dataclass
class StepResult:
    name: str
    status: str
    duration_seconds: float
    returncode: int | None
    command: list[str]
    stdout_log: str
    stderr_log: str
    message: str = ""


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_run_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", value):
        raise ValueError("run ID 只能包含字母、数字、点、下划线和连字符")
    return value


def default_run_id() -> str:
    return "gl-acceptance-" + datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


def ensure_run_dir(root: Path, run_id: str) -> Path:
    root = root.resolve()
    run_dir = (root / safe_run_id(run_id)).resolve()
    run_dir.relative_to(root)
    if run_dir.exists() and any(run_dir.iterdir()):
        raise ValueError(f"验收目录已存在且非空：{run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def redacted_environment(environ: Mapping[str, str]) -> dict[str, str]:
    fields = (
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "XHS_MCP_BINARY",
        "XHS_MCP_LOGIN_BINARY",
        "XHS_MCP_COOKIES_PATH",
        "SOCIAL_PROXY_URL",
        "X_BROWSER_PROFILE_DIR",
    )
    result = {field: "present" if environ.get(field) else "missing" for field in fields}
    result["SOCIAL_PROXY_MODE"] = environ.get("SOCIAL_PROXY_MODE", "auto")
    return result


def run_step(
    run_dir: Path,
    name: str,
    command: Sequence[str],
    timeout: float,
    environ: Mapping[str, str] | None = None,
) -> StepResult:
    logs = run_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    stdout_path = logs / f"{name}.stdout.log"
    stderr_path = logs / f"{name}.stderr.log"
    started = time.monotonic()
    try:
        completed = subprocess.run(
            list(command),
            cwd=ROOT,
            env=dict(environ or os.environ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        status = "PASS" if completed.returncode == 0 else "FAIL"
        message = "" if completed.returncode == 0 else f"退出码 {completed.returncode}"
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        status = "FAIL"
        message = f"超过 {timeout:g} 秒超时"
        returncode = None
    return StepResult(
        name=name,
        status=status,
        duration_seconds=round(time.monotonic() - started, 3),
        returncode=returncode,
        command=[str(item) for item in command],
        stdout_log=stdout_path.relative_to(run_dir).as_posix(),
        stderr_log=stderr_path.relative_to(run_dir).as_posix(),
        message=message,
    )


def offline_steps() -> list[tuple[str, list[str], float]]:
    python_tests = [
        "collectors/inspect-seo-content-inventory/scripts/test_inspect_seo_content_inventory.py",
        "collectors/read-product-events/scripts/test_normalize_product_events.py",
        "collectors/read-social-platform-export/scripts/test_normalize_social_platform_export.py",
        "collectors/tests/test_official_social_api.py",
        "collectors/tests/test_social_browser_collectors.py",
        "collectors/x-browser/scripts/test_collect_x.py",
        "collectors/xiaohongshu-mcp/scripts/test_collect_xiaohongshu.py",
        "collectors/xiaohongshu-mcp/scripts/test_run_xiaohongshu.py",
        "collectors/xiaohongshu-mcp/scripts/test_minimal_continuous_flow.py",
        "collectors/xiaohongshu-mcp/scripts/test_validate_visual_reference_selection.py",
        "collectors/xiaohongshu-mcp/scripts/test_auto_select_visual_reference.py",
        "executors/generate-image/scripts/test_skill_contract.py",
        "executors/render-social-card-pack/scripts/test_validate_social_card_pack.py",
        "executors/render-social-card-pack/scripts/test_visual_helpers.py",
        "executors/render-social-card-pack/scripts/test_render_workflow_card_pack.py",
        "executors/render-social-video/scripts/test_render_video.py",
        "executors/render-social-video/scripts/test_synthesize_speech.py",
        "executors/render-social-video/scripts/test_seedance_provider.py",
        "executors/x-draft-stager/scripts/test_stage_x_draft.py",
        "executors/xhs-render-cards/scripts/test_skill_registration.py",
        "executors/xhs-render-cards/scripts/test_validate_social_card_pack.py",
        "models/onboard-growth-lab/scripts/test_check_configuration.py",
        "models/run-social-content-loop/scripts/test_validate_orchestration.py",
        "scripts/acceptance/test_run_acceptance.py",
    ]
    steps = [
        (f"python-{index:02d}", [sys.executable, path], 30.0)
        for index, path in enumerate(python_tests, start=1)
    ]
    steps.extend(
        [
            ("node-image-syntax", ["node", "--check", "executors/generate-image/generate-image.mjs"], 10.0),
            (
                "git-worktree-diff",
                ["git", "-c", f"safe.directory={ROOT}", "diff", "--check"],
                10.0,
            ),
            (
                "git-staged-diff",
                ["git", "-c", f"safe.directory={ROOT}", "diff", "--cached", "--check"],
                10.0,
            ),
        ]
    )
    return steps


def xhs_steps(args: argparse.Namespace, run_dir: Path) -> list[tuple[str, list[str], float]]:
    command = [
        sys.executable,
        "collectors/xiaohongshu-mcp/scripts/run_xiaohongshu.py",
        args.xhs_query,
        "--limit",
        str(args.limit),
        "--cover-pool",
        str(args.limit),
        "--out",
        str(run_dir / "xhs" / "xiaohongshu-search.json"),
        "--runtime-collection-timeout",
        str(args.platform_timeout),
    ]
    if args.allow_visible_login:
        command.append("--allow-visible-login")
    return [("xhs-smoke", command, args.platform_timeout + 120)]


def x_steps(args: argparse.Namespace, run_dir: Path, environ: Mapping[str, str]) -> list[tuple[str, list[str], float]]:
    configured = environ.get("X_BROWSER_PYTHON") or os.path.expandvars(
        r"%USERPROFILE%\.growth-lab\clients\x-browser-venv\Scripts\python.exe"
    )
    python = str(Path(configured))
    script = "collectors/x-browser/scripts/collect_x.py"
    return [
        ("x-preflight", [python, script, "--preflight"], 35.0),
        ("x-cdp-status", [python, script, "--cdp-status"], 15.0),
        (
            "x-smoke",
            [
                python,
                script,
                args.x_query,
                "--exclude",
                args.x_exclude,
                "--limit",
                str(args.limit),
                "--out",
                str(run_dir / "x" / "x-search.json"),
                "--attach",
            ],
            args.platform_timeout,
        ),
        (
            "x-exact-media",
            [
                python,
                script,
                args.x_query,
                "--exact",
                "--exclude",
                args.x_exclude,
                "--limit",
                str(args.limit),
                "--out",
                str(run_dir / "x" / "x-exact-search.json"),
                "--download-media",
                "--attach",
            ],
            args.platform_timeout,
        ),
    ]


def scan_for_secrets(run_dir: Path) -> list[str]:
    findings: list[str] = []
    for path in run_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".log", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(path.relative_to(run_dir).as_posix())
    return findings


def write_report(run_dir: Path, run_id: str, tiers: list[str], results: list[StepResult]) -> None:
    findings = scan_for_secrets(run_dir)
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    if findings:
        counts["FAIL"] = counts.get("FAIL", 0) + 1
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "tiers": tiers,
        "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "counts": counts,
        "sensitive_output_findings": findings,
        "steps": [asdict(item) for item in results],
    }
    write_json(run_dir / "run.json", payload)
    lines = [
        f"# Acceptance report: {run_id}",
        "",
        f"Tiers: {', '.join(tiers)}",
        f"Result: {'FAIL' if counts.get('FAIL') else 'PASS'}",
        "",
        "| Step | Status | Seconds | Message |",
        "|---|---|---:|---|",
    ]
    lines.extend(
        f"| {item.name} | {item.status} | {item.duration_seconds:.3f} | {item.message} |"
        for item in results
    )
    if findings:
        lines.extend(["", "Sensitive output findings: " + ", ".join(findings)])
    (run_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", action="append", choices=("offline", "xhs-smoke", "x-smoke"), required=True)
    parser.add_argument("--run-id", default=default_run_id())
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--platform-timeout", type=float, default=180)
    parser.add_argument("--allow-visible-login", action="store_true")
    parser.add_argument("--xhs-query", default="产品工具")
    parser.add_argument("--x-query", default="AI")
    parser.add_argument("--x-exclude", default="giveaway")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.limit < 1 or args.limit > 25:
        print("error: --limit 必须在 1 到 25 之间", file=sys.stderr)
        return 2
    if args.platform_timeout < 30 or args.platform_timeout > 900:
        print("error: --platform-timeout 必须在 30 到 900 秒之间", file=sys.stderr)
        return 2
    try:
        run_dir = ensure_run_dir(args.run_root, args.run_id)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    write_json(run_dir / "environment.json", redacted_environment(os.environ))
    results: list[StepResult] = []
    tiers = list(dict.fromkeys(args.tier))
    specifications: list[tuple[str, list[str], float]] = []
    if "offline" in tiers:
        specifications.extend(offline_steps())
    if "xhs-smoke" in tiers:
        specifications.extend(xhs_steps(args, run_dir))
    if "x-smoke" in tiers:
        specifications.extend(x_steps(args, run_dir, os.environ))
    for name, command, timeout in specifications:
        print(json.dumps({"status": "running", "step": name}, ensure_ascii=False), flush=True)
        result = run_step(run_dir, name, command, timeout)
        results.append(result)
        print(json.dumps({"status": result.status, "step": name}, ensure_ascii=False), flush=True)
        if result.status != "PASS":
            break
    write_report(run_dir, args.run_id, tiers, results)
    print(json.dumps({"run_dir": str(run_dir), "report": str(run_dir / "report.md")}, ensure_ascii=False))
    return 1 if any(item.status != "PASS" for item in results) or scan_for_secrets(run_dir) else 0


if __name__ == "__main__":
    raise SystemExit(main())
