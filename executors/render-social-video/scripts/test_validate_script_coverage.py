from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("validate_script_coverage.py")
SPEC = importlib.util.spec_from_file_location("validate_script_coverage", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ScriptCoverageTests(unittest.TestCase):
    def fixture(self, directory: Path, *, status: str = "approved", short_hold: bool = False) -> tuple[Path, Path, Path]:
        script_path = directory / "video-script.json"
        script = {
            "schema_version": 1,
            "title": "Product demo",
            "workflow_mode": "human-reviewed",
            "status": status,
            "total_duration_seconds": 4.0,
            "shots": [{
                "id": "product-input",
                "start_seconds": 0,
                "end_seconds": 4.0,
                "purpose": "Show the real input action",
                "source_type": "screen-recording",
                "picture": "Type one approved sentence into the Product input",
                "narration": "输入需要证据支持的判断。",
                "subtitle": "输入需要证据支持的判断。",
                "requirements": [{
                    "id": "typed-state",
                    "kind": "product-action",
                    "instruction": "Type the approved sentence",
                    "expected_visible_state": "The complete sentence is visible in the input",
                    "minimum_hold_seconds": 1.0
                }]
            }]
        }
        script_path.write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
        asset = directory / "clip.mp4"
        frame = directory / "typed-state.png"
        asset.write_bytes(b"fixture-video")
        frame.write_bytes(b"fixture-frame")
        evidence_path = directory / "asset-evidence-ledger.json"
        evidence = {
            "schema_version": 1,
            "script_file": "video-script.json",
            "script_sha256": sha256(script_path),
            "shots": [{
                "shot_id": "product-input",
                "asset_file": "clip.mp4",
                "asset_sha256": sha256(asset),
                "status": "pass",
                "requirements": [{
                    "requirement_id": "typed-state",
                    "status": "pass",
                    "evidence_file": "typed-state.png",
                    "evidence_timestamp_seconds": 2.5,
                    "observed_hold_seconds": 0.5 if short_hold else 1.2,
                    "observed_state": "The complete sentence is visible"
                }]
            }]
        }
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False), encoding="utf-8")
        plan_path = directory / "video-plan.json"
        plan = {
            "scenes": [{
                "id": "product-input",
                "type": "video",
                "asset": "clip.mp4",
                "asset_role": "screen-recording",
                "narration": "输入需要证据支持的判断。",
                "duration": 4.0
            }]
        }
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        return script_path, evidence_path, plan_path

    def test_complete_approved_script_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, evidence, plan = self.fixture(Path(temp))
            result = MODULE.validate(script.resolve(), evidence.resolve(), True, plan.resolve())
            self.assertEqual(result["status"], "pass")

    def test_presented_human_script_cannot_enter_production(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, evidence, plan = self.fixture(Path(temp), status="presented")
            result = MODULE.validate(script.resolve(), evidence.resolve(), True, plan.resolve())
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("must be approved" in item for item in result["failures"]))

    def test_short_visible_hold_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, evidence, plan = self.fixture(Path(temp), short_hold=True)
            result = MODULE.validate(script.resolve(), evidence.resolve(), True, plan.resolve())
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("readable hold is too short" in item for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
