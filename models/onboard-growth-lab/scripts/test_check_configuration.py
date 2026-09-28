from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import check_configuration as checker


class ConfigurationAuditTest(unittest.TestCase):
    def test_missing_configuration_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = checker.audit(Path(temp_dir), {})
        self.assertEqual(result["xiaohongshu"]["status"], "missing-configuration")
        self.assertEqual(result["xiaohongshu"]["recommended"], 25)
        self.assertFalse(result["xiaohongshu"]["requires_api_key"])
        self.assertEqual(result["image_generation"]["status"], "optional-missing")
        self.assertEqual(result["configuration_guide"], "CONFIGURATION.md")

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
                ]),
                encoding="utf-8",
            )
            result = checker.audit(root, {})
        serialized = json.dumps(result)
        self.assertEqual(result["xiaohongshu"]["status"], "configured-not-verified")
        self.assertEqual(result["image_generation"]["configured_providers"], ["openai"])
        self.assertNotIn(secret, serialized)
        self.assertNotIn("not-a-real-cookie", serialized)


if __name__ == "__main__":
    unittest.main()
