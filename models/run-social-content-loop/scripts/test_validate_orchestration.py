from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError


SCRIPT = Path(__file__).with_name("validate_orchestration.py")
SPEC = importlib.util.spec_from_file_location("validate_orchestration", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


GOVERNANCE = {
    "all_stages_scope_acknowledged": True,
    "skill_neutrality_persistent_acknowledged": True,
    "publisher_responsibility_accepted": True,
    "account_authority_confirmed": True,
    "safety_rules_remain_applicable_acknowledged": True,
    "confirmed_at": "2026-08-04T00:00:00+08:00",
}


class OrchestrationValidationTests(unittest.TestCase):
    def test_schema_files_are_valid_json(self):
        schema_dir = SCRIPT.parent.parent / "schemas"
        for name in (
            "research-plan.schema.json",
            "canonical-brief.schema.json",
            "platform-package.schema.json",
        ):
            parsed = json.loads((schema_dir / name).read_text(encoding="utf-8"))
            self.assertEqual(parsed["$schema"], "https://json-schema.org/draft/2020-12/schema")
            Draft202012Validator.check_schema(parsed)

    def build_run(
        self,
        root: Path,
        targets=("x", "instagram"),
        governance=GOVERNANCE,
        source_platforms=("x",),
    ) -> Path:
        run = root / "run"
        (run / "research").mkdir(parents=True)
        sources = []
        source_ids = []
        for index, platform in enumerate(source_platforms):
            source_id = f"source-{index + 1}"
            evidence = f"research/{source_id}.json"
            (run / evidence).write_text("{}", encoding="utf-8")
            sources.append(
                {
                    "id": source_id,
                    "platform": platform,
                    "role": "primary" if index == 0 else "supporting",
                    "evidence_files": [evidence],
                }
            )
            source_ids.append(source_id)
        (run / "product.md").write_text("verified fact", encoding="utf-8")
        plan = {
            "schema_version": 1,
            "run_id": "test-run",
            "objective": "test native variants",
            "research": {
                "mode": "synthesize",
                "sources": sources,
                "learning_scope": ["topic", "structure"],
                "forbidden_learning": ["copy wording"],
            },
            "distribution": {
                "mode": "single-target" if len(targets) == 1 else "multi-target",
                "targets": [
                    {"platform": platform, "account_role": "official", "objective": "announce", "adapter_mode": "platform-native"}
                    for platform in targets
                ],
            },
            "content_governance": governance,
        }
        plan_path = run / "research-plan.json"
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        brief = {
            "schema_version": 1,
            "brief_id": "brief-1",
            "status": "approved",
            "research_plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
            "product_facts": [{"claim": "fact", "evidence_files": ["product.md"]}],
            "audience": "users",
            "objective": "announce",
            "core_message": "one shared fact base",
            "insights": [{"insight": "short native content", "source_ids": source_ids}],
            "source_boundaries": ["do not copy wording"],
            "target_directions": [
                {"platform": platform, "message_job": "native announcement", "primary_reference_id": source_ids[0], "learning_scope": ["topic", "structure"]}
                for platform in targets
            ],
            "content_governance": governance,
        }
        brief_path = run / "canonical-brief.json"
        brief_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
        brief_hash = hashlib.sha256(brief_path.read_bytes()).hexdigest()
        for platform in targets:
            package = run / "packages" / platform
            package.mkdir(parents=True)
            (package / "copy.md").write_text(f"{platform} copy", encoding="utf-8")
            (package / "source-boundary.md").write_text("no copying", encoding="utf-8")
            manifest = {
                "schema_version": 1,
                "package_id": f"pkg-{platform}",
                "platform": platform,
                "canonical_brief_sha256": brief_hash,
                "account_role": "official",
                "adapter_mode": "platform-native",
                "copy_file": "copy.md",
                "source_boundary_file": "source-boundary.md",
                "asset_files": [],
                "native_constraints": {"format": "native"},
                "content_governance": governance,
                "content_authorization": {},
                "publish": {"approved": False, "auto_publish": False, "confirmed_at": None},
            }
            (package / "publish-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return run

    def test_supported_research_and_distribution_matrix(self):
        cases = (
            (("x", "xiaohongshu"), ("x",)),
            (("x", "xiaohongshu"), ("x", "instagram")),
            (("x",), ("x",)),
            (("x",), ("instagram",)),
            (("user-provided",), ("x",)),
            (("user-provided",), ("x", "email")),
        )
        for source_platforms, targets in cases:
            with self.subTest(sources=source_platforms, targets=targets):
                with tempfile.TemporaryDirectory() as temp_dir:
                    run = self.build_run(
                        Path(temp_dir), targets, GOVERNANCE, source_platforms
                    )
                    result = validator.validate(run, "packages")
                self.assertEqual(result["targets"], list(targets))
                self.assertEqual(result["source_count"], len(source_platforms))

    def test_plan_stage_allows_research_before_governance(self):
        governance = {key: False for key in validator.GOVERNANCE_FIELDS}
        governance["confirmed_at"] = None
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.validate(self.build_run(Path(temp_dir), ("x",), governance), "plan")
        self.assertEqual(result["status"], "valid")

    def test_plan_allows_declared_evidence_before_collection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir), ("x",), GOVERNANCE)
            (run / "research" / "source-1.json").unlink()
            self.assertEqual(validator.validate(run, "plan")["status"], "valid")
            with self.assertRaisesRegex(validator.ValidationError, "文件不存在"):
                validator.validate(run, "generation")

    def test_generation_requires_lifecycle_governance(self):
        governance = {key: False for key in validator.GOVERNANCE_FIELDS}
        governance["confirmed_at"] = None
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir), ("x",), governance)
            with self.assertRaisesRegex(validator.ValidationError, "全生命周期"):
                validator.validate(run, "generation")

    def test_brief_hash_must_match_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir), ("x",))
            plan = json.loads((run / "research-plan.json").read_text(encoding="utf-8"))
            plan["objective"] = "changed"
            (run / "research-plan.json").write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "哈希"):
                validator.validate(run, "generation")

    def test_multi_target_rejects_close_adaptation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir))
            plan_path = run / "research-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["distribution"]["targets"][0]["adapter_mode"] = "close-adaptation"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "platform-native"):
                validator.validate(run, "plan")

    def test_close_replication_requires_explicit_policy(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir), ("xiaohongshu",))
            plan_path = run / "research-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["distribution"]["targets"][0]["adapter_mode"] = "close-replication"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "replication_policy"):
                validator.validate(run, "plan")

    def test_single_target_accepts_confirmed_close_replication(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir), ("xiaohongshu",))
            plan_path = run / "research-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["research"]["learning_scope"] = ["topic", "structure", "visual", "format"]
            plan["distribution"]["targets"][0]["adapter_mode"] = "close-replication"
            plan["distribution"]["targets"][0]["replication_policy"] = {
                "risk_accepted": True,
                "single_reference_only": True,
                "replace_source_assets": True,
                "rights_basis": "user explicitly requested and accepted close replication risk",
                "confirmed_at": "2026-08-04T12:00:00+08:00",
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = validator.validate(run, "plan")
        self.assertEqual(result["status"], "valid")

    def test_confirmed_close_replication_passes_full_package_flow(self):
        policy = {
            "risk_accepted": True,
            "single_reference_only": True,
            "replace_source_assets": True,
            "rights_basis": "user explicitly requested and accepted close replication risk",
            "confirmed_at": "2026-08-04T12:00:00+08:00",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir), ("xiaohongshu",), source_platforms=("xiaohongshu",))
            plan_path = run / "research-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["research"]["learning_scope"] = ["topic", "structure", "visual", "format"]
            plan["distribution"]["targets"][0]["adapter_mode"] = "close-replication"
            plan["distribution"]["targets"][0]["replication_policy"] = policy
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            brief_path = run / "canonical-brief.json"
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
            brief["research_plan_sha256"] = hashlib.sha256(plan_path.read_bytes()).hexdigest()
            brief["target_directions"][0]["learning_scope"] = ["topic", "structure", "visual", "format"]
            brief_path.write_text(json.dumps(brief), encoding="utf-8")

            manifest_path = run / "packages" / "xiaohongshu" / "publish-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["canonical_brief_sha256"] = hashlib.sha256(brief_path.read_bytes()).hexdigest()
            manifest["adapter_mode"] = "close-replication"
            manifest["replication_policy"] = policy
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = validator.validate(run, "packages")
            schema_dir = SCRIPT.parent.parent / "schemas"
            Draft202012Validator(json.loads((schema_dir / "research-plan.schema.json").read_text(encoding="utf-8"))).validate(plan)
            Draft202012Validator(json.loads((schema_dir / "platform-package.schema.json").read_text(encoding="utf-8"))).validate(manifest)
        self.assertEqual(result["status"], "valid")

    def test_packages_must_cover_every_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir))
            (run / "packages" / "instagram" / "publish-manifest.json").unlink()
            with self.assertRaises(validator.ValidationError):
                validator.validate(run, "packages")

    def test_multi_target_rejects_same_copy_with_different_tags(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir))
            (run / "packages" / "x" / "copy.md").write_text(
                "same body #x", encoding="utf-8"
            )
            (run / "packages" / "instagram" / "copy.md").write_text(
                "same body #instagram", encoding="utf-8"
            )
            with self.assertRaisesRegex(validator.ValidationError, "平台原生"):
                validator.validate(run, "packages")

    def test_valid_run_documents_match_published_schemas(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir))
            schema_dir = SCRIPT.parent.parent / "schemas"
            plan_schema = json.loads(
                (schema_dir / "research-plan.schema.json").read_text(encoding="utf-8")
            )
            brief_schema = json.loads(
                (schema_dir / "canonical-brief.schema.json").read_text(encoding="utf-8")
            )
            package_schema = json.loads(
                (schema_dir / "platform-package.schema.json").read_text(encoding="utf-8")
            )
            Draft202012Validator(plan_schema).validate(
                json.loads((run / "research-plan.json").read_text(encoding="utf-8"))
            )
            Draft202012Validator(brief_schema).validate(
                json.loads((run / "canonical-brief.json").read_text(encoding="utf-8"))
            )
            for platform in ("x", "instagram"):
                Draft202012Validator(package_schema).validate(
                    json.loads(
                        (run / "packages" / platform / "publish-manifest.json").read_text(
                            encoding="utf-8"
                        )
                    )
                )

    def test_schema_rejects_missing_required_plan_field(self):
        schema = json.loads(
            (SCRIPT.parent.parent / "schemas" / "research-plan.schema.json").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir), ("x",))
            plan = json.loads((run / "research-plan.json").read_text(encoding="utf-8"))
            del plan["objective"]
            with self.assertRaises(JsonSchemaValidationError):
                Draft202012Validator(schema).validate(plan)

    def test_video_target_requires_rendered_video_manifest_and_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run = self.build_run(Path(temp_dir), ("x",))
            plan_path = run / "research-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["distribution"]["targets"][0]["formats"] = ["text", "video"]
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            brief_path = run / "canonical-brief.json"
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
            brief["research_plan_sha256"] = hashlib.sha256(plan_path.read_bytes()).hexdigest()
            brief_path.write_text(json.dumps(brief), encoding="utf-8")
            package = run / "packages" / "x"
            manifest_path = package / "publish-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["canonical_brief_sha256"] = hashlib.sha256(brief_path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "video_manifest_file"):
                validator.validate(run, "packages")
            video_dir = package / "video"
            (video_dir / "render").mkdir(parents=True)
            (video_dir / "render" / "final.mp4").write_bytes(b"fixture-video")
            (video_dir / "video-manifest.json").write_text(
                json.dumps({"status": "rendered-not-published", "files": {"video": "render/final.mp4"}}),
                encoding="utf-8",
            )
            manifest["video_manifest_file"] = "video/video-manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = validator.validate(run, "packages")
        self.assertEqual(result["status"], "valid")


if __name__ == "__main__":
    unittest.main()
