from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("auto_select_visual_reference.py")
SPEC = importlib.util.spec_from_file_location("auto_select_visual_reference", SCRIPT)
selector = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(selector)


class AutoSelectionTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path]:
        (root / "images").mkdir()
        for name in ("a.png", "b.png"):
            (root / "images" / name).write_bytes(b"png")
        candidates = root / "visual-candidates.json"
        candidates.write_text(
            json.dumps({"candidates": [
                {"note_id": "a", "image_files": ["images/a.png"]},
                {"note_id": "b", "image_files": ["images/b.png"]},
            ]}),
            encoding="utf-8",
        )
        review = root / "visual-review.json"
        return candidates, review

    def scores(self, total_variant: int = 0) -> dict[str, int]:
        return {
            "promotional_hierarchy": 20 + total_variant,
            "content_visualization": 16,
            "proof_zone": 16,
            "layout_whitespace": 12,
            "mobile_readability": 8,
            "product_adaptability": 8,
        }

    def test_selects_highest_passing_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            candidates, review = self.fixture(Path(temp_dir))
            review.write_text(json.dumps({"items": [
                {"note_id": "a", "hard_reject": False, "scores": self.scores()},
                {"note_id": "b", "hard_reject": False, "scores": self.scores(2)},
            ]}), encoding="utf-8")
            result = selector.select(candidates, review)
        self.assertEqual(result["primary"]["note_id"], "b")
        self.assertEqual(result["rejected_candidate_ids"], ["a"])
        self.assertEqual(
            result["disclosure"], "internal-only-do-not-display-reference-by-default"
        )

    def test_refuses_to_force_weak_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            candidates, review = self.fixture(Path(temp_dir))
            weak = {key: 1 for key in selector.DIMENSIONS}
            review.write_text(json.dumps({"items": [
                {"note_id": "a", "hard_reject": False, "scores": weak},
                {"note_id": "b", "hard_reject": True, "scores": self.scores(2)},
            ]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "提供其认为合适"):
                selector.select(candidates, review)


if __name__ == "__main__":
    unittest.main()
