from __future__ import annotations

import importlib.util
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("collect_xiaohongshu.py")
SPEC = importlib.util.spec_from_file_location("collect_xiaohongshu", SCRIPT)
collector = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(collector)


class CollectXiaohongshuTests(unittest.TestCase):
    def test_default_limit_and_sanitized_output(self) -> None:
        requests: list[dict] = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                data = {"is_logged_in": True} if self.path.endswith("/login/status") else {"status": "healthy"}
                self.respond(data)

            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                requests.append(json.loads(self.rfile.read(length)))
                self.respond({"feeds": [{
                    "id": "note-1",
                    "xsecToken": "secret-token",
                    "modelType": "note",
                    "noteCard": {
                        "type": "normal",
                        "displayTitle": "测试标题",
                        "user": {"nickname": "公开作者", "avatar": "https://private.example/avatar"},
                        "interactInfo": {"likedCount": "12", "commentCount": "3", "collectedCount": "8"},
                        "cover": {"urlDefault": "https://cdn.example/image?signature=secret"},
                    },
                }]})

            def respond(self, data):
                body = json.dumps({"success": True, "data": data}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp_dir, mock.patch.dict(
                collector.os.environ, {"DEFAULT_SAMPLE_LIMIT": "25"}
            ):
                args = collector.build_parser().parse_args([
                    "文献综述", "--out", str(Path(temp_dir) / "evidence.json")
                ])
            self.assertEqual(args.limit, 25)
            client = collector.XiaohongshuClient(f"http://127.0.0.1:{server.server_port}", 2)
            client.check_ready()
            evidence = collector.build_evidence("文献综述", client.search("文献综述", args.limit), args.limit)
        finally:
            server.shutdown()
            server.server_close()

        self.assertEqual(requests[0]["max_items"], 25)
        serialized = json.dumps(evidence, ensure_ascii=False)
        self.assertEqual(evidence["collected"], 1)
        self.assertEqual(evidence["items"][0]["public_url"], "https://www.xiaohongshu.com/explore/note-1")
        self.assertNotIn("secret-token", serialized)
        self.assertNotIn("signature", serialized)
        self.assertNotIn("private.example", serialized)

    def test_configured_default_limit_is_adjustable(self) -> None:
        with mock.patch.dict(collector.os.environ, {"DEFAULT_SAMPLE_LIMIT": "20"}):
            args = collector.build_parser().parse_args(["主题", "--out", "evidence.json"])
        self.assertEqual(args.limit, 20)

    def test_rejects_non_local_endpoint(self) -> None:
        with self.assertRaises(collector.CollectorError):
            collector.validate_local_endpoint("https://example.com:18063")

    def test_cover_pool_downloads_all_covers_without_persisting_tokens(self) -> None:
        feeds = [
            {
                "id": "note-low",
                "xsecToken": "token-low",
                "modelType": "note",
                "noteCard": {
                    "displayTitle": "文献综述基础",
                    "cover": {"urlDefault": "cover"},
                    "interactInfo": {"likedCount": "10", "collectedCount": "20"},
                },
            },
            {
                "id": "note-high",
                "xsecToken": "token-high",
                "modelType": "note",
                "noteCard": {
                    "displayTitle": "文献综述视觉案例",
                    "cover": {"urlDefault": "cover"},
                    "interactInfo": {"likedCount": "1万", "collectedCount": "2万"},
                },
            },
        ]

        class FakeClient:
            opener = object()
            timeout = 2

        png = b"\x89PNG\r\n\x1a\n" + b"test-image"
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            collector, "download_image", return_value=png
        ), mock.patch.object(
            collector, "build_cover_contact_sheets", return_value=["cover-pool/contact-sheet-01.jpg"]
        ):
            root = Path(temp_dir)
            manifest = collector.prepare_cover_pool(FakeClient(), feeds, root, 2)
            serialized = json.dumps(manifest, ensure_ascii=False)
            saved = (root / "cover-pool.json").read_text(encoding="utf-8")
            self.assertEqual(manifest["cover_count"], 2)
            self.assertEqual(manifest["items"][0]["note_id"], "note-low")
            self.assertTrue((root / manifest["items"][0]["cover_file"]).is_file())
            self.assertNotIn("token-high", serialized + saved)
            self.assertNotIn("signature", serialized + saved)

    def test_visual_candidates_require_explicit_reviewed_note_ids(self) -> None:
        feeds = [
            {
                "id": "note-low",
                "xsecToken": "token-low",
                "modelType": "note",
                "noteCard": {"displayTitle": "低互动但排版合格", "cover": {"urlDefault": "cover"}},
            },
            {
                "id": "note-high",
                "xsecToken": "token-high",
                "modelType": "note",
                "noteCard": {"displayTitle": "高互动但排版不合格", "cover": {"urlDefault": "cover"}},
            },
        ]

        class FakeClient:
            opener = object()
            timeout = 2

            def detail(self, feed_id, token):
                return {
                    "noteId": feed_id,
                    "title": f"详情 {feed_id}",
                    "desc": "公开正文摘要",
                    "type": "normal",
                    "user": {"nickname": "作者"},
                    "interactInfo": {"likedCount": "10"},
                    "imageList": [{"urlDefault": f"https://cdn.example/{feed_id}?signature=secret"}],
                }

        png = b"\x89PNG\r\n\x1a\n" + b"test-image"
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            collector, "download_image", return_value=png
        ):
            root = Path(temp_dir)
            manifest = collector.prepare_visual_candidates(
                FakeClient(), feeds, root, ["note-low"], 1, 0
            )
            serialized = json.dumps(manifest, ensure_ascii=False)
            saved = (root / "visual-candidates.json").read_text(encoding="utf-8")
            self.assertEqual(manifest["candidate_count"], 1)
            self.assertEqual(manifest["candidates"][0]["note_id"], "note-low")
            self.assertTrue((root / manifest["candidates"][0]["image_files"][0]).is_file())
            self.assertNotIn("token-high", serialized + saved)
            self.assertNotIn("signature", serialized + saved)

    def test_review_selection_file_contains_only_public_note_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            selection = Path(temp_dir) / "cover-selection.json"
            selection.write_text(
                json.dumps({"note_ids": ["note-visual-1", "note-visual-2"]}),
                encoding="utf-8",
            )
            self.assertEqual(
                collector.wait_for_review_selection(selection, 1),
                ["note-visual-1", "note-visual-2"],
            )


if __name__ == "__main__":
    unittest.main()
