from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("stage_x_draft.py")
SPEC = importlib.util.spec_from_file_location("stage_x_draft", SCRIPT)
stager = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(stager)


class DraftStagerTests(unittest.TestCase):
    def package(self, root: Path, **overrides):
        (root / "draft").mkdir()
        (root / "draft" / "copy.md").write_text(
            "# X 文案（Dry-run，未发布）\n\n测试内容\n\n#GrowthLab\n",
            encoding="utf-8",
        )
        manifest = {
            "platform": "x",
            "copy_file": "draft/copy.md",
            "asset_files": [],
            "draft_staging": {"approved": True},
            "content_governance": {
                "all_stages_scope_acknowledged": True,
                "skill_neutrality_persistent_acknowledged": True,
                "publisher_responsibility_accepted": True,
                "account_authority_confirmed": True,
                "safety_rules_remain_applicable_acknowledged": True,
                "confirmed_at": "2026-08-04T00:00:00+08:00",
            },
            "content_authorization": {
                "rights_confirmed": True,
                "final_content_reviewed": True,
                "generation_disclosed": True,
                "proxy_action_authorized": True,
                "target_account_confirmed": True,
                "distribution_settings_reviewed": True,
                "responsibility_accepted": True,
                "skill_neutrality_acknowledged": True,
                "content_sha256": hashlib.sha256(
                    "测试内容\n\n#GrowthLab".encode("utf-8")
                ).hexdigest(),
                "confirmed_at": "2026-08-04T00:00:00+08:00",
            },
            "publish": {"approved": False, "auto_publish": False},
            **overrides,
        }
        path = root / "publish-manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_reads_approved_copy_without_heading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            _, text, assets = stager.read_package(self.package(Path(temp_dir)))
        self.assertEqual(text, "测试内容\n\n#GrowthLab")
        self.assertEqual(assets, [])

    def test_rejects_live_publish_approval(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.package(
                Path(temp_dir), publish={"approved": True, "auto_publish": False}
            )
            with self.assertRaisesRegex(stager.DraftError, "真实发布"):
                stager.read_package(path)

    def test_save_button_label_is_allowlisted(self):
        self.assertTrue(stager.is_save_label("Save"))
        self.assertTrue(stager.is_save_label("保存"))
        self.assertFalse(stager.is_save_label("Post"))
        self.assertFalse(stager.is_save_label("发布"))

    def test_rejects_missing_full_content_authorization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.package(Path(temp_dir), content_authorization={})
            with self.assertRaisesRegex(stager.DraftError, "明确授权确认"):
                stager.read_package(path)

    def test_rejects_missing_lifecycle_governance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.package(Path(temp_dir), content_governance={})
            with self.assertRaisesRegex(stager.DraftError, "所有环节"):
                stager.read_package(path)

    def test_rejects_copy_changed_after_authorization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = self.package(root)
            (root / "draft" / "copy.md").write_text(
                "# X 文案（Dry-run，未发布）\n\n已改变内容\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(stager.DraftError, "授权哈希"):
                stager.read_package(path)

    def test_accepts_reviewed_media_with_package_hash(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = self.package(root, asset_files=["draft/image.png"])
            image = root / "draft" / "image.png"
            image.write_bytes(b"approved-image")
            manifest = json.loads(path.read_text(encoding="utf-8"))
            text = "测试内容\n\n#GrowthLab"
            manifest["content_authorization"]["package_sha256"] = stager.package_digest(
                text, [image.resolve()], root.resolve()
            )
            path.write_text(json.dumps(manifest), encoding="utf-8")
            _, _, assets = stager.read_package(path)
            self.assertEqual(assets, [image.resolve()])

    def test_rejects_media_changed_after_authorization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = self.package(root, asset_files=["draft/image.png"])
            image = root / "draft" / "image.png"
            image.write_bytes(b"changed")
            with self.assertRaisesRegex(stager.DraftError, "发布包授权哈希"):
                stager.read_package(path)

    def test_delete_button_labels_are_allowlisted(self):
        self.assertTrue(stager.is_delete_label("Delete draft"))
        self.assertTrue(stager.is_delete_label("删除草稿"))
        self.assertFalse(stager.is_delete_label("Post"))

    def test_cdp_must_be_unprivileged_loopback_port(self):
        self.assertEqual(stager.cdp_port("19222"), 19222)
        with self.assertRaises(stager.DraftError):
            stager.cdp_port("80")


if __name__ == "__main__":
    unittest.main()
