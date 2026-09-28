from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_visual_reference_selection.py")
SPEC = importlib.util.spec_from_file_location("validate_visual_reference_selection", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class VisualReferenceSelectionTests(unittest.TestCase):
    def test_requires_exactly_one_valid_primary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            image_a = root / "visual-candidates/a/01.png"
            image_b = root / "visual-candidates/b/01.png"
            image_a.parent.mkdir(parents=True)
            image_b.parent.mkdir(parents=True)
            image_a.write_bytes(b"image-a")
            image_b.write_bytes(b"image-b")
            candidates = {
                "candidates": [
                    {"note_id": "a", "image_files": ["visual-candidates/a/01.png"]},
                    {"note_id": "b", "image_files": ["visual-candidates/b/01.png"]},
                ]
            }
            selection = {
                "schema_version": 1,
                "primary": {
                    "note_id": "a",
                    "reference_image": "visual-candidates/a/01.png",
                    "reasons": {
                        "topic_fit": "matches the task",
                        "visual_quality": "clear hierarchy",
                        "product_fit": "supports a restrained product card",
                        "non_copying_boundary": "learn hierarchy only",
                    },
                },
                "rejected_candidate_ids": ["b"],
            }
            candidates_path = root / "visual-candidates.json"
            selection_path = root / "visual-reference-selection.json"
            candidates_path.write_text(json.dumps(candidates), encoding="utf-8")
            selection_path.write_text(json.dumps(selection), encoding="utf-8")

            result = validator.validate(selection_path, candidates_path)
            self.assertEqual(result["primary_note_id"], "a")

            selection["selected"] = ["a", "b"]
            selection_path.write_text(json.dumps(selection), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "multiple-primary"):
                validator.validate(selection_path, candidates_path)


if __name__ == "__main__":
    unittest.main()
