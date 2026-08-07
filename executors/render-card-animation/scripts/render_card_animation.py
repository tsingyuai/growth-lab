#!/usr/bin/env python3
"""Render a local HTML card animation to a validated MP4 with Playwright."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any

from playwright.sync_api import sync_playwright


class AnimationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ffmpeg_executable(explicit: str | None = None) -> str:
    for candidate in (explicit, os.environ.get("FFMPEG_BINARY"), shutil.which("ffmpeg")):
        if candidate and Path(candidate).expanduser().is_file():
            return str(Path(candidate).expanduser().resolve())
    try:
        import imageio_ffmpeg

        candidate = imageio_ffmpeg.get_ffmpeg_exe()
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    except (ImportError, RuntimeError):
        pass
    raise AnimationError("未找到 FFmpeg；请设置 FFMPEG_BINARY。")


def browser_executable(explicit: str | None = None) -> str:
    candidates = [
        explicit,
        os.environ.get("CHROME_BINARY"),
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).expanduser().is_file():
            return str(Path(candidate).expanduser().resolve())
    raise AnimationError("未找到可用的 Chrome/Edge 浏览器。")


def inspect_video(ffmpeg: str, video: Path) -> dict[str, Any]:
    decode = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(video), "-map", "0:v:0", "-f", "null", "-"],
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    if decode.returncode != 0:
        raise AnimationError(f"动画视频无法完整解码：{decode.stderr.strip()}")
    probe = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(video)], capture_output=True, text=True, timeout=30, check=False
    )
    text = probe.stderr + probe.stdout
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    video_line = next((line for line in text.splitlines() if "Video:" in line), "")
    size_match = re.search(r"(?<![\d.])(\d{2,5})x(\d{2,5})(?![\d.])", video_line)
    fps_match = re.search(r"([\d.]+)\s+fps", video_line)
    if not duration_match or not size_match:
        raise AnimationError("无法读取动画视频时长或分辨率。")
    hours, minutes, seconds = duration_match.groups()
    duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    return {
        "duration_seconds": round(duration, 3),
        "width": int(size_match.group(1)),
        "height": int(size_match.group(2)),
        "fps": float(fps_match.group(1)) if fps_match else 0.0,
        "has_audio": "Audio:" in text,
    }


def render(args: argparse.Namespace) -> dict[str, Any]:
    html = Path(args.html).expanduser().resolve()
    if not html.is_file() or html.suffix.lower() != ".html":
        raise AnimationError("--html 必须指向本地 HTML 文件。")
    if not 1 <= args.duration <= 60:
        raise AnimationError("动画时长必须在 1 到 60 秒之间。")
    if args.width < 320 or args.height < 320:
        raise AnimationError("动画画布尺寸过小。")
    assets = [Path(item).expanduser().resolve() for item in args.asset]
    for asset in assets:
        if not asset.is_file():
            raise AnimationError(f"动画素材不存在：{asset}")
    output = Path(args.out).expanduser().resolve()
    if output.suffix.lower() != ".mp4":
        raise AnimationError("--out 必须使用 .mp4 扩展名。")
    if output.exists() and not args.force:
        raise AnimationError(f"输出已存在：{output}；如需替换请传入 --force。")
    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = ffmpeg_executable(args.ffmpeg)
    browser = browser_executable(args.browser)
    started_at = datetime.now(timezone.utc)

    with tempfile.TemporaryDirectory(prefix="growth-lab-animation-") as temp:
        temp_dir = Path(temp)
        with sync_playwright() as playwright:
            instance = playwright.chromium.launch(
                executable_path=browser,
                headless=True,
                args=[
                    "--disable-background-networking",
                    "--disable-component-update",
                    "--disable-default-apps",
                    "--disable-extensions",
                    "--disable-sync",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
            )
            context = instance.new_context(
                viewport={"width": args.width, "height": args.height},
                device_scale_factor=1,
                record_video_dir=str(temp_dir),
                record_video_size={"width": args.width, "height": args.height},
            )
            page = context.new_page()
            page.goto(html.as_uri(), wait_until="load", timeout=30_000)
            page.wait_for_function("window.__ANIMATION_READY__ === true", timeout=15_000)
            page.evaluate("window.__startAnimation()")
            page.wait_for_timeout(int(args.duration * 1000))
            video = page.video
            page.close()
            context.close()
            instance.close()
            if video is None:
                raise AnimationError("Playwright 未返回动画视频。")
            source_video = Path(video.path())
            if not source_video.is_file():
                raise AnimationError("Playwright 动画视频文件不存在。")

        partial = output.with_name(f".{output.stem}.partial.mp4")
        partial.unlink(missing_ok=True)
        command = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source_video),
            "-t",
            f"{args.duration:.3f}",
            "-an",
            "-vf",
            f"scale={args.width}:{args.height}:flags=lanczos,format=yuv420p",
            "-r",
            str(args.fps),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-movflags",
            "+faststart",
            str(partial),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=240, check=False)
        if result.returncode != 0 or not partial.is_file():
            partial.unlink(missing_ok=True)
            raise AnimationError(f"FFmpeg 动画转码失败：{result.stderr.strip()}")
        metadata = inspect_video(ffmpeg, partial)
        if metadata["duration_seconds"] < args.duration - 0.5:
            partial.unlink(missing_ok=True)
            raise AnimationError("动画视频明显短于请求时长。")
        if (metadata["width"], metadata["height"]) != (args.width, args.height):
            partial.unlink(missing_ok=True)
            raise AnimationError("动画视频尺寸与请求画布不一致。")
        if output.exists():
            output.unlink()
        partial.replace(output)

    manifest_path = (
        Path(args.manifest).expanduser().resolve()
        if args.manifest
        else output.with_name(f"{output.stem}.animation-manifest.json")
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    def relative_or_absolute(path: Path) -> str:
        try:
            return path.relative_to(manifest_path.parent).as_posix()
        except ValueError:
            return str(path)

    manifest = {
        "schema_version": 1,
        "status": "rendered-validated",
        "source": {
            "html_file": relative_or_absolute(html),
            "html_sha256": sha256_file(html),
            "assets": [
                {"file": relative_or_absolute(asset), "sha256": sha256_file(asset)} for asset in assets
            ],
        },
        "render": {
            "started_at": started_at.isoformat(),
            "engine": "playwright-chromium",
            "browser_executable": Path(browser).name,
            "width": args.width,
            "height": args.height,
            "fps": args.fps,
            "requested_duration_seconds": args.duration,
            "network_disabled_by_policy": True,
        },
        "output": {
            "file": relative_or_absolute(output),
            "sha256": sha256_file(output),
            **metadata,
        },
        "publication_authorized": False,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"video": str(output), "manifest": str(manifest_path), **manifest}


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a local HTML card animation")
    parser.add_argument("--html", required=True)
    parser.add_argument("--asset", action="append", default=[])
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    parser.add_argument("--fps", type=int, choices=[24, 25, 30], default=30)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--browser")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    print(json.dumps(render(args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AnimationError as exc:
        print(f"错误：{exc}", file=os.sys.stderr)
        raise SystemExit(1)
