from __future__ import annotations

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib


SCRIPT = Path(__file__).with_name("validate_social_card_pack.py")


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))


def write_rgb_png(path: Path, width: int, height: int) -> None:
    row = b"\x00" + b"\xff\xff\xff" * width
    payload = zlib.compress(row * height)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", payload)
        + png_chunk(b"IEND", b"")
    )


def write_manifest(package: Path, output: str = "render/01-cover.png") -> None:
    data = {
        "schema_version": 1,
        "platform": "xiaohongshu",
        "production_mode": "complete-effect",
        "canvas": {"width": 12, "height": 16, "format": "png", "color_modes": ["RGB"]},
        "cards": [{"id": "01-cover", "output": output}],
    }
    (package / "visual-manifest.json").write_text(json.dumps(data), encoding="utf-8")


def run_validator(package: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--package", str(package)],
        text=True,
        capture_output=True,
        check=False,
    )


class SocialCardPackValidatorTests(unittest.TestCase):
    def test_valid_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            write_rgb_png(package / "render/01-cover.png", 12, 16)
            write_manifest(package)
            result = run_validator(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"card_count": 1', result.stdout)

    def test_rejects_wrong_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            write_rgb_png(package / "render/01-cover.png", 10, 16)
            write_manifest(package)
            result = run_validator(package)
            self.assertEqual(result.returncode, 1)
            self.assertIn("wrong dimensions", result.stderr)

    def test_rejects_unsafe_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            write_rgb_png(package / "render/01-cover.png", 12, 16)
            write_manifest(package, "../01-cover.png")
            result = run_validator(package)
            self.assertEqual(result.returncode, 1)
            self.assertIn("safe relative path", result.stderr)


if __name__ == "__main__":
    unittest.main()
