from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("run_acceptance.py")
SPEC = importlib.util.spec_from_file_location("run_acceptance", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


class AcceptanceRunnerTests(unittest.TestCase):
    def test_run_directory_must_be_new_or_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run = runner.ensure_run_dir(root, "valid-run")
            (run / "evidence.txt").write_text("evidence", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "已存在且非空"):
                runner.ensure_run_dir(root, "valid-run")

    def test_environment_is_redacted(self) -> None:
        result = runner.redacted_environment(
            {"OPENAI_API_KEY": "secret-value", "SOCIAL_PROXY_MODE": "system"}
        )
        self.assertEqual(result["OPENAI_API_KEY"], "present")
        self.assertNotIn("secret-value", str(result))
        self.assertEqual(result["SOCIAL_PROXY_MODE"], "system")

    def test_secret_scanner_flags_credential_shaped_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "bad.log").write_text("sk-abcdefghijklmnopqrstuvwxyz123456", encoding="utf-8")
            self.assertEqual(runner.scan_for_secrets(root), ["bad.log"])

    def test_step_timeout_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.run_step(
                Path(temp_dir),
                "timeout",
                [runner.sys.executable, "-c", "import time; time.sleep(2)"],
                0.05,
            )
        self.assertEqual(result.status, "FAIL")
        self.assertIn("超时", result.message)


if __name__ == "__main__":
    unittest.main()
