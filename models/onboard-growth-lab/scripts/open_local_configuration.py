#!/usr/bin/env python3
"""Create the ignored local configuration when needed and open it for the user."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable


ROOT = Path(__file__).resolve().parents[3]


def ensure_local_env(root: Path) -> tuple[Path, bool]:
    target = root / ".env.local"
    if target.is_file():
        return target, False
    example = root / ".env.example"
    if not example.is_file():
        raise FileNotFoundError("仓库缺少 .env.example，无法创建本地配置")
    shutil.copyfile(example, target)
    return target, True


def editor_command(path: Path, system: str) -> list[str]:
    if system == "Windows":
        return ["notepad.exe", str(path)]
    if system == "Darwin":
        return ["open", str(path)]
    return ["xdg-open", str(path)]


def open_editor(
    path: Path,
    system: str,
    launcher: Callable[..., object] = subprocess.Popen,
) -> None:
    launcher(
        editor_command(path, system),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        path, created = ensure_local_env(ROOT)
        if not args.check_only:
            open_editor(path, platform.system())
    except (OSError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "ready" if args.check_only else "opened",
                "file": ".env.local",
                "created": created,
                "git_ignored_required": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
