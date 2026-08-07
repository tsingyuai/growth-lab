from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("collect_x.py")
SPEC = importlib.util.spec_from_file_location("collect_x", SCRIPT)
collector = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(collector)


class XCollectorTests(unittest.TestCase):
    def test_exact_query_is_built_inside_python(self) -> None:
        self.assertEqual(
            collector.build_search_query("目标短语", True, ["排除短语"]),
            '"目标短语" -"排除短语"',
        )

    def test_strict_filter_rejects_reverse_and_algorithmic_matches(self) -> None:
        posts = [
            {"post_id": "1", "text": "目标短语 example"},
            {"post_id": "2", "text": "排除短语 example"},
            {"post_id": "3", "text": "unrelated"},
        ]
        result = collector.strict_filter(posts, "目标短语", True, ["排除短语"])
        self.assertEqual([row["post_id"] for row in result], ["1"])

    def test_config_precedence_and_secret_free_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env").write_text("SOCIAL_PROXY_MODE=direct\n", encoding="utf-8")
            (root / ".env.local").write_text(
                "SOCIAL_PROXY_MODE=explicit\nSOCIAL_PROXY_URL=http://127.0.0.1:7890\n",
                encoding="utf-8",
            )
            values = collector.resolved_config(root, {"SOCIAL_PROXY_MODE": "system"})
        self.assertEqual(values["SOCIAL_PROXY_MODE"], "system")
        self.assertIn("SOCIAL_PROXY_URL", values)

    def test_direct_route_uses_direct_only(self) -> None:
        async def probe(route: str) -> bool:
            return route == "direct"

        route, report = asyncio.run(collector.resolve_route("direct", True, probe))
        self.assertEqual(route, "direct")
        self.assertEqual(report["selected"], "direct")

    def test_explicit_route_uses_shared_proxy(self) -> None:
        async def probe(route: str) -> bool:
            return route == "explicit"

        route, report = asyncio.run(collector.resolve_route("explicit", True, probe))
        self.assertEqual(route, "explicit")
        self.assertTrue(report["explicit"])

    def test_auto_route_falls_back_to_explicit_proxy(self) -> None:
        attempted: list[str] = []

        async def probe(route: str) -> bool:
            attempted.append(route)
            return route == "explicit"

        route, report = asyncio.run(collector.resolve_route("auto", True, probe))
        self.assertEqual(route, "explicit")
        self.assertEqual(attempted, ["direct", "explicit"])
        self.assertEqual(report["selected"], "explicit")

    def test_missing_proxy_is_actionable(self) -> None:
        async def probe(route: str) -> bool:
            return False

        with self.assertRaisesRegex(collector.CollectorError, "SOCIAL_PROXY_URL"):
            asyncio.run(collector.resolve_route("explicit", False, probe))

    def test_proxy_credentials_are_split_from_server(self) -> None:
        proxy = collector.playwright_proxy(
            "http://user:private%20password@127.0.0.1:7890",
            "127.0.0.1,localhost,::1",
        )
        self.assertEqual(proxy["server"], "http://127.0.0.1:7890")
        self.assertEqual(proxy["username"], "user")
        self.assertEqual(proxy["password"], "private password")
        self.assertEqual(proxy["bypass"], "127.0.0.1,localhost,::1")

    def test_socks5_proxy_is_supported(self) -> None:
        proxy = collector.playwright_proxy(
            "socks5://127.0.0.1:10808", "127.0.0.1,localhost,::1"
        )
        self.assertEqual(proxy["server"], "socks5://127.0.0.1:10808")

    def test_proxy_bypass_requires_all_loopback_hosts(self) -> None:
        with self.assertRaisesRegex(collector.CollectorError, "SOCIAL_PROXY_BYPASS"):
            collector.validate_loopback_bypass("localhost")

    def test_system_proxy_is_resolved_without_reporting_it(self) -> None:
        secret_proxy = "http://user:secret@127.0.0.1:7890"
        with mock.patch.object(
            collector.urllib.request, "getproxies", return_value={"https": secret_proxy}
        ):
            self.assertEqual(
                collector.system_proxy_url("https://x.com/robots.txt"), secret_proxy
            )

    def test_original_media_url_requests_full_size(self) -> None:
        url = "https://pbs.twimg.com/media/example.jpg?format=jpg&name=small"
        self.assertIn("name=orig", collector.original_media_url(url))

    def test_extractor_is_a_complete_expression(self) -> None:
        self.assertTrue(collector.EXTRACT_POSTS_JS.strip().endswith(".filter(Boolean)"))
        self.assertNotIn('.filter(Boolean)+', collector.EXTRACT_POSTS_JS)

    def test_normalize_rejects_non_x_urls_and_unsafe_media(self) -> None:
        self.assertIsNone(
            collector.normalize_post(
                {"post_id": "123", "url": "https://example.com/demo", "text": "demo"},
                "demo",
            )
        )
        row = collector.normalize_post(
            {
                "post_id": "123",
                "url": "https://x.com/demo/status/123",
                "text": "demo",
                "media_urls": [
                    "https://pbs.twimg.com/media/example.jpg",
                    "https://example.com/secret.jpg",
                ],
            },
            "demo",
        )
        self.assertIsNotNone(row)
        self.assertEqual(row["media_urls"], ["https://pbs.twimg.com/media/example.jpg"])

    def test_normalize_preserves_original_language_and_translation_slots(self) -> None:
        row = collector.normalize_post(
            {
                "post_id": "123",
                "url": "https://x.com/example/status/123",
                "text": "A small product update",
                "original_language": "en-US",
            },
            "product",
        )
        self.assertEqual(row["text"], "A small product update")
        self.assertEqual(row["original_text"], "A small product update")
        self.assertEqual(row["original_language"], "en-us")
        self.assertEqual(row["language_detection"], "x-dom")
        self.assertEqual(row["zh_translation"], "")
        self.assertEqual(row["translation_method"], "pending")

    def test_chinese_original_is_saved_as_its_own_translation(self) -> None:
        row = collector.normalize_post(
            {
                "post_id": "124",
                "url": "https://x.com/example/status/124",
                "text": "这是中文原文",
            },
            "产品",
        )
        self.assertEqual(row["original_language"], "zh")
        self.assertEqual(row["zh_translation"], "这是中文原文")
        self.assertEqual(row["translation_method"], "original-is-chinese")

    def test_translation_batch_updates_only_foreign_items(self) -> None:
        items = [
            {
                "post_id": "1",
                "original_text": "Hello",
                "original_language": "en",
                "translation_method": "pending",
                "zh_translation": "",
            },
            {
                "post_id": "2",
                "original_text": "你好",
                "original_language": "zh",
                "translation_method": "original-is-chinese",
                "zh_translation": "你好",
            },
        ]
        response = {
            "output_text": '[{"post_id":"1","zh_translation":"你好"}]'
        }
        fake_response = mock.MagicMock()
        fake_response.__enter__.return_value.read.return_value = json.dumps(response).encode()
        with mock.patch.object(collector.urllib.request, "urlopen", return_value=fake_response):
            collector.translate_items_zh(
                items,
                {"OPENAI_API_KEY": "test", "OPENAI_TEXT_MODEL": "test-model"},
            )
        self.assertEqual(items[0]["zh_translation"], "你好")
        self.assertEqual(items[0]["translation_method"], "openai:test-model")
        self.assertEqual(items[1]["translation_method"], "original-is-chinese")

    def test_default_limit_matches_social_batch(self) -> None:
        self.assertEqual(collector.build_parser().parse_args(["topic"]).limit, 25)

    def test_browser_auto_falls_back_to_edge(self) -> None:
        with mock.patch.object(collector.Path, "is_file", side_effect=[False, False, True]):
            family, path = collector.resolve_browser({"SOCIAL_BROWSER_FAMILY": "auto"})
        self.assertEqual(family, "edge")
        self.assertEqual(path.name.lower(), "msedge.exe")

    def test_explicit_edge_path_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            edge = Path(temp_dir) / "msedge.exe"
            edge.touch()
            family, path = collector.resolve_browser(
                {"SOCIAL_BROWSER_FAMILY": "edge", "SOCIAL_BROWSER_PATH": str(edge)}
            )
        self.assertEqual(family, "edge")
        self.assertEqual(path, edge)

    def test_system_login_inherits_os_rules_without_proxy_argument(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            collector.subprocess, "Popen"
        ) as popen:
            browser = Path(temp_dir) / "msedge.exe"
            profile = Path(temp_dir) / "profile"
            collector.launch_detached_login(
                browser,
                profile,
                "system",
                None,
                "127.0.0.1,localhost,::1",
                19222,
            )
        arguments = popen.call_args.args[0]
        self.assertNotIn("--proxy-server", " ".join(arguments))
        self.assertIn("--remote-debugging-address=127.0.0.1", arguments)
        self.assertIn("--remote-debugging-port=19222", arguments)
        self.assertIn("https://x.com/i/flow/login", arguments)

    def test_cdp_port_is_loopback_endpoint_and_validated(self) -> None:
        self.assertEqual(collector.validate_cdp_port("19222"), 19222)
        self.assertEqual(collector.cdp_endpoint(19222), "http://127.0.0.1:19222")
        with self.assertRaisesRegex(collector.CollectorError, "1024"):
            collector.validate_cdp_port("80")

    def test_profile_must_stay_outside_repository(self) -> None:
        with self.assertRaisesRegex(collector.CollectorError, "仓库外"):
            collector.ensure_external_profile(collector.ROOT / "profile", collector.ROOT)

    def test_probe_url_must_target_x(self) -> None:
        with self.assertRaisesRegex(collector.CollectorError, "x.com"):
            collector.validate_probe_url("https://example.com/robots.txt")


if __name__ == "__main__":
    unittest.main()
