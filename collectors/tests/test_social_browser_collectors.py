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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import social_browser_collector as collector  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class SocialBrowserCollectorFlowTest(unittest.TestCase):
    def test_rejects_unsafe_adapter_identity_and_url(self) -> None:
        spec = collector.PlatformSpec(
            platform="tiktok",
            endpoint_env="TIKTOK_MCP_ENDPOINT",
            default_endpoint="http://127.0.0.1:18064",
            public_hosts=("tiktok.com",),
        )
        self.assertIsNone(
            collector.sanitize_item(
                {"content_id": "../../secret", "public_url": "https://www.tiktok.com/video/1"},
                spec,
            )
        )
        self.assertIsNone(
            collector.sanitize_item(
                {"content_id": "safe-id", "public_url": "https://example.com/video/1"},
                spec,
            )
        )
        self.assertFalse(
            collector._asset_url_allowed(
                "https://127.0.0.1/private", "http://127.0.0.1:18064"
            )
        )

    def test_review_selection_file_uses_public_ids_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "selection.json"
            path.write_text(json.dumps({"content_ids": ["public-1", "public-2"]}), encoding="utf-8")
            self.assertEqual(
                collector.wait_for_review_selection(path, 1),
                ["public-1", "public-2"],
            )

    def run_platform(self, platform: str, public_url: str) -> None:
        requests: list[dict] = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = urlsplit(self.path).path
                if path in {"/cover.png", "/detail.png"}:
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Content-Length", str(len(PNG)))
                    self.end_headers()
                    self.wfile.write(PNG)
                    return
                data = {"is_logged_in": True} if path.endswith("/login/status") else {"status": "healthy"}
                self.respond(data)

            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length))
                requests.append({"path": self.path, "payload": payload})
                origin = f"http://127.0.0.1:{self.server.server_port}"
                if self.path.endswith("/content/search"):
                    self.respond({
                        "items": [{
                            "content_id": "public-content-1",
                            "public_url": public_url,
                            "title": "Public test title",
                            "content_type": "video" if platform == "tiktok" else "reel",
                            "author": "public-author",
                            "visible_engagement": {"likes": "12", "comments": "3", "views": "80"},
                            "cover_url": f"{origin}/cover.png?signature=secret",
                            "access_ref": "transient-secret-ref",
                        }]
                    })
                    return
                self.respond({
                    "content": {
                        "content_id": "public-content-1",
                        "public_url": public_url,
                        "title": "Public test title",
                        "description": "Public description",
                        "content_type": "video" if platform == "tiktok" else "reel",
                        "author": "public-author",
                        "visible_engagement": {"likes": "12", "comments": "3"},
                    },
                    "media": [{"kind": "keyframe", "url": f"{origin}/detail.png?signature=secret"}],
                })

            def respond(self, data):
                body = json.dumps({"success": True, "data": data}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, _format, *_args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output = Path(temp_dir)
                script = ROOT / "collectors" / f"{platform}-mcp" / "scripts" / f"collect_{platform}.py"
                result = subprocess.run(
                    [
                        sys.executable,
                        str(script),
                        "research workflow",
                        "--endpoint",
                        f"http://127.0.0.1:{server.server_port}",
                        "--limit",
                        "1",
                        "--cover-pool",
                        "1",
                        "--candidate-content-id",
                        "public-content-1",
                        "--assets-per-candidate",
                        "1",
                        "--detail-interval",
                        "0",
                        "--out",
                        str(output / f"{platform}-search.json"),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                summary = json.loads(result.stdout)
                self.assertEqual(summary["collected"], 1)
                self.assertEqual(summary["cover_pool"], 1)
                self.assertEqual(summary["visual_candidates"], 1)
                self.assertTrue((output / "cover-pool.json").is_file())
                self.assertTrue((output / "visual-candidates.json").is_file())
                persisted = "".join(
                    path.read_text(encoding="utf-8", errors="ignore")
                    for path in output.rglob("*.json")
                )
                self.assertNotIn("transient-secret-ref", persisted)
                self.assertNotIn("signature=secret", persisted)
        finally:
            server.shutdown()
            server.server_close()

        search = next(item for item in requests if item["path"].endswith("/content/search"))
        detail = next(item for item in requests if item["path"].endswith("/content/detail"))
        self.assertEqual(search["payload"]["max_items"], 1)
        self.assertEqual(detail["payload"]["content_id"], "public-content-1")

    def test_tiktok_continuous_flow(self) -> None:
        self.run_platform("tiktok", "https://www.tiktok.com/@demo/video/public-content-1")

    def test_instagram_continuous_flow(self) -> None:
        self.run_platform("instagram", "https://www.instagram.com/reel/public-content-1/")


if __name__ == "__main__":
    unittest.main()
