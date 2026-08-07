from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("publish_xiaohongshu.py")
SPEC = importlib.util.spec_from_file_location("publish_xhs", SCRIPT)
publisher = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(publisher)


class XiaohongshuPublisherTests(unittest.TestCase):
    def package(self, root: Path) -> Path:
        (root / "copy.md").write_text("正文", encoding="utf-8")
        image = root / "image.png"
        image.write_bytes(b"image")
        settings = {
            "tags": ["产品"], "schedule_at": "", "is_original": True,
            "visibility": "公开可见", "products": [], "target_account": "测试账号",
        }
        digest = publisher.publication_digest("标题", "正文", [image.resolve()], root.resolve(), settings)
        manifest = {
            "platform": "xiaohongshu", "copy_file": "copy.md", "asset_files": ["image.png"],
            "native_constraints": {"title": "标题", **settings},
            "content_authorization": {
                "rights_confirmed": True, "final_content_reviewed": True, "proxy_action_authorized": True,
                "target_account_confirmed": True, "distribution_settings_reviewed": True,
                "responsibility_accepted": True, "publication_sha256": digest,
            },
            "publish": {"approved": True, "auto_publish": True, "confirmed_at": "now"},
        }
        path = root / "publish-manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_reads_exact_approved_package(self):
        with tempfile.TemporaryDirectory() as temp:
            _, payload = publisher.read_package(self.package(Path(temp)))
            self.assertEqual(payload["title"], "标题")
            self.assertEqual(len(payload["images"]), 1)

    def test_changed_settings_fail_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.package(Path(temp))
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["native_constraints"]["visibility"] = "仅自己可见"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(publisher.PublishError, "publication_sha256"):
                publisher.read_package(path)

    def test_endpoint_must_be_loopback(self):
        old = publisher.os.environ.get("XHS_MCP_ENDPOINT")
        publisher.os.environ["XHS_MCP_ENDPOINT"] = "https://example.com:18063"
        try:
            with self.assertRaisesRegex(publisher.PublishError, "本机"):
                publisher.read_endpoint()
        finally:
            if old is None:
                publisher.os.environ.pop("XHS_MCP_ENDPOINT", None)
            else:
                publisher.os.environ["XHS_MCP_ENDPOINT"] = old


if __name__ == "__main__":
    unittest.main()
