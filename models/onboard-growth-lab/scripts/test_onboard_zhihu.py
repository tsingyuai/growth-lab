#!/usr/bin/env python3
"""Tests for the Zhihu onboarding state machine."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("onboard_zhihu.py")


FAKE_CLI = r"""#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]
log = os.environ.get("FAKE_ZHIHU_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(args) + "\n")

if args == ["version"]:
    print(json.dumps({"version": "0.6.3"}))
elif args == ["capabilities"]:
    print(json.dumps({"commands": [
        {"name": "search zhihu"}, {"name": "hot"},
        {"name": "question answers"}, {"name": "me contents"}
    ]}))
elif args == ["auth", "status"]:
    print(json.dumps({"configured": True, "source": "test-keychain"}))
elif args == ["auth", "status", "--verify"]:
    print(json.dumps({"ok": True, "configured": True, "source": "test-keychain"}))
elif args[:3] == ["auth", "set", "--secret-stdin"]:
    secret = sys.stdin.read().strip()
    print(json.dumps({"ok": True, "configured": bool(secret), "source": "test-keychain"}))
elif args[:2] == ["search", "zhihu"]:
    print(json.dumps({"Code": 0, "Data": {"Items": [{
        "Title": "验证内容",
        "Url": "https://www.zhihu.com/question/123"
    }]}}))
elif args[:1] == ["hot"]:
    print(json.dumps({"Code": 0, "Data": {"Items": [{
        "Title": "热榜验证",
        "Url": "https://www.zhihu.com/question/456"
    }]}}))
else:
    print(json.dumps({"error": "unexpected", "args": args})); sys.exit(9)
"""


class ZhihuOnboardingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.fake_cli = self.root / "zhihu-cli"
        self.fake_cli.write_text(FAKE_CLI, encoding="utf-8")
        self.fake_cli.chmod(0o755)
        self.log = self.root / "commands.jsonl"
        self.env = os.environ.copy()
        self.env["FAKE_ZHIHU_LOG"] = str(self.log)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_onboard(
        self,
        *args: str,
        stdin: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
            env=self.env,
        )

    def commands(self) -> list[list[str]]:
        if not self.log.is_file():
            return []
        return [
            json.loads(line)
            for line in self.log.read_text(encoding="utf-8").splitlines()
        ]

    def test_status_reports_verification_as_next_action(self) -> None:
        completed = self.run_onboard("status", "--binary", str(self.fake_cli))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["readiness"], "ready-to-verify")
        self.assertEqual(payload["action"]["next_action"], "run_minimal_content_read")
        self.assertIn("verify --query", payload["action"]["command"])

    def test_install_requires_confirmation(self) -> None:
        completed = self.run_onboard("install")
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["error"]["code"], "CONFIRMATION_REQUIRED")

    def test_auth_reads_secret_from_stdin_without_echo(self) -> None:
        secret = "test-secret-must-not-appear"
        completed = self.run_onboard("auth", "--binary", str(self.fake_cli), stdin=secret)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertNotIn(secret, completed.stdout)
        self.assertNotIn(secret, completed.stderr)
        self.assertIn(["auth", "set", "--secret-stdin"], self.commands())

    def test_verify_performs_online_check_and_real_read(self) -> None:
        completed = self.run_onboard(
            "verify",
            "--binary",
            str(self.fake_cli),
            "--query",
            "AI Agent",
            "--yes",
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["readiness"], "ready")
        self.assertTrue(payload["auth_verified"])
        self.assertEqual(payload["content_read"]["type"], "search")
        self.assertEqual(payload["content_read"]["count"], 1)
        self.assertEqual(payload["status"]["readiness"], "ready")
        self.assertIn(["auth", "status", "--verify"], self.commands())
        self.assertTrue(any(command[:2] == ["search", "zhihu"] for command in self.commands()))

    def test_verify_rejects_empty_query(self) -> None:
        completed = self.run_onboard(
            "verify",
            "--binary",
            str(self.fake_cli),
            "--query",
            "",
            "--yes",
        )
        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENTS")

    def test_verify_requires_confirmation(self) -> None:
        completed = self.run_onboard(
            "verify",
            "--binary",
            str(self.fake_cli),
            "--hot",
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["error"]["code"], "CONFIRMATION_REQUIRED")


if __name__ == "__main__":
    unittest.main()
