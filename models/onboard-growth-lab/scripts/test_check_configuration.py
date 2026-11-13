from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import check_configuration as checker


class ConfigurationAuditTest(unittest.TestCase):
    def test_missing_configuration_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = checker.audit(
                root,
                {"ZHIHU_CLI_HOME": str(root / "missing-zhihu-cli")},
            )
        self.assertEqual(result["xiaohongshu"]["status"], "missing-configuration")
        self.assertEqual(result["xiaohongshu"]["recommended"], 25)
        self.assertFalse(result["xiaohongshu"]["requires_api_key"])
        self.assertEqual(result["zhihu"]["status"], "missing-cli")
        self.assertEqual(result["zhihu"]["readiness"], "missing-cli")
        self.assertEqual(result["zhihu"]["next_action"], "request_install_consent")
        self.assertIn("onboard_zhihu.py install --yes", result["zhihu"]["command"])
        self.assertEqual(result["image_generation"]["status"], "optional-missing")
        self.assertEqual(result["configuration_guide"], "CONFIGURATION.md")

    def test_configured_secret_is_never_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            service = root / "service.exe"
            login = root / "login.exe"
            cookie = root / "cookies.json"
            zhihu = root / "zhihu-cli"
            service.touch()
            login.touch()
            cookie.write_text("not-a-real-cookie", encoding="utf-8")
            zhihu.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "args = sys.argv[1:]\n"
                "if args == ['version']:\n"
                "    print(json.dumps({'version': '0.6.3'}))\n"
                "elif args == ['capabilities']:\n"
                "    print(json.dumps({'commands': []}))\n"
                "elif args == ['auth', 'status']:\n"
                "    print(json.dumps({'configured': True, 'source': 'test'}))\n"
                "else:\n"
                "    print(json.dumps({'error': 'unexpected'})); sys.exit(1)\n",
                encoding="utf-8",
            )
            zhihu.chmod(0o755)
            secret = "test-secret-value-must-not-appear"
            (root / ".env.local").write_text(
                "\n".join([
                    f"XHS_MCP_BINARY={service}",
                    f"XHS_MCP_LOGIN_BINARY={login}",
                    f"XHS_MCP_COOKIES_PATH={cookie}",
                    f"ZHIHU_CLI_BIN={zhihu}",
                    f"OPENAI_API_KEY={secret}",
                ]),
                encoding="utf-8",
            )
            result = checker.audit(root, {})
        serialized = json.dumps(result)
        self.assertEqual(result["xiaohongshu"]["status"], "configured-not-verified")
        self.assertEqual(result["zhihu"]["status"], "configured-not-verified")
        self.assertEqual(result["zhihu"]["readiness"], "ready-to-verify")
        self.assertEqual(result["zhihu"]["next_action"], "run_minimal_content_read")
        self.assertIn("onboard_zhihu.py verify", result["zhihu"]["command"])
        self.assertEqual(result["zhihu"]["version"], "0.6.3")
        self.assertEqual(result["image_generation"]["configured_providers"], ["openai"])
        self.assertNotIn(secret, serialized)
        self.assertNotIn("not-a-real-cookie", serialized)

    def test_missing_configured_zhihu_binary_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env.local").write_text(
                "ZHIHU_CLI_BIN=/does/not/exist/zhihu-cli\n",
                encoding="utf-8",
            )
            result = checker.audit(root, {})
        self.assertEqual(result["zhihu"]["status"], "configured-binary-not-found")


if __name__ == "__main__":
    unittest.main()
