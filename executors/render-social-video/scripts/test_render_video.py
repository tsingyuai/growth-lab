from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).with_name("render_video.py")
SPEC = importlib.util.spec_from_file_location("render_video", SCRIPT)
renderer = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(renderer)


class VideoRendererTests(unittest.TestCase):
    def plan(self, root: Path) -> Path:
        screenshot = Image.new("RGB", (1000, 700), "white")
        draw = ImageDraw.Draw(screenshot)
        draw.rectangle((80, 80, 920, 620), fill="#eef0ff", outline="#4f35e8", width=8)
        draw.text((120, 120), "Product UI", fill="black")
        screenshot.save(root / "product.png")
        plan = {
            "schema_version": 1,
            "title": "Growth Lab",
            "canvas": {"width": 1080, "height": 1920, "fps": 24},
            "voice": {"provider": "none"},
            "scenes": [
                {"id": "intro", "type": "title", "heading": "从产品信息到增长内容", "body": "先做一个可复现的视频原型", "narration": "从产品信息到增长内容。", "duration": 1.5, "motion": "none"},
                {"id": "proof", "type": "screenshot", "heading": "真实截图作为证据", "body": "字幕和标注保持确定性", "narration": "真实截图作为产品证据。", "asset": "product.png", "duration": 1.5, "motion": "slow-zoom", "highlight": {"x": 0.1, "y": 0.1, "width": 0.4, "height": 0.25}}
            ]
        }
        path = root / "video-plan.json"
        path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        return path

    def test_plan_and_frame_are_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = renderer.read_plan(path)
            frame = root / "frame.png"
            renderer.scene_frame(plan, plan["scenes"][1], path, frame)
            with Image.open(frame) as rendered:
                self.assertEqual(rendered.size, (1080, 1920))

    def test_product_demo_frame_supports_three_by_four_and_cursor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["canvas"] = {"width": 1440, "height": 1920, "fps": 24}
            plan["style"] = {
                "layout": "product-demo",
                "background": "#08090C",
                "foreground": "#FFFFFF",
                "accent": "#6650E8",
                "muted": "#C8CBD4",
                "brand_mark": "G",
            }
            plan["scenes"][0].update({"type": "screenshot", "asset": "product.png"})
            plan["scenes"][0]["asset_role"] = "product-screenshot"
            plan["scenes"][1]["hook"] = "产品界面就是证据"
            plan["scenes"][1]["asset_role"] = "product-screenshot"
            plan["scenes"][1]["cursor"] = {"x": 0.6, "y": 0.55, "size": 0.1}
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            frame = root / "product-demo.png"
            renderer.scene_frame(plan, plan["scenes"][1], path, frame)
            with Image.open(frame) as rendered:
                self.assertEqual(rendered.size, (1440, 1920))
                self.assertGreater(len(rendered.getcolors(maxcolors=2_000_000)), 5)

    def test_product_demo_requires_recording_majority(self):
        scenes = [
            {"asset_role": "screen-recording"},
            {"asset_role": "product-screenshot"},
        ]
        mix = renderer.validate_evidence_mix("product-demo", scenes, [5.0, 5.0])
        self.assertEqual(mix["screen_recording_ratio"], 0.5)
        with self.assertRaisesRegex(renderer.VideoError, "至少 50%"):
            renderer.validate_evidence_mix("product-demo", scenes, [4.9, 5.1])

    def test_product_demo_limits_deterministic_animation(self):
        scenes = [
            {"asset_role": "screen-recording"},
            {"asset_role": "deterministic-animation"},
            {"asset_role": "product-screenshot"},
        ]
        renderer.validate_evidence_mix("product-demo", scenes, [6.0, 2.5, 1.5])
        with self.assertRaisesRegex(renderer.VideoError, "不得超过.*25%"):
            renderer.validate_evidence_mix("product-demo", scenes, [5.0, 3.0, 2.0])

    def test_screen_recording_filter_enlarges_and_centers_capture(self):
        value = renderer.screen_recording_filter(1440, 1920)
        self.assertIn("scale=1614:-2", value)
        self.assertIn("crop=1440:ih:(iw-ow)*0.85:0", value)
        self.assertIn("pad=1440:1920:0:(oh-ih)/2", value)

    def test_focused_screen_uses_same_source_blurred_backdrop(self):
        filters = renderer.screen_recording_filter_chain(
            1440, 1920,
            {
                "preset": "focused-screen",
                "foreground_width_ratio": 0.84,
                "backdrop_blur": 26,
                "backdrop_dim": 0.16,
            },
        )
        value = ";".join(filters)
        self.assertIn("[0:v]split=2", value)
        self.assertIn("gblur=sigma=26.00", value)
        self.assertIn("eq=brightness=-0.160", value)
        self.assertIn("[background][foreground]overlay=(W-w)/2:(H-h)/2[base]", value)

    def test_caption_segments_render_in_distinct_lanes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plan_path = self.plan(root)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            group = {"vertical_anchor": "middle"}
            centers = []
            for lane in ("left", "center", "right"):
                output = root / f"{lane}.png"
                renderer.caption_segment_overlay(
                    plan, group,
                    {"id": lane, "text": lane, "lane": lane, "emphasis": "accent"},
                    plan_path, output,
                )
                with Image.open(output) as image:
                    box = image.getchannel("A").getbbox()
                self.assertIsNotNone(box)
                centers.append((box[0] + box[2]) / 2)
            self.assertLess(centers[0], centers[1])
            self.assertLess(centers[1], centers[2])

    def test_default_subtitles_are_large_on_both_canvases(self):
        plan = {"canvas": {"width": 1080}, "style": {}}
        self.assertEqual(renderer.subtitle_font_size(plan), 64)
        plan["canvas"]["width"] = 1440
        self.assertEqual(renderer.subtitle_font_size(plan), 85)
        plan["style"]["subtitle_size"] = 60
        self.assertEqual(renderer.subtitle_font_size(plan), 80)

    def test_plan_supports_up_to_twelve_scenes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["scenes"] = [
                {
                    "id": f"scene-{index}", "type": "title", "heading": f"镜头 {index}",
                    "duration": 1.5, "motion": "none",
                }
                for index in range(1, 13)
            ]
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(len(renderer.read_plan(path)["scenes"]), 12)
            plan["scenes"].append(
                {"id": "scene-13", "type": "title", "heading": "镜头 13", "duration": 1.5, "motion": "none"}
            )
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "Schema"):
                renderer.read_plan(path)

    def test_product_demo_rejects_evidenceless_scene(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["canvas"] = {"width": 1440, "height": 1920, "fps": 24}
            plan["style"] = {"layout": "product-demo"}
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "产品截图.*已审核卡片"):
                renderer.read_plan(path)

    def test_rendered_card_requires_verified_visual_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["scenes"][1]["asset_role"] = "rendered-card"
            plan["scenes"][1]["asset_source_id"] = "01-cover"
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "visual_source"):
                renderer.read_plan(path)

            source_manifest = root / "source-visual-manifest.json"
            source_manifest.write_text(
                '{"schema_version":1,"cards":[{"id":"01-cover","status":"approved"}]}', encoding="utf-8"
            )
            plan["visual_source"] = {
                "mode": "reused-card-pack",
                "manifest_file": source_manifest.name,
                "manifest_sha256": hashlib.sha256(source_manifest.read_bytes()).hexdigest(),
            }
            path.write_text(json.dumps(plan), encoding="utf-8")
            self.assertEqual(renderer.read_plan(path)["visual_source"]["mode"], "reused-card-pack")

    def test_card_sequence_uses_full_canvas_card(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            Image.new("RGB", (1080, 1440), "#123456").save(root / "card.png")
            source_manifest = root / "visual-manifest.json"
            source_manifest.write_text(
                '{"schema_version":1,"cards":[{"id":"card-01","status":"approved"}]}', encoding="utf-8"
            )
            plan = {
                "schema_version": 1,
                "title": "Growth Lab",
                "canvas": {"width": 1440, "height": 1920, "fps": 24},
                "voice": {"provider": "none"},
                "visual_source": {
                    "mode": "reused-card-pack",
                    "manifest_file": source_manifest.name,
                    "manifest_sha256": hashlib.sha256(source_manifest.read_bytes()).hexdigest(),
                },
                "style": {"layout": "card-sequence"},
                "scenes": [
                    {
                        "id": f"scene-{index}", "type": "screenshot", "heading": "场景",
                        "asset": "card.png", "asset_role": "rendered-card",
                        "asset_source_id": "card-01", "duration": 1.5, "motion": "none",
                    }
                    for index in range(1, 3)
                ],
            }
            path = root / "video-plan.json"
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            validated = renderer.read_plan(path)
            output = root / "frame.png"
            renderer.scene_frame(validated, validated["scenes"][0], path, output)
            with Image.open(output) as rendered:
                self.assertEqual(rendered.size, (1440, 1920))
                self.assertEqual(rendered.getpixel((720, 960)), (18, 52, 86))

    def test_product_demo_rendered_card_uses_full_canvas_without_wrapper(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            card_color = (18, 52, 86)
            Image.new("RGB", (1080, 1440), card_color).save(root / "card.png")
            source_manifest = root / "visual-manifest.json"
            source_manifest.write_text(
                '{"schema_version":1,"cards":[{"id":"card-01","status":"approved"}]}',
                encoding="utf-8",
            )
            plan = {
                "schema_version": 1,
                "title": "Growth Lab",
                "canvas": {"width": 1440, "height": 1920, "fps": 24},
                "voice": {"provider": "none"},
                "visual_source": {
                    "mode": "mixed-product-evidence",
                    "manifest_file": source_manifest.name,
                    "manifest_sha256": hashlib.sha256(source_manifest.read_bytes()).hexdigest(),
                },
                "style": {"layout": "product-demo"},
                "scenes": [
                    {
                        "id": "recording", "type": "video", "heading": "录屏",
                        "asset": "fixture.mp4", "asset_role": "screen-recording",
                        "duration": 1.5, "motion": "none",
                    },
                    {
                        "id": "card", "type": "screenshot", "heading": "卡片",
                        "asset": "card.png", "asset_role": "rendered-card",
                        "asset_source_id": "card-01", "duration": 1.5, "motion": "none",
                    },
                ],
            }
            output = root / "frame.png"
            renderer.scene_frame(plan, plan["scenes"][1], root / "video-plan.json", output)
            with Image.open(output) as rendered:
                self.assertEqual(rendered.size, (1440, 1920))
                self.assertEqual(rendered.getpixel((20, 20)), card_color)
                self.assertEqual(rendered.getpixel((720, 960)), card_color)

    def test_subtitle_cues_are_validated_and_written_with_phrase_timing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["scenes"][0]["subtitle_cues"] = [
                {"text": "第一句", "start": 0.05, "end": 0.7},
                {"text": "第二句", "start": 0.8, "end": 1.4},
            ]
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            validated = renderer.read_plan(path)
            srt = root / "subtitles.srt"
            renderer.write_srt(validated["scenes"], [1.5, 1.5], srt)
            content = srt.read_text(encoding="utf-8")
            self.assertIn("00:00:00,050 --> 00:00:00,700", content)
            self.assertIn("00:00:00,800 --> 00:00:01,400", content)
            plan["scenes"][0]["subtitle_cues"][1]["start"] = 0.6
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "不重叠"):
                renderer.read_plan(path)

    def test_caption_group_accumulates_and_writes_readable_srt_states(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["scenes"][0]["caption_groups"] = [{
                "id": "benefits", "display_mode": "accumulate", "exit_together": True,
                "vertical_anchor": "middle", "end": 1.4,
                "segments": [
                    {"id": "auto", "text": "能自动", "lane": "left", "start": 0.1},
                    {"id": "control", "text": "可控制", "lane": "center", "start": 0.6},
                    {"id": "value", "text": "高性价比", "lane": "right", "start": 1.0},
                ],
            }]
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            validated = renderer.read_plan(path)
            srt = root / "captions.srt"
            renderer.write_srt(validated["scenes"], [1.5, 1.5], srt)
            content = srt.read_text(encoding="utf-8")
            self.assertIn("能自动 可控制", content)
            self.assertIn("能自动 可控制 高性价比", content)

    def test_long_duration_is_reserved_for_screen_recording(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["scenes"][0]["duration"] = 13
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "1.5 到 12"):
                renderer.read_plan(path)

    def test_rejects_unapproved_canvas(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["canvas"] = {"width": 1200, "height": 1920, "fps": 24}
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "Schema"):
                renderer.read_plan(path)

    def test_rejects_rendered_card_marked_for_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            Image.new("RGB", (1080, 1440), "white").save(root / "card.png")
            source_manifest = root / "visual-manifest.json"
            source_manifest.write_text(
                '{"schema_version":1,"cards":[{"id":"card-01","status":"revise"}]}', encoding="utf-8"
            )
            plan = {
                "schema_version": 1,
                "title": "Growth Lab",
                "canvas": {"width": 1440, "height": 1920, "fps": 24},
                "voice": {"provider": "none"},
                "visual_source": {
                    "mode": "reused-card-pack",
                    "manifest_file": source_manifest.name,
                    "manifest_sha256": hashlib.sha256(source_manifest.read_bytes()).hexdigest(),
                },
                "style": {"layout": "card-sequence"},
                "scenes": [
                    {
                        "id": f"scene-{index}", "type": "screenshot", "heading": "场景",
                        "asset": "card.png", "asset_role": "rendered-card",
                        "asset_source_id": "card-01", "duration": 1.5, "motion": "none",
                    }
                    for index in range(1, 3)
                ],
            }
            path = root / "video-plan.json"
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "已批准"):
                renderer.read_plan(path)

    def test_local_tts_requires_pinned_model_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["voice"] = {
                "provider": "local-tts",
                "engine": "kokoro",
                "model_id": renderer.KOKORO_MODEL_ID,
                "model_revision": renderer.KOKORO_MODEL_REVISION,
                "voice_name": "zf_001",
                "language": "zh",
                "speed": 1.02,
                "license": "Apache-2.0",
            }
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(renderer.read_plan(path)["voice"]["voice_name"], "zf_001")
            plan["voice"]["model_revision"] = "0" * 40
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "model_revision"):
                renderer.read_plan(path)

    def test_seedance_broll_requires_validated_provider_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            clip = root / "seedance.mp4"
            clip.write_bytes(b"fixture-video")
            provider_manifest = root / "seedance-manifest.json"
            provider_manifest.write_text(
                json.dumps({
                    "schema_version": 1,
                    "status": "succeeded-downloaded-validated",
                    "provider": "seedance-ark",
                    "model_endpoint": "ep-test",
                    "task_id": "task-123",
                    "request_sha256": "0" * 64,
                    "request": {},
                    "provider_result": {"generate_audio": False},
                    "output": {
                        "file": "raw/seedance.mp4",
                        "sha256": hashlib.sha256(clip.read_bytes()).hexdigest(),
                        "duration_seconds": 5.0,
                        "width": 720,
                        "height": 1280,
                        "fps": 24.0,
                        "has_audio": False,
                    },
                    "remote_urls_persisted": False,
                    "publication_authorized": False,
                    "finished_at": "2026-08-05T00:00:00+08:00",
                }),
                encoding="utf-8",
            )
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["scenes"][1] = {
                "id": "proof",
                "type": "video",
                "heading": "生成式镜头只做辅助",
                "body": "准确文字仍由本地叠加",
                "narration": "生成式镜头只做辅助。",
                "asset": clip.name,
                "asset_role": "generated-broll",
                "provider_manifest": provider_manifest.name,
                "provider_manifest_sha256": hashlib.sha256(provider_manifest.read_bytes()).hexdigest(),
                "duration": 3.0,
                "motion": "none",
            }
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            validated = renderer.read_plan(path)
            scene = validated["scenes"][1]
            self.assertEqual(scene["_provider_source"]["task_id"], "task-123")
            overlay = root / "overlay.png"
            renderer.generated_video_overlay(validated, scene, path, overlay)
            with Image.open(overlay) as image:
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.size, (1080, 1920))
                self.assertEqual(image.getpixel((0, 0))[3], 0)
                self.assertGreater(image.getpixel((100, 100))[3], 0)
                self.assertEqual(image.getpixel((70, 1700))[3], 0)

            provider_value = json.loads(provider_manifest.read_text(encoding="utf-8"))
            provider_value["status"] = "failed"
            provider_manifest.write_text(json.dumps(provider_value), encoding="utf-8")
            plan["scenes"][1]["provider_manifest_sha256"] = hashlib.sha256(
                provider_manifest.read_bytes()
            ).hexdigest()
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "不符合公开 Schema|状态或素材哈希"):
                renderer.read_plan(path)

    def test_subtitles_only_video_overlay_omits_heading_panel(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            scene = plan["scenes"][1]
            scene["overlay_mode"] = "subtitles-only"
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            overlay = root / "subtitles-only.png"
            renderer.generated_video_overlay(plan, scene, path, overlay)
            with Image.open(overlay) as image:
                self.assertEqual(image.getpixel((100, 100))[3], 0)
                subtitle_pixels = [
                    image.getpixel((x, y))[3]
                    for y in range(1500, 1850, 25)
                    for x in range(80, 1000, 25)
                ]
                self.assertGreater(max(subtitle_pixels), 0)

    def test_screen_recording_requires_validated_capture_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            clip = root / "product-demo.mp4"
            clip.write_bytes(b"validated-screen-recording")
            capture_manifest = root / "product-demo.capture-manifest.json"
            capture_manifest.write_text(
                json.dumps({
                    "schema_version": 1,
                    "status": "recorded-validated",
                    "source": {"kind": "window", "window_title": "Growth Lab Capture Test"},
                    "capture": {
                        "started_at": "2026-08-06T10:00:00+00:00",
                        "requested_duration_seconds": 5.0,
                        "draw_mouse": True,
                        "scope_confirmed": True,
                        "human_privacy_review_required": True,
                    },
                    "renderer": {
                        "name": "ffmpeg-gdigrab",
                        "ffmpeg_version": "ffmpeg version 7.1",
                        "external_binary": True,
                    },
                    "output": {
                        "file": clip.name,
                        "sha256": hashlib.sha256(clip.read_bytes()).hexdigest(),
                        "duration_seconds": 5.0,
                        "width": 1280,
                        "height": 720,
                        "fps": 30.0,
                        "has_audio": False,
                    },
                    "publication_authorized": False,
                }),
                encoding="utf-8",
            )
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["scenes"][1] = {
                "id": "proof",
                "type": "video",
                "heading": "真实操作过程",
                "asset": clip.name,
                "asset_role": "screen-recording",
                "capture_manifest": capture_manifest.name,
                "capture_manifest_sha256": hashlib.sha256(capture_manifest.read_bytes()).hexdigest(),
                "duration": 3.0,
                "motion": "none",
            }
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            scene = renderer.read_plan(path)["scenes"][1]
            self.assertEqual(scene["_capture_source"]["source_kind"], "window")
            self.assertEqual(scene["_asset_duration"], 5.0)

            capture_data = json.loads(capture_manifest.read_text(encoding="utf-8"))
            capture_data["capture"]["scope_confirmed"] = False
            capture_manifest.write_text(json.dumps(capture_data), encoding="utf-8")
            plan["scenes"][1]["capture_manifest_sha256"] = hashlib.sha256(
                capture_manifest.read_bytes()
            ).hexdigest()
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "Schema|状态、权限"):
                renderer.read_plan(path)

    def test_browser_capture_requires_hash_bound_semantic_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "browser.capture-manifest.json"
            capture_data = {
                "source": {"kind": "browser"},
                "capture": {},
            }
            with self.assertRaisesRegex(renderer.VideoError, "语义证据"):
                renderer.validate_browser_capture_evidence(manifest, capture_data)
            evidence = root / "browser-evidence.json"
            evidence.write_text('{"status":"pass"}', encoding="utf-8")
            capture_data["capture"]["semantic_validation"] = {
                "status": "pass",
                "evidence_file": evidence.name,
                "evidence_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
            }
            renderer.validate_browser_capture_evidence(manifest, capture_data)
            capture_data["capture"]["semantic_validation"]["evidence_sha256"] = "0" * 64
            with self.assertRaisesRegex(renderer.VideoError, "哈希不匹配"):
                renderer.validate_browser_capture_evidence(manifest, capture_data)

    def test_deterministic_animation_requires_validated_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = self.plan(root)
            clip = root / "cards.mp4"
            clip.write_bytes(b"validated-deterministic-animation")
            animation_manifest = root / "cards.animation-manifest.json"
            animation_manifest.write_text(
                json.dumps({
                    "schema_version": 1,
                    "status": "rendered-validated",
                    "source": {
                        "html_file": "cards.html",
                        "html_sha256": "1" * 64,
                        "assets": [],
                    },
                    "render": {
                        "started_at": "2026-08-06T10:00:00+00:00",
                        "engine": "playwright-chromium",
                        "browser_executable": "chrome.exe",
                        "width": 1080,
                        "height": 1920,
                        "fps": 30,
                        "requested_duration_seconds": 5.0,
                        "network_disabled_by_policy": True,
                    },
                    "output": {
                        "file": clip.name,
                        "sha256": hashlib.sha256(clip.read_bytes()).hexdigest(),
                        "duration_seconds": 5.0,
                        "width": 1080,
                        "height": 1920,
                        "fps": 30.0,
                        "has_audio": False,
                    },
                    "publication_authorized": False,
                }),
                encoding="utf-8",
            )
            plan = json.loads(path.read_text(encoding="utf-8"))
            plan["scenes"][1] = {
                "id": "cards",
                "type": "video",
                "heading": "卡片动画",
                "asset": clip.name,
                "asset_role": "deterministic-animation",
                "animation_manifest": animation_manifest.name,
                "animation_manifest_sha256": hashlib.sha256(animation_manifest.read_bytes()).hexdigest(),
                "duration": 3.0,
                "motion": "none",
            }
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            scene = renderer.read_plan(path)["scenes"][1]
            self.assertEqual(scene["_animation_source"]["engine"], "playwright-chromium")
            self.assertEqual(scene["_asset_duration"], 5.0)

            manifest_data = json.loads(animation_manifest.read_text(encoding="utf-8"))
            manifest_data["output"]["has_audio"] = True
            animation_manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
            plan["scenes"][1]["animation_manifest_sha256"] = hashlib.sha256(
                animation_manifest.read_bytes()
            ).hexdigest()
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "Schema|状态或素材哈希"):
                renderer.read_plan(path)

    def test_rejects_asset_outside_package(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as other:
            root = Path(temp)
            path = self.plan(root)
            plan = json.loads(path.read_text(encoding="utf-8"))
            external = Path(other) / "outside.png"
            Image.new("RGB", (10, 10)).save(external)
            plan["scenes"][1]["asset"] = str(external)
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(renderer.VideoError, "目录内"):
                renderer.read_plan(path)

    def test_srt_uses_scene_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "subtitles.srt"
            renderer.write_srt([{"narration": "第一句"}, {"narration": "第二句"}], [1.5, 2.0], path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("00:00:00,000 --> 00:00:01,500", text)
            self.assertIn("00:00:01,500 --> 00:00:03,500", text)

    def test_balanced_subtitle_does_not_start_second_line_with_punctuation(self):
        image = Image.new("RGB", (1080, 1920), "white")
        draw = ImageDraw.Draw(image)
        face = renderer.font(renderer.DEFAULT_FONT, 37)
        lines = renderer.balanced_two_lines(
            draw,
            "生成式镜头只负责动态氛围，准确内容仍由本地控制。",
            face,
            812,
        )
        self.assertEqual(len(lines), 2)
        self.assertGreater(len(lines[1]), 1)
        self.assertNotIn(lines[1][0], "，。！？；：、")
        self.assertTrue(lines[0].endswith("，"))


if __name__ == "__main__":
    unittest.main()
