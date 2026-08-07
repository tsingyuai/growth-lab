from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("open_local_configuration.py")
SPEC = importlib.util.spec_from_file_location("open_local_configuration", SCRIPT)
opener = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(opener)


class LocalConfigurationTests(unittest.TestCase):
    def test_creates_local_file_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env.example").write_text("OPENAI_API_KEY=\n", encoding="utf-8")
            path, created = opener.ensure_local_env(root)
            self.assertTrue(created)
            self.assertEqual(path.read_text(encoding="utf-8"), "OPENAI_API_KEY=\n")

    def test_existing_local_file_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env.example").write_text("example", encoding="utf-8")
            (root / ".env.local").write_text("existing", encoding="utf-8")
            path, created = opener.ensure_local_env(root)
            self.assertFalse(created)
            self.assertEqual(path.read_text(encoding="utf-8"), "existing")

    def test_windows_opens_notepad_without_waiting(self) -> None:
        launcher = mock.Mock()
        opener.open_editor(Path("C:/repo/.env.local"), "Windows", launcher)
        self.assertEqual(launcher.call_args.args[0][0], "notepad.exe")


if __name__ == "__main__":
    unittest.main()
