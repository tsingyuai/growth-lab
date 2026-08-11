#!/usr/bin/env python3
"""Capture a bounded Windows desktop, region, or visible window with FFmpeg."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any


MAX_DURATION_SECONDS = 300.0


class CaptureError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ffmpeg_executable(explicit: str | None = None) -> str:
    candidates = [explicit, os.environ.get("FFMPEG_BINARY"), shutil.which("ffmpeg")]
    for candidate in candidates:
        if candidate and Path(candidate).expanduser().is_file():
            return str(Path(candidate).expanduser().resolve())
    try:
        import imageio_ffmpeg

        candidate = imageio_ffmpeg.get_ffmpeg_exe()
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    except (ImportError, RuntimeError):
        pass
    raise CaptureError(
        "未找到 FFmpeg。请设置 FFMPEG_BINARY，或使用 social-video-venv 中的 Python 运行。"
    )


def ffmpeg_capabilities(ffmpeg: str) -> dict[str, Any]:
    version = subprocess.run(
        [ffmpeg, "-version"], capture_output=True, text=True, timeout=15, check=False
    )
    formats = subprocess.run(
        [ffmpeg, "-hide_banner", "-formats"], capture_output=True, text=True, timeout=15, check=False
    )
    encoders = subprocess.run(
        [ffmpeg, "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=15, check=False
    )
    version_line = (version.stdout or version.stderr).splitlines()
    return {
        "available": version.returncode == 0,
        "path": ffmpeg,
        "version": version_line[0].strip() if version_line else "unknown",
        "gdigrab": "gdigrab" in (formats.stdout + formats.stderr),
        "libx264": "libx264" in (encoders.stdout + encoders.stderr),
    }


def visible_windows() -> list[dict[str, Any]]:
    if os.name != "nt":
        raise CaptureError("窗口枚举当前仅支持 Windows。")
    user32 = ctypes.windll.user32
    windows: list[dict[str, Any]] = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value.strip()
        if title:
            windows.append({"hwnd": int(hwnd), "title": title})
        return True

    callback_ref = callback_type(callback)
    if not user32.EnumWindows(callback_ref, 0):
        raise CaptureError("无法枚举当前可见窗口。")
    return sorted(windows, key=lambda item: item["title"].casefold())


def parse_region(value: str) -> tuple[int, int, int, int]:
    try:
        x, y, width, height = (int(part.strip()) for part in value.split(","))
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("区域格式必须是 x,y,width,height。") from exc
    if x < 0 or y < 0 or width < 64 or height < 64:
        raise argparse.ArgumentTypeError("区域坐标必须非负，宽高至少为 64。")
    return x, y, width, height


def build_capture_command(
    ffmpeg: str,
    output: Path,
    duration: float,
    framerate: int,
    window_title: str | None = None,
    region: tuple[int, int, int, int] | None = None,
    draw_mouse: bool = True,
) -> list[str]:
    if not 1.0 <= duration <= MAX_DURATION_SECONDS:
        raise CaptureError(f"录制时长必须在 1 到 {int(MAX_DURATION_SECONDS)} 秒之间。")
    if framerate not in {24, 25, 30, 60}:
        raise CaptureError("帧率仅支持 24、25、30 或 60。")
    if window_title and region:
        raise CaptureError("指定窗口和屏幕区域不能同时使用。")
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "warning",
        "-f",
        "gdigrab",
        "-framerate",
        str(framerate),
        "-draw_mouse",
        "1" if draw_mouse else "0",
    ]
    if region:
        x, y, width, height = region
        command += ["-offset_x", str(x), "-offset_y", str(y), "-video_size", f"{width}x{height}"]
    command += [
        "-i",
        f"title={window_title}" if window_title else "desktop",
        "-t",
        f"{duration:.3f}",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-vf",
        "crop=trunc(iw/2)*2:trunc(ih/2)*2",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    return command


def inspect_video(ffmpeg: str, video: Path) -> dict[str, Any]:
    decode = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(video), "-map", "0:v:0", "-f", "null", "-"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if decode.returncode != 0:
        raise CaptureError(f"录屏文件无法完整解码：{decode.stderr.strip()}")
    probe = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(video)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    text = probe.stderr + probe.stdout
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    video_line = next((line for line in text.splitlines() if "Video:" in line), "")
    size_match = re.search(r"(?<![\d.])(\d{2,5})x(\d{2,5})(?![\d.])", video_line)
    fps_match = re.search(r"([\d.]+)\s+fps", video_line)
    if not duration_match or not size_match:
        raise CaptureError("无法读取录屏时长或分辨率。")
    hours, minutes, seconds = duration_match.groups()
    duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    return {
        "duration_seconds": round(duration, 3),
        "width": int(size_match.group(1)),
        "height": int(size_match.group(2)),
        "fps": float(fps_match.group(1)) if fps_match else 0.0,
        "has_audio": "Audio:" in text,
    }


def wait_for_capture_start(
    process: subprocess.Popen[str],
    partial: Path,
    ready_file: Path | None,
    started_at: datetime,
    timeout: float = 10.0,
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise CaptureError("FFmpeg 在写入首帧前退出。")
        if partial.is_file() and partial.stat().st_size > 0:
            if ready_file:
                ready_file.parent.mkdir(parents=True, exist_ok=True)
                ready_file.write_text(
                    json.dumps(
                        {
                            "status": "capture-started",
                            "pid": process.pid,
                            "started_at": started_at.isoformat(),
                            "partial_file": str(partial),
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
            return
        time.sleep(0.05)
    raise CaptureError("FFmpeg 启动后 10 秒内没有写入首帧。")


def record(args: argparse.Namespace) -> dict[str, Any]:
    if os.name != "nt":
        raise CaptureError("真实屏幕录制当前仅支持 Windows。")
    if not args.confirm_capture:
        raise CaptureError("录屏前必须传入 --confirm-capture，确认目标范围内没有密码、通知或无关隐私。")
    if not args.window_title and not args.region and not args.confirm_full_desktop:
        raise CaptureError("录制整个桌面还必须传入 --confirm-full-desktop。")
    if args.window_title:
        titles = {item["title"] for item in visible_windows()}
        if args.window_title not in titles:
            raise CaptureError("未找到标题完全匹配的可见窗口；请先运行 list-windows。")

    destination = Path(args.out).expanduser().resolve()
    if destination.suffix.lower() != ".mp4":
        raise CaptureError("输出文件必须使用 .mp4 扩展名。")
    if destination.exists() and not args.force:
        raise CaptureError(f"输出已存在：{destination}；如需替换请传入 --force。")
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(f".{destination.stem}.partial.mp4")
    partial.unlink(missing_ok=True)
    ready_file = Path(args.ready_file).expanduser().resolve() if args.ready_file else None
    if ready_file:
        ready_file.unlink(missing_ok=True)

    ffmpeg = ffmpeg_executable(args.ffmpeg)
    capabilities = ffmpeg_capabilities(ffmpeg)
    if not capabilities["available"] or not capabilities["gdigrab"] or not capabilities["libx264"]:
        raise CaptureError("FFmpeg 必须同时支持 gdigrab 和 libx264。")
    if args.countdown:
        for remaining in range(args.countdown, 0, -1):
            print(f"{remaining} 秒后开始录制…", flush=True)
            time.sleep(1)

    command = build_capture_command(
        ffmpeg,
        partial,
        args.duration,
        args.framerate,
        window_title=args.window_title,
        region=args.region,
        draw_mouse=not args.hide_mouse,
    )
    started_at = datetime.now(timezone.utc)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        wait_for_capture_start(process, partial, ready_file, started_at)
        stdout, stderr = process.communicate(timeout=args.duration + 90)
    except subprocess.TimeoutExpired as exc:
        process.kill()
        process.communicate()
        partial.unlink(missing_ok=True)
        if ready_file:
            ready_file.unlink(missing_ok=True)
        raise CaptureError("FFmpeg 录屏超时。") from exc
    except CaptureError:
        process.kill()
        process.communicate()
        partial.unlink(missing_ok=True)
        if ready_file:
            ready_file.unlink(missing_ok=True)
        raise
    if process.returncode != 0 or not partial.is_file() or partial.stat().st_size == 0:
        partial.unlink(missing_ok=True)
        if ready_file:
            ready_file.unlink(missing_ok=True)
        detail = (stderr or stdout).strip()
        raise CaptureError(f"FFmpeg 录屏失败：{detail[-2000:]}")
    metadata = inspect_video(ffmpeg, partial)
    if metadata["duration_seconds"] < max(0.5, args.duration - 1.0):
        partial.unlink(missing_ok=True)
        raise CaptureError("录屏成片明显短于请求时长。")
    if destination.exists():
        destination.unlink()
    partial.replace(destination)

    if args.window_title:
        source = {"kind": "window", "window_title": args.window_title}
    elif args.region:
        x, y, width, height = args.region
        source = {"kind": "region", "x": x, "y": y, "width": width, "height": height}
    else:
        source = {"kind": "desktop"}
    manifest_path = (
        Path(args.manifest).expanduser().resolve()
        if args.manifest
        else destination.with_name(f"{destination.stem}.capture-manifest.json")
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        output_file = destination.relative_to(manifest_path.parent).as_posix()
    except ValueError:
        output_file = str(destination)
    manifest = {
        "schema_version": 1,
        "status": "recorded-validated",
        "source": source,
        "capture": {
            "started_at": started_at.isoformat(),
            "requested_duration_seconds": args.duration,
            "draw_mouse": not args.hide_mouse,
            "scope_confirmed": True,
            "human_privacy_review_required": True,
        },
        "renderer": {
            "name": "ffmpeg-gdigrab",
            "ffmpeg_version": capabilities["version"],
            "external_binary": True,
        },
        "output": {
            "file": output_file,
            "sha256": sha256_file(destination),
            **metadata,
        },
        "publication_authorized": False,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"video": str(destination), "manifest": str(manifest_path), **manifest}


def main() -> int:
    parser = argparse.ArgumentParser(description="Growth Lab Windows screen recorder")
    parser.add_argument("--ffmpeg", help="FFmpeg executable; otherwise use FFMPEG_BINARY or imageio-ffmpeg")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Check FFmpeg screen-capture capabilities")
    list_parser = subparsers.add_parser("list-windows", help="List visible window titles")
    list_parser.add_argument("--contains", default="", help="Case-insensitive title filter")

    record_parser = subparsers.add_parser("record", help="Record a bounded MP4")
    record_parser.add_argument("--out", required=True)
    record_parser.add_argument("--manifest")
    record_parser.add_argument("--ready-file", help="Write a JSON signal after FFmpeg starts writing frames")
    source = record_parser.add_mutually_exclusive_group()
    source.add_argument("--window-title")
    source.add_argument("--region", type=parse_region, metavar="X,Y,WIDTH,HEIGHT")
    record_parser.add_argument("--duration", type=float, required=True)
    record_parser.add_argument("--framerate", type=int, default=30)
    record_parser.add_argument("--countdown", type=int, choices=range(0, 11), default=3)
    record_parser.add_argument("--hide-mouse", action="store_true")
    record_parser.add_argument("--confirm-capture", action="store_true")
    record_parser.add_argument("--confirm-full-desktop", action="store_true")
    record_parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.command == "check":
        ffmpeg = ffmpeg_executable(args.ffmpeg)
        result = {"platform": sys.platform, **ffmpeg_capabilities(ffmpeg)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["available"] and result["gdigrab"] and result["libx264"] else 1
    if args.command == "list-windows":
        needle = args.contains.casefold()
        result = [item for item in visible_windows() if needle in item["title"].casefold()]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(record(args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CaptureError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
