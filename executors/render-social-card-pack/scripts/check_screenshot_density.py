#!/usr/bin/env python3
"""Reject screenshot crops dominated by empty space before card composition."""

import argparse
import json
from pathlib import Path

from PIL import Image


def measure(path: Path, dark_threshold: int) -> dict:
    image = Image.open(path).convert("L")
    width, height = image.size
    pixels = image.load()
    points = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if pixels[x, y] < dark_threshold
    ]
    if not points:
        return {
            "path": str(path),
            "size": [width, height],
            "content_bbox_coverage": 0.0,
            "largest_blank_band": 1.0,
        }

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    bbox_coverage = (
        (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    ) / (width * height)

    active_threshold = max(4, round(width * 0.004))
    longest = current = 0
    for y in range(height):
        active = sum(pixels[x, y] < dark_threshold for x in range(width)) >= active_threshold
        current = 0 if active else current + 1
        longest = max(longest, current)

    return {
        "path": str(path),
        "size": [width, height],
        "content_bbox_coverage": round(bbox_coverage, 3),
        "largest_blank_band": round(longest / height, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="检查截图裁切是否被大块空白占据。应在加圈注前运行。"
    )
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--min-coverage", type=float, default=0.80)
    parser.add_argument("--max-blank-band", type=float, default=0.20)
    parser.add_argument("--dark-threshold", type=int, default=242)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    report = {
        "rule": {
            "min_content_bbox_coverage": args.min_coverage,
            "max_largest_blank_band": args.max_blank_band,
        },
        "images": [],
    }
    for path in args.images:
        item = measure(path, args.dark_threshold)
        item["passed"] = (
            item["content_bbox_coverage"] >= args.min_coverage
            and item["largest_blank_band"] <= args.max_blank_band
        )
        report["images"].append(item)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not all(item["passed"] for item in report["images"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
