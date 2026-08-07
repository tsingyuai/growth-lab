from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import check_configuration as checker


class ConfigurationAuditTest(unittest.TestCase):
    def test_running_social_adapter_is_not_reported_as_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            checker,
            "local_service_reachable",
            side_effect=lambda endpoint: endpoint.endswith(":18064"),
        ):
            result = checker.audit(Path(temp_dir), {})
        self.assertEqual(result["tiktok"]["status"], "configured-not-verified")
        self.assertEqual(result["instagram"]["status"], "missing-runtime")
        self.assertEqual(result["network_access"]["status"], "auto-configured-not-verified")
        self.assertIn(
            result["x"]["status"],
            {"missing-runtime", "missing-browser", "needs-visible-login", "configured-not-verified"},
        )
        self.assertTrue(result["x"]["preflight_required"])

    def test_missing_configuration_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = checker.audit(Path(temp_dir), {}, probe_services=False)
        self.assertEqual(result["xiaohongshu"]["status"], "missing-configuration")
        self.assertEqual(result["xiaohongshu"]["recommended"], 25)
        self.assertFalse(result["xiaohongshu"]["requires_api_key"])
        self.assertEqual(result["image_generation"]["status"], "optional-missing")
        self.assertEqual(result["tiktok"]["status"], "missing-runtime")
        self.assertEqual(result["instagram"]["status"], "missing-runtime")
        self.assertEqual(result["configuration_guide"], "CONFIGURATION.md")
        self.assertIn(result["video_generation"]["status"], {"optional-missing-runtime", "configured-not-verified"})

    def test_configured_secret_is_never_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            service = root / "service.exe"
            login = root / "login.exe"
            cookie = root / "cookies.json"
            service.touch()
            login.touch()
            cookie.write_text("not-a-real-cookie", encoding="utf-8")
            secret = "test-secret-value-must-not-appear"
            (root / ".env.local").write_text(
                "\n".join([
                    f"XHS_MCP_BINARY={service}",
                    f"XHS_MCP_LOGIN_BINARY={login}",
                    f"XHS_MCP_COOKIES_PATH={cookie}",
                    f"OPENAI_API_KEY={secret}",
                    f"TIKTOK_ACCESS_TOKEN={secret}",
                    f"INSTAGRAM_ACCESS_TOKEN={secret}",
                    f"X_USER_ACCESS_TOKEN={secret}",
                    "WECHAT_APP_ID=test-app",
                    f"WECHAT_APP_SECRET={secret}",
                    "TIKTOK_MCP_ENDPOINT=http://127.0.0.1:18064",
                    "INSTAGRAM_MCP_ENDPOINT=http://127.0.0.1:18065",
                    "SOCIAL_PROXY_MODE=explicit",
                    f"SOCIAL_PROXY_URL=http://proxy-user:{secret}@127.0.0.1:7890",
                    "SOCIAL_PROXY_BYPASS=127.0.0.1,localhost,::1",
                ]),
                encoding="utf-8",
            )
            result = checker.audit(root, {}, probe_services=False)
        serialized = json.dumps(result)
        self.assertEqual(result["xiaohongshu"]["status"], "configured-not-verified")
        self.assertEqual(result["image_generation"]["configured_providers"], ["openai"])
        self.assertEqual(result["tiktok"]["status"], "missing-runtime")
        self.assertEqual(result["instagram"]["status"], "missing-runtime")
        self.assertEqual(result["tiktok"]["official_account_api"]["status"], "configured-not-verified")
        self.assertEqual(result["instagram"]["official_account_api"]["status"], "configured-not-verified")
        self.assertEqual(result["x"]["official_publishing_api"]["status"], "configured-not-verified")
        self.assertEqual(result["wechat"]["official_account_api"]["status"], "configured-not-verified")
        self.assertEqual(result["network_access"]["status"], "explicit-configured-not-verified")
        self.assertEqual(result["network_access"]["proxy_url"], "present-not-displayed")
        self.assertNotIn(secret, serialized)
        self.assertNotIn("not-a-real-cookie", serialized)

    def test_xhs_standard_external_client_is_auto_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            root = base / "repo"
            home = base / "home"
            client = home / ".growth-lab" / "clients" / "xiaohongshu-mcp"
            legacy = home / ".xhs-autopilot" / "xiaohongshu-mcp"
            root.mkdir()
            client.mkdir(parents=True)
            legacy.mkdir(parents=True)
            (client / "xiaohongshu-mcp-windows-amd64.exe").touch()
            (client / "xiaohongshu-login-windows-amd64.exe").touch()
            (legacy / "cookies.json").write_text("private", encoding="utf-8")
            result = checker.audit(root, {"USERPROFILE": str(home)}, probe_services=False)
        self.assertEqual(result["xiaohongshu"]["status"], "configured-not-verified")

    def test_x_uses_shared_proxy_without_reporting_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            root = base / "repo"
            root.mkdir()
            python = root / "python.exe"
            edge = root / "msedge.exe"
            profile = base / "x-profile"
            python.touch()
            edge.touch()
            profile.mkdir()
            secret = "x-proxy-password"
            (root / ".env.local").write_text(
                "\n".join([
                    f"X_BROWSER_PYTHON={python}",
                    "SOCIAL_BROWSER_FAMILY=edge",
                    f"SOCIAL_BROWSER_PATH={edge}",
                    f"X_BROWSER_PROFILE_DIR={profile}",
                    "SOCIAL_PROXY_MODE=explicit",
                    f"SOCIAL_PROXY_URL=http://user:{secret}@127.0.0.1:7890",
                    "SOCIAL_PROXY_BYPASS=127.0.0.1,localhost,::1",
                ]),
                encoding="utf-8",
            )
            result = checker.audit(root, {}, probe_services=False)
        serialized = json.dumps(result)
        self.assertEqual(result["x"]["status"], "configured-not-verified")
        self.assertEqual(result["x"]["network_mode"], "explicit")
        self.assertTrue(result["x"]["shared_proxy_configured"])
        self.assertEqual(result["x"]["profile_location"], "external")
        self.assertEqual(result["x"]["runtime"], "present-not-verified")
        self.assertEqual(result["x"]["browser_family"], "edge")
        self.assertTrue(result["x"]["cdp"]["loopback_only"])
        self.assertEqual(result["x"]["cdp"]["endpoint"], "127.0.0.1:19222")
        self.assertNotIn(secret, serialized)

    def test_x_profile_inside_repository_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            python = root / "python.exe"
            edge = root / "msedge.exe"
            profile = root / "x-profile"
            python.touch()
            edge.touch()
            profile.mkdir()
            result = checker.audit(
                root,
                {
                    "X_BROWSER_PYTHON": str(python),
                    "SOCIAL_BROWSER_FAMILY": "edge",
                    "SOCIAL_BROWSER_PATH": str(edge),
                    "X_BROWSER_PROFILE_DIR": str(profile),
                },
                probe_services=False,
            )
        self.assertEqual(result["x"]["status"], "invalid-profile-location")

    def test_proxy_cannot_capture_loopback_services(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = checker.audit(
                Path(temp_dir),
                {
                    "SOCIAL_PROXY_MODE": "explicit",
                    "SOCIAL_PROXY_URL": "http://127.0.0.1:7890",
                    "SOCIAL_PROXY_BYPASS": "localhost",
                },
                probe_services=False,
            )
        self.assertEqual(result["network_access"]["status"], "invalid-configuration")
        self.assertEqual(result["network_access"]["loopback_bypass"], "invalid")

    def test_invalid_x_cdp_port_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            python = root / "python.exe"
            edge = root / "msedge.exe"
            python.touch()
            edge.touch()
            result = checker.audit(
                root,
                {
                    "X_BROWSER_PYTHON": str(python),
                    "SOCIAL_BROWSER_FAMILY": "edge",
                    "SOCIAL_BROWSER_PATH": str(edge),
                    "X_BROWSER_CDP_PORT": "80",
                },
                probe_services=False,
            )
        self.assertEqual(result["x"]["status"], "invalid-cdp-port")

    def test_video_runtime_is_optional_and_detected_without_running_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = root / "video-python.exe"
            runtime.touch()
            result = checker.audit(
                root,
                {"VIDEO_RENDERER_PYTHON": str(runtime)},
                probe_services=False,
            )
        self.assertEqual(result["video_generation"]["status"], "configured-not-verified")
        self.assertEqual(result["video_generation"]["ffmpeg"], "runtime-managed")

    def test_local_tts_runtime_is_optional_and_detected_without_running_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = root / "tts-python.exe"
            runtime.touch()
            result = checker.audit(
                root,
                {"SOCIAL_TTS_PYTHON": str(runtime)},
                probe_services=False,
            )
        self.assertEqual(result["video_generation"]["local_tts"], "present-not-verified")

    def test_seedance_configuration_is_optional_and_redacted(self) -> None:
        result = checker.audit(
            Path("."),
            {
                "ARK_API_KEY": "private-key-value",
                "ARK_BASE_URL": "https://ark.example/api/v3",
                "SEEDANCE_MODEL_ENDPOINT": "ep-video-test",
            },
            probe_services=False,
        )
        seedance = result["video_generation"]["seedance_broll"]
        self.assertEqual(seedance["status"], "configured-not-verified")
        self.assertEqual(seedance["missing"], [])
        self.assertNotIn("private-key-value", json.dumps(result))
        self.assertFalse(seedance["live_generation_verified"])


if __name__ == "__main__":
    unittest.main()
