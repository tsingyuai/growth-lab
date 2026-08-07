from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("validate_visual_quality_review.py")


def review() -> dict:
    score_keys = [
        "content_completeness", "hierarchy", "composition", "layout_vitality",
        "mobile_readability", "evidence_strength", "visual_finish", "benchmark_parity",
    ]
    return {
        "schema_version": 1, "status": "pass", "attempt": 1,
        "reviewed_at_phone_scale": True,
        "benchmark": {"source": "approved-v7.png", "approved_by_user": True},
        "cards": [{
            "id": "01-cover", "output": "render/01-cover.png", "decision": "approved",
            "scores": {key: 4 for key in score_keys},
            "checks": {
                "one_clear_job": True, "no_placeholder_content": True,
                "no_purposeless_empty_zone": True, "exact_copy": True,
                "evidence_target_visible": True, "phone_scale_checked": True,
            },
            "failure_modes": [], "next_action": "none",
        }],
        "sequence_checks": {
            "distinct_compositions": True, "no_template_repetition": True,
            "distinct_product_states": True, "coherent_visual_system": True,
        },
        "rework_items": [],
    }


def run(data: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "review.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), "--review", str(path)], text=True, capture_output=True)


class VisualQualityReviewTests(unittest.TestCase):
    def test_passes_complete_review(self) -> None:
        result = run(review())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_one_low_score(self) -> None:
        data = review()
        data["cards"][0]["scores"]["layout_vitality"] = 3
        result = run(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("layout_vitality", result.stderr)

    def test_rejects_purposeless_empty_zone(self) -> None:
        data = review()
        data["cards"][0]["checks"]["no_purposeless_empty_zone"] = False
        result = run(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no_purposeless_empty_zone", result.stderr)


if __name__ == "__main__":
    unittest.main()
