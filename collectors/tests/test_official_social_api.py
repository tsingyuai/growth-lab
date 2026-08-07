from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


COLLECTORS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COLLECTORS))

import official_social_api as api  # noqa: E402


class Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


class OfficialSocialApiProbeTest(unittest.TestCase):
    def test_missing_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.assertEqual(api.probe_tiktok(root, {})["status"], "missing-configuration")
            self.assertEqual(api.probe_instagram(root, {})["status"], "missing-configuration")

    @patch.object(api, "build_remote_opener")
    def test_tokens_use_authorization_header_and_are_not_persisted(self, opener_builder) -> None:
        opener_builder.return_value.open.side_effect = [
            Response({"data": {"user": {"open_id": "oid", "display_name": "Demo"}}, "error": {"code": "ok"}}),
            Response({"user_id": "123", "username": "demo"}),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tiktok = api.probe_tiktok(root, {"TIKTOK_ACCESS_TOKEN": "tiktok-secret"})
            instagram = api.probe_instagram(root, {"INSTAGRAM_ACCESS_TOKEN": "instagram-secret"})
        self.assertEqual(tiktok["status"], "verified")
        self.assertEqual(instagram["status"], "verified")
        serialized = json.dumps([tiktok, instagram])
        self.assertNotIn("tiktok-secret", serialized)
        self.assertNotIn("instagram-secret", serialized)
        first_request = opener_builder.return_value.open.call_args_list[0].args[0]
        second_request = opener_builder.return_value.open.call_args_list[1].args[0]
        self.assertEqual(first_request.get_header("Authorization"), "Bearer tiktok-secret")
        self.assertEqual(second_request.get_header("Authorization"), "Bearer instagram-secret")

    def test_explicit_proxy_requires_valid_http_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaises(api.ProxyConfigurationError):
                api.build_remote_opener(
                    root,
                    {"SOCIAL_PROXY_MODE": "explicit", "SOCIAL_PROXY_URL": "socks5://127.0.0.1:1080"},
                )
            opener = api.build_remote_opener(
                root,
                {"SOCIAL_PROXY_MODE": "explicit", "SOCIAL_PROXY_URL": "http://127.0.0.1:7890"},
            )
        handlers = [handler for handler in opener.handlers if hasattr(handler, "proxies")]
        self.assertTrue(any(handler.proxies.get("https") == "http://127.0.0.1:7890" for handler in handlers))


if __name__ == "__main__":
    unittest.main()
