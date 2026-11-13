#!/usr/bin/env python3
"""Tests for the official Zhihu CLI collector."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("zhihu_cli.py")


FAKE_CLI = r"""#!/usr/bin/env python3
import json
import sys

args = sys.argv[1:]
if args == ["version"]:
    print(json.dumps({"version": "0.6.3", "platform": "test/arm64"}))
elif args == ["capabilities"]:
    print(json.dumps({"version": "0.6.3", "commands": [
        {"name": "search zhihu"}, {"name": "hot"}, {"name": "question answers"}
    ]}))
elif args == ["auth", "status"]:
    print(json.dumps({"configured": True, "source": "test", "masked_value": "***"}))
elif args[:2] == ["search", "zhihu"]:
    query = args[args.index("--query") + 1]
    print(json.dumps({"Code": 0, "Message": "success", "Data": {"Items": [{
        "Title": "如何选择 AI 产品？",
        "ContentType": "Answer",
        "ContentID": "123",
        "ContentText": "<em>先定义用户问题</em>，再比较方案。",
        "Url": "https://www.zhihu.com/answer/123?utm_source=openapi&utm_medium=platform",
        "VoteUpCount": 42,
        "CommentCount": 7,
        "AuthorName": "研究者",
        "AuthorityLevel": "3",
        "EditTime": 1710000000
    }]}}))
elif args[:1] == ["hot"]:
    print(json.dumps({"Code": 0, "Data": {"Items": [{
        "Title": "热点问题",
        "Url": "https://www.zhihu.com/question/456",
        "Summary": "热点摘要",
        "ThumbnailUrl": ""
    }]}}))
elif args[:2] == ["question", "answers"]:
    print(json.dumps({"Code": 0, "Data": {"Items": [{
        "ContentType": "Answer",
        "ContentToken": "789",
        "Url": "https://www.zhihu.com/answer/789",
        "Summary": "回答摘要"
    }], "Paging": {"IsEnd": True}}}))
else:
    print(json.dumps({"error": "unexpected args", "args": args}))
    sys.exit(9)
"""


class ZhihuCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.fake_cli = self.root / "zhihu-cli"
        self.fake_cli.write_text(FAKE_CLI, encoding="utf-8")
        self.fake_cli.chmod(0o755)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_collector(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_status_sanitizes_auth_payload(self) -> None:
        completed = self.run_collector("status", "--binary", str(self.fake_cli))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["installed"])
        self.assertTrue(payload["compatible"])
        self.assertEqual(payload["next_action"], "ready_unverified")
        self.assertNotIn("masked_value", payload["auth"])
        self.assertIn("search zhihu", payload["commands"])

    def test_collect_writes_raw_normalized_and_deduplicated_records(self) -> None:
        output = self.root / "output"
        completed = self.run_collector(
            "collect",
            "--binary",
            str(self.fake_cli),
            "--query",
            "AI 产品",
            "--query",
            "AI 产品经理",
            "--hot",
            "--question-url",
            "https://www.zhihu.com/question/456",
            "--output",
            str(output),
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["record_count"], 3)

        records = [
            json.loads(line)
            for line in (output / "records.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(len(records), 3)
        answer = next(record for record in records if record["content_id"] == "123")
        self.assertEqual(len(answer["discovery"]), 2)
        self.assertEqual(
            answer["canonical_url"],
            "https://www.zhihu.com/answer/123",
        )
        self.assertNotIn("<em>", answer["summary"])

        metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["arguments"]["queries"], ["AI 产品", "AI 产品经理"])
        self.assertEqual(metadata["record_count"], 3)
        self.assertTrue((output / "raw").is_dir())
        self.assertEqual(len(list((output / "raw").glob("*.json"))), 4)

    def test_collect_requires_auth(self) -> None:
        unauth_cli = self.root / "unauth-cli"
        unauth_cli.write_text(
            "#!/usr/bin/env python3\n"
            "import json\n"
            "print(json.dumps({'configured': False}))\n",
            encoding="utf-8",
        )
        unauth_cli.chmod(0o755)
        completed = self.run_collector(
            "collect",
            "--binary",
            str(unauth_cli),
            "--query",
            "test",
            "--output",
            str(self.root / "unauth-output"),
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["error"]["code"], "AUTH_REQUIRED")

    def test_collect_empty_is_not_success(self) -> None:
        empty_cli = self.root / "empty-cli"
        empty_cli.write_text(
            FAKE_CLI.replace(
                '"ContentID": "123",', '"ContentID": "",'
            ).replace(
                '"Url": "https://www.zhihu.com/answer/123?utm_source=openapi&utm_medium=platform",',
                '"Url": "",',
            ),
            encoding="utf-8",
        )
        empty_cli.chmod(0o755)
        output = self.root / "empty-output"
        completed = self.run_collector(
            "collect",
            "--binary",
            str(empty_cli),
            "--query",
            "empty",
            "--output",
            str(output),
        )
        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["error"]["code"], "EMPTY_RESULT")
        metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["record_count"], 0)


if __name__ == "__main__":
    unittest.main()
