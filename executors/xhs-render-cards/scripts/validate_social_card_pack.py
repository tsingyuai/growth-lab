#!/usr/bin/env python3
"""Validate a social card pack manifest and its rendered PNG files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import struct
import sys


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_MODES = {2: "RGB", 6: "RGBA"}


def fail(message: str) -> None:
    raise ValueError(message)


def safe_relative_path(value: str, field: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        fail(f"{field} must be a safe relative path: {value!r}")
    return path


def read_png(path: Path) -> tuple[int, int, str]:
    with path.open("rb") as handle:
        if handle.read(8) != PNG_SIGNATURE:
            fail(f"not a PNG file: {path}")
        length = struct.unpack(">I", handle.read(4))[0]
        chunk = handle.read(4)
        if chunk != b"IHDR" or length != 13:
            fail(f"invalid PNG IHDR: {path}")
        width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
            ">IIBBBBB", handle.read(13)
        )
    if bit_depth != 8 or compression != 0 or filtering != 0 or interlace not in (0, 1):
        fail(f"unsupported PNG encoding: {path}")
    mode = COLOR_MODES.get(color_type)
    if mode is None:
        fail(f"PNG must use RGB or RGBA color type: {path}")
    return width, height, mode


def load_manifest(package: Path) -> dict:
    manifest_path = package / "visual-manifest.json"
    if not manifest_path.is_file():
        fail(f"missing visual-manifest.json: {manifest_path}")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid visual-manifest.json: {exc}")
    if not isinstance(data, dict):
        fail("visual-manifest.json must contain an object")
    return data


def validate(package: Path) -> dict:
    package = package.resolve()
    manifest = load_manifest(package)
    if manifest.get("schema_version") != 1:
        fail("schema_version must be 1")
    if not isinstance(manifest.get("platform"), str) or not manifest["platform"].strip():
        fail("platform is required")
    if manifest.get("production_mode") not in {
        "deterministic",
        "complete-effect",
        "separable-layer",
    }:
        fail("production_mode is invalid")

    canvas = manifest.get("canvas")
    if not isinstance(canvas, dict):
        fail("canvas is required")
    width = canvas.get("width")
    height = canvas.get("height")
    if not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
        fail("canvas width and height must be positive integers")
    if canvas.get("format") != "png":
        fail("canvas format must be png")
    allowed_modes = canvas.get("color_modes", ["RGB", "RGBA"])
    if not isinstance(allowed_modes, list) or not set(allowed_modes).issubset({"RGB", "RGBA"}):
        fail("canvas color_modes must contain only RGB or RGBA")

    cards = manifest.get("cards")
    if not isinstance(cards, list) or not cards:
        fail("cards must be a non-empty array")

    seen_ids: set[str] = set()
    seen_outputs: set[str] = set()
    results = []
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            fail(f"cards[{index}] must be an object")
        card_id = card.get("id")
        if not isinstance(card_id, str) or not card_id.strip():
            fail(f"cards[{index}].id is required")
        if card_id in seen_ids:
            fail(f"duplicate card id: {card_id}")
        seen_ids.add(card_id)

        output_value = card.get("output")
        if not isinstance(output_value, str):
            fail(f"cards[{index}].output is required")
        output = safe_relative_path(output_value, f"cards[{index}].output")
        if output.parts[0] != "render" or output.suffix.lower() != ".png":
            fail(f"card output must be render/*.png: {output_value}")
        normalized = output.as_posix()
        if normalized in seen_outputs:
            fail(f"duplicate card output: {normalized}")
        seen_outputs.add(normalized)

        image_path = package.joinpath(*output.parts)
        if not image_path.is_file():
            fail(f"missing rendered card: {normalized}")
        actual_width, actual_height, mode = read_png(image_path)
        if (actual_width, actual_height) != (width, height):
            fail(
                f"wrong dimensions for {normalized}: "
                f"{actual_width}x{actual_height}, expected {width}x{height}"
            )
        if mode not in allowed_modes:
            fail(f"disallowed color mode for {normalized}: {mode}")
        results.append({"id": card_id, "output": normalized, "mode": mode})

    render_dir = package / "render"
    actual_outputs = {
        f"render/{path.name}" for path in render_dir.glob("*.png") if path.is_file()
    }
    extras = sorted(actual_outputs - seen_outputs)
    if extras:
        fail(f"render directory contains unlisted PNG files: {', '.join(extras)}")

    return {
        "ok": True,
        "platform": manifest["platform"],
        "production_mode": manifest["production_mode"],
        "canvas": {"width": width, "height": height, "format": "png"},
        "card_count": len(results),
        "cards": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.package)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
