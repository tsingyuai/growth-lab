from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("seedance_provider.py")
SPEC = importlib.util.spec_from_file_location("seedance_provider", SCRIPT)
seedance = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(seedance)


class FakeClient:
    def __init__(self, *, ambiguous: bool = False):
        self.ambiguous = ambiguous
        self.created = 0
        self.deleted = 0

    def create(self, payload):
        self.created += 1
        if self.ambiguous:
            raise seedance.AmbiguousCreateError("transport timeout")
        return {"id": "task-123"}

    def get(self, task_id):
        return {
            "id": task_id,
            "status": "succeeded",
            "model": "ep-test",
            "content": {"video_url": "https://media.example/video.mp4?token=secret-token"},
            "revised_prompt": "clean motion without text",
            "usage": {"completion_tokens": 5},
            "seed": 7,
            "duration": 5,
            "ratio": "9:16",
            "resolution": "720p",
            "frames": 120,
            "framespersecond": 24,
            "generate_audio": False,
            "service_tier": "default",
        }

    def delete(self, task_id):
        self.deleted += 1
        return {}


class SeedanceProviderTests(unittest.TestCase):
    def configured(self):
        return {
            "ARK_API_KEY": "secret-api-key",
            "ARK_BASE_URL": "https://ark.example/api/v3",
            "SEEDANCE_MODEL_ENDPOINT": "ep-test",
        }

    def request(self, root: Path, content=None, options=None) -> Path:
        value = {
            "schema_version": 1,
            "provider": "seedance-ark",
            "purpose": "b-roll",
            "scene_id": "hero-motion",
            "content": content or [{"type": "text", "text": "Abstract paper layers moving gently; no text."}],
            "options": {
                "duration": 5,
                "ratio": "9:16",
                "resolution": "720p",
                "generate_audio": False,
                **(options or {}),
            },
            "input_rights_confirmed": True,
            "remote_asset_upload_authorized": True,
        }
        path = root / "seedance-request.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def test_configuration_report_never_exposes_key(self):
        report = seedance.configuration_report(self.configured())
        self.assertEqual(report["status"], "configured-not-verified")
        self.assertNotIn("secret-api-key", json.dumps(report))

    def test_url_env_is_resolved_but_only_hashed_in_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = self.request(
                root,
                content=[
                    {"type": "text", "text": "Animate this owned reference without adding text."},
                    {"type": "image_url", "url_env": "SEEDANCE_INPUT_HERO", "role": "first_frame"},
                ],
            )
            actual = "https://storage.example/hero.png?signature=private"
            normalized, summary = seedance.read_generation_request(
                request, {"SEEDANCE_INPUT_HERO": actual}
            )
            self.assertEqual(normalized["content"][1]["image_url"]["url"], actual)
            encoded = json.dumps(summary)
            self.assertNotIn(actual, encoded)
            self.assertIn(seedance.sha256_bytes(actual.encode()), encoded)

    def test_rejects_signed_url_in_request_and_generated_audio(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = self.request(
                root,
                content=[
                    {"type": "text", "text": "Animate this."},
                    {"type": "image_url", "url": "https://storage.example/hero.png?signature=private"},
                ],
            )
            with self.assertRaisesRegex(seedance.SeedanceError, "url_env"):
                seedance.read_generation_request(request)
            request = self.request(root, options={"generate_audio": True})
            with self.assertRaisesRegex(seedance.SeedanceError, "False was expected|generate_audio=false"):
                seedance.read_generation_request(request)

    def test_success_is_downloaded_validated_sanitized_and_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = self.request(root)
            output = root / "out"
            client = FakeClient()

            def downloader(url, destination):
                self.assertIn("secret-token", url)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"fake-video")

            def validator(path):
                self.assertEqual(path.read_bytes(), b"fake-video")
                return {
                    "duration_seconds": 5.0,
                    "width": 720,
                    "height": 1280,
                    "fps": 24.0,
                    "has_audio": False,
                }

            manifest = seedance.run_generation(
                request,
                output,
                confirm_paid_generation=True,
                wait_timeout=30,
                poll_interval=2,
                configured=self.configured(),
                client=client,
                downloader=downloader,
                validator=validator,
            )
            self.assertEqual(manifest["status"], "succeeded-downloaded-validated")
            self.assertEqual(client.created, 1)
            persisted = (output / seedance.MANIFEST_FILE).read_text(encoding="utf-8")
            self.assertNotIn("secret-token", persisted)
            self.assertNotIn("media.example", persisted)
            second = seedance.run_generation(
                request,
                output,
                confirm_paid_generation=False,
                wait_timeout=30,
                poll_interval=2,
                configured=self.configured(),
                client=client,
                downloader=downloader,
                validator=validator,
            )
            self.assertEqual(second["output"]["sha256"], manifest["output"]["sha256"])
            self.assertEqual(client.created, 1)

    def test_ambiguous_create_blocks_repeated_paid_request(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = self.request(root)
            output = root / "out"
            client = FakeClient(ambiguous=True)
            with self.assertRaises(seedance.AmbiguousCreateError):
                seedance.run_generation(
                    request,
                    output,
                    confirm_paid_generation=True,
                    wait_timeout=30,
                    poll_interval=2,
                    configured=self.configured(),
                    client=client,
                )
            self.assertTrue((output / seedance.AMBIGUOUS_FILE).is_file())
            with self.assertRaisesRegex(seedance.SeedanceError, "禁止自动重复"):
                seedance.run_generation(
                    request,
                    output,
                    confirm_paid_generation=True,
                    wait_timeout=30,
                    poll_interval=2,
                    configured=self.configured(),
                    client=client,
                )
            self.assertEqual(client.created, 1)

    def test_resume_without_state_never_creates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            client = FakeClient()
            with self.assertRaisesRegex(seedance.SeedanceError, "不会创建新的付费任务"):
                seedance.run_generation(
                    self.request(root),
                    root / "out",
                    confirm_paid_generation=False,
                    wait_timeout=30,
                    poll_interval=2,
                    configured=self.configured(),
                    client=client,
                    allow_create=False,
                )
            self.assertEqual(client.created, 0)

    def test_remote_delete_requires_separate_confirmation(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            seedance.write_json(output / seedance.STATE_FILE, {
                "schema_version": 1,
                "provider": "seedance-ark",
                "task_id": "task-123",
            })
            client = FakeClient()
            with self.assertRaisesRegex(seedance.SeedanceError, "--confirm-delete"):
                seedance.delete_remote_task(
                    output, confirm_delete=False, configured=self.configured(), client=client
                )
            result = seedance.delete_remote_task(
                output, confirm_delete=True, configured=self.configured(), client=client
            )
            self.assertTrue(result["remote_deleted"])
            self.assertFalse(result["local_files_deleted"])
            self.assertEqual(client.deleted, 1)


if __name__ == "__main__":
    unittest.main()
