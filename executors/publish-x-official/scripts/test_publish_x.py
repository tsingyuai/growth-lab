from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("publish_x.py")
SPEC = importlib.util.spec_from_file_location("publish_x", SCRIPT)
publisher = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(publisher)


class FakeClient:
    def __init__(self):
        self.uploaded = []
        self.created = None

    def upload_image(self, path):
        self.uploaded.append(path.name)
        return "media-1"

    def me(self):
        return {"data": {"id": "99", "username": "growthlab"}}

    def create_post(self, text, media_ids):
        self.created = (text, media_ids)
        return {"data": {"id": "12345"}}

    def delete_post(self, post_id):
        return {"data": {"deleted": True}}


class XPublisherTests(unittest.TestCase):
    def package(self, root: Path, with_image: bool = True) -> Path:
        (root / "copy.md").write_text("测试正式发布", encoding="utf-8")
        assets = []
        paths = []
        if with_image:
            image = root / "image.png"
            image.write_bytes(b"image")
            assets = ["image.png"]
            paths = [image.resolve()]
        digest = publisher.publication_digest(
            "测试正式发布", paths, root.resolve(), "growthlab"
        )
        manifest = {
            "platform": "x", "copy_file": "copy.md", "asset_files": assets,
            "native_constraints": {"target_account": "@growthlab"},
            "content_authorization": {
                "rights_confirmed": True, "final_content_reviewed": True,
                "proxy_action_authorized": True, "target_account_confirmed": True,
                "distribution_settings_reviewed": True, "responsibility_accepted": True,
                "publication_sha256": digest,
            },
            "publish": {"approved": True, "auto_publish": True, "confirmed_at": "now"},
        }
        path = root / "publish-manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_package_digest_covers_image_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.package(root)
            publisher.read_package(path)
            (root / "image.png").write_bytes(b"changed")
            with self.assertRaisesRegex(publisher.PublishError, "publication_sha256"):
                publisher.read_package(path)

    def test_publish_records_id_and_prevents_duplicate(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.package(Path(temp))
            client = FakeClient()
            result = publisher.publish(path, client)
            self.assertEqual(result["post_id"], "12345")
            self.assertEqual(client.uploaded, ["image.png"])
            with self.assertRaisesRegex(publisher.PublishError, "重复"):
                publisher.publish(path, client)

    def test_delete_uses_recorded_post_id(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.package(Path(temp), with_image=False)
            client = FakeClient()
            publisher.publish(path, client)
            result = publisher.delete(path, client)
            self.assertEqual(result["status"], "deleted")


if __name__ == "__main__":
    unittest.main()
