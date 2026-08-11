from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("record_screen.py")
SPEC = importlib.util.spec_from_file_location("record_screen", SCRIPT)
recorder = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(recorder)


class RecordScreenTests(unittest.TestCase):
    def test_window_command_is_bounded_and_has_no_audio(self):
        command = recorder.build_capture_command(
            "ffmpeg.exe",
            Path("out.mp4"),
            5.0,
            30,
            window_title="Growth Lab Capture Test",
        )
        self.assertIn("title=Growth Lab Capture Test", command)
        self.assertEqual(command[command.index("-t") + 1], "5.000")
        self.assertIn("-an", command)
        self.assertIn("libx264", command)
        self.assertEqual(command[command.index("-vf") + 1], "crop=trunc(iw/2)*2:trunc(ih/2)*2")

    def test_region_command_has_bounded_geometry(self):
        command = recorder.build_capture_command(
            "ffmpeg.exe", Path("out.mp4"), 3.0, 24, region=(10, 20, 800, 600)
        )
        self.assertEqual(command[command.index("-offset_x") + 1], "10")
        self.assertEqual(command[command.index("-offset_y") + 1], "20")
        self.assertEqual(command[command.index("-video_size") + 1], "800x600")
        self.assertIn("desktop", command)

    def test_rejects_unbounded_or_conflicting_capture(self):
        with self.assertRaisesRegex(recorder.CaptureError, "时长"):
            recorder.build_capture_command("ffmpeg.exe", Path("out.mp4"), 0, 30)
        with self.assertRaisesRegex(recorder.CaptureError, "不能同时"):
            recorder.build_capture_command(
                "ffmpeg.exe", Path("out.mp4"), 5, 30,
                window_title="A", region=(0, 0, 100, 100),
            )

    def test_sha256_streams_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "capture.mp4"
            path.write_bytes(b"screen-recording")
            self.assertEqual(
                recorder.sha256_file(path),
                "47d1475319e7ced47d296fed0596c7859d134a89e51eba6d22800cead65e3b21",
            )

    def test_ready_signal_is_written_only_after_partial_has_data(self):
        class FakeProcess:
            pid = 1234

            @staticmethod
            def poll():
                return None

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            partial = root / ".capture.partial.mp4"
            ready = root / "capture.ready.json"
            partial.write_bytes(b"first-frame")
            started_at = recorder.datetime.now(recorder.timezone.utc)
            recorder.wait_for_capture_start(FakeProcess(), partial, ready, started_at, timeout=0.2)
            payload = json.loads(ready.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "capture-started")
            self.assertEqual(payload["pid"], 1234)


if __name__ == "__main__":
    unittest.main()
