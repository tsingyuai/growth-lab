from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import wave


SCRIPT = Path(__file__).with_name("synthesize_speech.py")
SPEC = importlib.util.spec_from_file_location("synthesize_speech", SCRIPT)
speech = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(speech)


class SpeechAdapterTests(unittest.TestCase):
    def request(self, root: Path) -> Path:
        value = {
            "schema_version": 1,
            "voice": {
                "engine": "kokoro",
                "model_id": speech.MODEL_ID,
                "model_revision": speech.MODEL_REVISION,
                "voice_name": "zf_001",
                "language": "zh",
                "speed": 1.0,
                "license": speech.LICENSE,
            },
            "items": [{"id": "intro", "text": "你好。", "output": "01-intro.wav"}],
        }
        path = root / "request.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def test_batch_records_pinned_model_and_audio_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            def factory(config):
                self.assertEqual(config["model_revision"], speech.MODEL_REVISION)

                def backend(text, output):
                    with wave.open(str(output), "wb") as audio:
                        audio.setnchannels(1)
                        audio.setsampwidth(2)
                        audio.setframerate(24000)
                        audio.writeframes(struct.pack("<h", 500) * 2400)
                    return {}

                return backend

            manifest = speech.synthesize_request(self.request(root), root / "out", factory)
            self.assertEqual(manifest["model_id"], speech.MODEL_ID)
            self.assertEqual(manifest["voice_name"], "zf_001")
            self.assertEqual(manifest["license"], "Apache-2.0")
            self.assertEqual(manifest["outputs"][0]["duration_seconds"], 0.1)
            self.assertEqual(len(manifest["outputs"][0]["sha256"]), 64)

    def test_rejects_unpinned_model(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.request(root)
            value = json.loads(path.read_text(encoding="utf-8"))
            value["voice"]["model_revision"] = "main"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(speech.SpeechError, "model_revision"):
                speech.read_request(path)


if __name__ == "__main__":
    unittest.main()
