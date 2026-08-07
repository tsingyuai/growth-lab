from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image


SCRIPT = Path(__file__).with_name("check_layout_variety.py")
SPEC = importlib.util.spec_from_file_location("check_layout_variety", SCRIPT)
layout = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(layout)

COMPOSE_SCRIPT = Path(__file__).with_name("compose_screenshot_scene.py")
COMPOSE_SPEC = importlib.util.spec_from_file_location("compose_screenshot_scene", COMPOSE_SCRIPT)
compose = importlib.util.module_from_spec(COMPOSE_SPEC)
assert COMPOSE_SPEC and COMPOSE_SPEC.loader
COMPOSE_SPEC.loader.exec_module(compose)


class LayoutVarietyTests(unittest.TestCase):
    def check(self, cards: list[dict]) -> list[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = Path(temp_dir) / "layout-ledger.json"
            ledger.write_text(json.dumps({"cards": cards}), encoding="utf-8")
            return layout.check(ledger)

    def test_repeated_fingerprint_is_rejected(self) -> None:
        card = {
            "archetype": "hero",
            "title_anchor": "top",
            "visual_mass": "center",
            "reading_path": "vertical",
            "screenshot_geometry": "none",
        }
        errors = self.check([
            {**card, "page": "01", "unique_move": "title-over-hero"},
            {**card, "page": "02", "unique_move": "split-proof-zone"},
        ])
        self.assertTrue(any("指纹完全重复" in error for error in errors))

    def test_distinct_three_card_slice_passes(self) -> None:
        errors = self.check([
            {"page": "01", "archetype": "hero", "title_anchor": "top", "visual_mass": "center", "reading_path": "vertical", "screenshot_geometry": "none", "unique_move": "title-over-hero"},
            {"page": "02", "archetype": "steps", "title_anchor": "left", "visual_mass": "bottom", "reading_path": "z-path", "screenshot_geometry": "single-dominant", "unique_move": "numbered-side-rail"},
            {"page": "03", "archetype": "proof", "title_anchor": "top", "visual_mass": "right", "reading_path": "split", "screenshot_geometry": "overlap-stack", "unique_move": "evidence-callout"},
        ])
        self.assertEqual(errors, [])


class ScreenshotShapeTests(unittest.TestCase):
    def test_ellipse_component_masks_corners(self) -> None:
        source = Image.new("RGBA", (80, 60), "#00C800")
        result = compose.rounded_component(source, 0, {}, "ellipse")
        self.assertEqual(result.getpixel((0, 0))[3], 0)
        self.assertEqual(result.getpixel((40, 30))[3], 255)


if __name__ == "__main__":
    unittest.main()
