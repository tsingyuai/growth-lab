from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("wechat_official_api.py")
SPEC = importlib.util.spec_from_file_location("wechat_api", SCRIPT)
wechat = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(wechat)


class WeChatClientTests(unittest.TestCase):
    def package(self, root: Path) -> Path:
        (root / "article.html").write_text("<p>审核正文</p>", encoding="utf-8")
        article = {
            "title": "标题", "author": "作者", "digest": "摘要", "content": "<p>审核正文</p>",
            "content_source_url": "https://example.com", "thumb_media_id": "thumb-1",
            "need_open_comment": 1, "only_fans_can_comment": 0,
        }
        digest = wechat.package_digest(article, "wx-test-app")
        manifest = {
            "platform": "wechat", "copy_file": "article.html", "asset_files": [],
            "native_constraints": {
                "title": "标题", "author": "作者", "digest": "摘要",
                "content_source_url": "https://example.com", "thumb_media_id": "thumb-1",
                "need_open_comment": True, "only_fans_can_comment": False,
                "target_app_id": "wx-test-app",
            },
            "draft_staging": {"approved": True},
            "content_authorization": {
                "rights_confirmed": True, "final_content_reviewed": True,
                "target_account_confirmed": True, "responsibility_accepted": True,
                "draft_sha256": digest, "publication_sha256": digest,
            },
            "publish": {"approved": False, "auto_publish": False, "confirmed_at": None},
        }
        path = root / "publish-manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_read_exact_html_package(self):
        with tempfile.TemporaryDirectory() as temp:
            _, article = wechat.read_package(self.package(Path(temp)))
            self.assertEqual(article["thumb_media_id"], "thumb-1")
            self.assertEqual(article["need_open_comment"], 1)

    def test_changed_html_fails_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.package(root)
            (root / "article.html").write_text("<p>被修改</p>", encoding="utf-8")
            with self.assertRaisesRegex(wechat.WeChatError, "draft_sha256"):
                wechat.read_package(path)

    def test_markdown_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.package(root)
            manifest = json.loads(path.read_text(encoding="utf-8"))
            (root / "article.md").write_text("正文", encoding="utf-8")
            manifest["copy_file"] = "article.md"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(wechat.WeChatError, "HTML"):
                wechat.read_package(path)


if __name__ == "__main__":
    unittest.main()
