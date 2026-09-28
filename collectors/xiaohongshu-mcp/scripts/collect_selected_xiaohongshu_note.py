#!/usr/bin/env python3
"""Collect one user-selected Xiaohongshu note without persisting its access token."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
from pathlib import Path

import collect_xiaohongshu as collector


TOKEN_ENV = "XHS_SELECTED_XSEC_TOKEN"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect one explicitly selected Xiaohongshu note")
    parser.add_argument("--note-id", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--images", type=int, default=8)
    parser.add_argument("--timeout", type=float)
    return parser


def main() -> int:
    collector.load_repo_env()
    args = build_parser().parse_args()
    if args.images < 1 or args.images > 20:
        print("error: --images 必须在 1 到 20 之间", file=sys.stderr)
        return 2
    token = os.environ.pop(TOKEN_ENV, "").strip()
    if not token:
        print(f"error: 必须通过临时进程环境变量 {TOKEN_ENV} 提供所选笔记访问参数", file=sys.stderr)
        return 2

    endpoint = os.environ.get("XHS_MCP_ENDPOINT", collector.DEFAULT_ENDPOINT)
    timeout = args.timeout or float(os.environ.get("XHS_MCP_TIMEOUT_SECONDS", "60"))
    try:
        client = collector.XiaohongshuClient(endpoint, timeout)
        client.check_ready()
        note = client.detail(args.note_id, token)
        token = ""
        candidate, image_urls = collector.detail_to_candidate(note, args.note_id)
        image_files: list[str] = []
        for index, url in enumerate(image_urls[: args.images], start=1):
            data = collector.download_image(client.opener, url, client.timeout)
            extension = collector.image_extension(data)
            if extension == ".bin":
                print(f"warning: 图片 {index} 格式未知，已跳过", file=sys.stderr)
                continue
            image_path = args.out_dir / "selected-note-images" / f"{index:02d}{extension}"
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(data)
            image_files.append(image_path.relative_to(args.out_dir).as_posix())
        payload = {
            "schema_version": 1,
            "platform": "xiaohongshu",
            "selection": "explicitly selected by user",
            "access_mode": "authorized read-only detail request via local xiaohongshu-mcp",
            "note_id": candidate["note_id"],
            "public_url": f"https://www.xiaohongshu.com/explore/{candidate['note_id']}",
            "title": candidate["title"],
            "description": candidate["description"],
            "note_type": candidate["note_type"],
            "author": candidate["author"],
            "visible_engagement": candidate["visible_engagement"],
            "image_files": image_files,
            "privacy": "access tokens, signed image URLs, cookies, avatars, and raw response fields omitted",
        }
        collector.write_json(args.out_dir / "selected-note.json", payload)
    except (collector.CollectorError, OSError, ValueError, urllib.error.URLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    finally:
        token = ""
        os.environ.pop(TOKEN_ENV, None)

    print(json.dumps({"output": str(args.out_dir / 'selected-note.json'), "images": len(image_files)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
