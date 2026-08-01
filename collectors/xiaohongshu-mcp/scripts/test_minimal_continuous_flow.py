from __future__ import annotations

import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.parse import urlsplit


SCRIPT = Path(__file__).with_name("collect_xiaohongshu.py")
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class MinimalContinuousFlowTest(unittest.TestCase):
    def test_search_cover_detail_and_sanitized_persistence(self) -> None:
        requests: list[dict] = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if urlsplit(self.path).path in {"/cover.png", "/detail.png"}:
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Content-Length", str(len(PNG)))
                    self.end_headers()
                    self.wfile.write(PNG)
                    return
                data = {"is_logged_in": True} if self.path.endswith("/login/status") else {"status": "healthy"}
                self.respond(data)

            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length))
                requests.append({"path": self.path, "payload": payload})
                origin = f"http://127.0.0.1:{self.server.server_port}"
                if self.path.endswith("/feeds/search"):
                    self.respond({
                        "feeds": [{
                            "id": "public-note-1",
                            "xsecToken": "transient-secret-token",
                            "modelType": "note",
                            "noteCard": {
                                "type": "normal",
                                "displayTitle": "公开测试标题",
                                "user": {"nickname": "公开作者", "avatar": "https://private.example/avatar"},
                                "interactInfo": {"likedCount": "12", "commentCount": "3", "collectedCount": "8"},
                                "cover": {"urlDefault": f"{origin}/cover.png?signature=secret"},
                            },
                        }],
                    })
                    return
                self.respond({
                    "data": {
                        "note": {
                            "noteId": "public-note-1",
                            "title": "公开测试标题",
                            "desc": "公开正文摘要",
                            "type": "normal",
                            "user": {"nickname": "公开作者"},
                            "interactInfo": {"likedCount": "12", "collectedCount": "8"},
                            "imageList": [{"urlDefault": f"{origin}/detail.png?signature=secret"}],
                        }
                    }
                })

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
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "研究工作流",
                        "--endpoint",
                        f"http://127.0.0.1:{server.server_port}",
                        "--timeout",
                        "3",
                        "--out",
                        str(root / "xiaohongshu-search.json"),
                        "--cover-pool",
                        "1",
                        "--candidate-note-id",
                        "public-note-1",
                        "--images-per-candidate",
                        "1",
                        "--detail-interval",
                        "0",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("首次默认推荐 25 条", result.stderr)
                self.assertIn("本次请求 25 条", result.stderr)
                summary = json.loads(result.stdout)
                self.assertEqual(summary["collected"], 1)
                self.assertEqual(summary["cover_pool"], 1)
                self.assertEqual(summary["visual_candidates"], 1)
                self.assertTrue((root / "cover-pool.json").is_file())
                self.assertTrue((root / "visual-candidates.json").is_file())
                self.assertTrue((root / "visual-candidates/public-note-1/01.png").is_file())
                persisted = "".join(
                    path.read_text(encoding="utf-8", errors="ignore")
                    for path in root.rglob("*.json")
                )
                self.assertNotIn("transient-secret-token", persisted)
                self.assertNotIn("signature=secret", persisted)
                self.assertNotIn("private.example", persisted)
        finally:
            server.shutdown()
            server.server_close()

        search = next(item for item in requests if item["path"].endswith("/feeds/search"))
        detail = next(item for item in requests if item["path"].endswith("/feeds/detail"))
        self.assertEqual(search["payload"]["max_items"], 25)
        self.assertEqual(detail["payload"]["feed_id"], "public-note-1")


if __name__ == "__main__":
    unittest.main()
