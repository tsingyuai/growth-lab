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

    def test_caption_timing_and_lanes_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, evidence, plan = self.fixture(Path(temp))
            script_data = json.loads(script.read_text(encoding="utf-8"))
            shot = script_data["shots"][0]
            shot["speech_groups"] = [{
                "id": "benefits", "display_mode": "accumulate", "exit_mode": "group",
                "vertical_anchor": "middle",
                "segments": [
                    {"id": "automatic", "text": "能自动", "lane": "left", "pause_after_ms": 200},
                    {"id": "control", "text": "可控制", "lane": "center", "pause_after_ms": 0},
                ],
            }]
            shot["narration"] = shot["subtitle"] = "能自动，可控制"
            script.write_text(json.dumps(script_data, ensure_ascii=False), encoding="utf-8")

            evidence_data = json.loads(evidence.read_text(encoding="utf-8"))
            evidence_data["script_sha256"] = sha256(script)
            evidence_shot = evidence_data["shots"][0]
            evidence_shot["caption_checks"] = [
                {"group_id": "benefits", "segment_id": "automatic", "status": "pass", "lane": "left", "audio_start_seconds": 0.2, "caption_start_seconds": 0.3},
                {"group_id": "benefits", "segment_id": "control", "status": "pass", "lane": "center", "audio_start_seconds": 1.0, "caption_start_seconds": 1.1},
            ]
            evidence_shot["caption_group_checks"] = [
                {"group_id": "benefits", "status": "pass", "audio_end_seconds": 1.8, "caption_exit_seconds": 1.95}
            ]
            evidence.write_text(json.dumps(evidence_data, ensure_ascii=False), encoding="utf-8")

            plan_data = json.loads(plan.read_text(encoding="utf-8"))
            plan_scene = plan_data["scenes"][0]
            plan_scene["narration"] = "能自动，可控制"
            plan_scene["speech_segments"] = [
                {"id": "automatic", "text": "能自动", "pause_after_ms": 200},
                {"id": "control", "text": "可控制", "pause_after_ms": 0},
            ]
            plan_scene["caption_groups"] = [{
                "id": "benefits", "display_mode": "accumulate", "exit_together": True,
                "vertical_anchor": "middle", "end": 1.95,
                "segments": [
                    {"id": "automatic", "text": "能自动", "lane": "left", "start": 0.3},
                    {"id": "control", "text": "可控制", "lane": "center", "start": 1.1},
                ],
            }]
            plan.write_text(json.dumps(plan_data, ensure_ascii=False), encoding="utf-8")
            result = MODULE.validate(script.resolve(), evidence.resolve(), True, plan.resolve())
            self.assertEqual(result["status"], "pass")

            evidence_data["shots"][0]["caption_checks"][1]["caption_start_seconds"] = 1.3
            evidence.write_text(json.dumps(evidence_data, ensure_ascii=False), encoding="utf-8")
            result = MODULE.validate(script.resolve(), evidence.resolve(), True, plan.resolve())
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("180ms" in item for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
