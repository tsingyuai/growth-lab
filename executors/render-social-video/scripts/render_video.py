#!/usr/bin/env python3
"""Render bounded screenshot-led social videos with Pillow and external FFmpeg."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import wave
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaError


DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
DEFAULT_FONT = Path(r"C:\Windows\Fonts\simhei.ttf")
MOTIONS = {"none", "slow-zoom", "pan-up"}
SCENE_TYPES = {"title", "screenshot", "video", "text", "cta"}
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"
CAPTURE_SCHEMA = (
    Path(__file__).resolve().parents[2]
    / "capture-screen-video"
    / "schemas"
    / "capture-manifest.schema.json"
)
ANIMATION_SCHEMA = (
    Path(__file__).resolve().parents[2]
    / "render-card-animation"
    / "schemas"
    / "animation-manifest.schema.json"
)
LOCAL_TTS_SCRIPT = Path(__file__).with_name("synthesize_speech.py")
SCRIPT_COVERAGE_VALIDATOR = Path(__file__).with_name("validate_script_coverage.py")
KOKORO_MODEL_ID = "hexgrad/Kokoro-82M-v1.1-zh"
KOKORO_MODEL_REVISION = "01e7505bd6a7a2ac4975463114c3a7650a9f7218"


class VideoError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_input(root: Path, raw: Any, label: str, suffixes: set[str]) -> Path:
    if not isinstance(raw, str) or not raw:
        raise VideoError(f"{label} 缺少文件路径。")
    path = (root / raw).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise VideoError(f"{label} 必须位于计划文件目录内。") from exc
    if not path.is_file() or path.suffix.lower() not in suffixes:
        raise VideoError(f"{label} 不存在或格式不支持：{raw}")
    return path


def evidence_mix(scenes: list[dict[str, Any]], durations: list[float]) -> dict[str, float]:
    total = sum(durations)
    if total <= 0 or len(scenes) != len(durations):
        raise VideoError("无法计算视频证据构成比例。")
    recording = sum(
        duration for scene, duration in zip(scenes, durations)
        if scene.get("asset_role") == "screen-recording"
    )
    animation = sum(
        duration for scene, duration in zip(scenes, durations)
        if scene.get("asset_role") == "deterministic-animation"
    )
    return {
        "total_duration": round(total, 3),
        "screen_recording_duration": round(recording, 3),
        "screen_recording_ratio": round(recording / total, 4),
        "deterministic_animation_duration": round(animation, 3),
        "deterministic_animation_ratio": round(animation / total, 4),
    }


def validate_evidence_mix(layout: str, scenes: list[dict[str, Any]], durations: list[float]) -> dict[str, float]:
    mix = evidence_mix(scenes, durations)
    if layout == "product-demo":
        if mix["screen_recording_ratio"] + 1e-9 < 0.5:
            raise VideoError("product-demo 的真实产品录屏必须占总时长至少 50%。")
        if mix["deterministic_animation_ratio"] - 1e-9 > 0.25:
            raise VideoError("product-demo 的确定性 HTML/卡片动效不得超过总时长 25%。")
    return mix


def read_plan(path: Path) -> dict[str, Any]:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VideoError("video-plan 不存在或不是有效 JSON。") from exc
    if not isinstance(plan, dict) or plan.get("schema_version") != 1:
        raise VideoError("video-plan schema_version 必须是 1。")
    try:
        schema = json.loads((SCHEMA_DIR / "video-plan.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(plan)
    except (OSError, json.JSONDecodeError, JsonSchemaError) as exc:
        raise VideoError(f"video-plan 不符合公开 Schema：{exc}") from exc
    canvas = plan.get("canvas") or {}
    canvas_size = (canvas.get("width"), canvas.get("height"))
    if canvas_size not in {(1080, 1920), (1440, 1920)} or canvas.get("fps") not in {24, 25, 30}:
        raise VideoError("仅支持 1080x1920、1440x1920 和 24/25/30 fps。")
    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not 2 <= len(scenes) <= 12:
        raise VideoError("video-plan 必须包含 2 到 12 个场景。")
    ids: set[str] = set()
    total = 0.0
    provider = (plan.get("voice") or {}).get("provider")
    layout = (plan.get("style") or {}).get("layout", "classic")
    visual_source = plan.get("visual_source") or {}
    manifest_file = visual_source.get("manifest_file")
    manifest_sha256 = visual_source.get("manifest_sha256")
    source_card_ids: set[str] = set()
    if bool(manifest_file) != bool(manifest_sha256):
        raise VideoError("visual_source.manifest_file 与 manifest_sha256 必须同时提供。")
    if manifest_file:
        source_manifest = safe_input(path.parent, manifest_file, "visual_source.manifest_file", {".json"})
        if sha256_file(source_manifest) != manifest_sha256:
            raise VideoError("visual_source 清单哈希不匹配。")
        try:
            source_manifest_data = json.loads(source_manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VideoError("visual_source 清单不是有效 JSON。") from exc
        cards = source_manifest_data.get("cards") if isinstance(source_manifest_data, dict) else None
        if (
            not isinstance(source_manifest_data, dict)
            or source_manifest_data.get("schema_version") != 1
            or not isinstance(cards, list)
            or not cards
        ):
            raise VideoError("visual_source 清单缺少有效的 cards。")
        source_card_ids = {
            str(card.get("id")) for card in cards
            if (
                isinstance(card, dict)
                and str(card.get("id") or "").strip()
                and card.get("status") == "approved"
            )
        }
    if provider not in {"none", "windows-sapi", "user-audio", "local-tts"}:
        raise VideoError("voice.provider 无效。")
    if provider == "local-tts":
        voice = plan["voice"]
        expected = {
            "engine": "kokoro",
            "model_id": KOKORO_MODEL_ID,
            "model_revision": KOKORO_MODEL_REVISION,
            "license": "Apache-2.0",
            "language": "zh",
        }
        for key, value in expected.items():
            if voice.get(key) != value:
                raise VideoError(f"local-tts voice.{key} 必须为 {value}。")
        if not re.fullmatch(r"z[fm]_\d{3}", str(voice.get("voice_name") or "")):
            raise VideoError("local-tts voice_name 必须是受控中文音色 ID。")
    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            raise VideoError(f"scenes[{index}] 必须是对象。")
        scene_id = str(scene.get("id") or "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,31}", scene_id) or scene_id in ids:
            raise VideoError(f"scenes[{index}].id 无效或重复。")
        ids.add(scene_id)
        if scene.get("type") not in SCENE_TYPES or scene.get("motion") not in MOTIONS:
            raise VideoError(f"scenes[{index}] 类型或 motion 无效。")
        if not str(scene.get("heading") or "").strip():
            raise VideoError(f"scenes[{index}].heading 不能为空。")
        duration = float(scene.get("duration") or 0)
        if not 1.5 <= duration <= 12:
            raise VideoError(f"scenes[{index}].duration 必须在 1.5 到 12 秒之间。")
        subtitle_cues = scene.get("subtitle_cues") or []
        previous_end = 0.0
        for cue_index, cue in enumerate(subtitle_cues):
            start = float(cue["start"])
            end = float(cue["end"])
            if start < previous_end or end <= start or end > duration + 1e-6:
                raise VideoError(
                    f"scenes[{index}].subtitle_cues[{cue_index}] 时间必须有序、不重叠且位于镜头内。"
                )
            previous_end = end
        total += duration
        if scene["type"] == "screenshot":
            safe_input(path.parent, scene.get("asset"), f"scenes[{index}].asset", {".png", ".jpg", ".jpeg", ".webp"})
            if scene.get("asset_role") == "rendered-card" and not manifest_file:
                raise VideoError("rendered-card 场景必须提供已验证的 visual_source 清单。")
            if scene.get("asset_role") == "rendered-card":
                source_id = str(scene.get("asset_source_id") or "")
                if not source_id or source_id not in source_card_ids:
                    raise VideoError(f"scenes[{index}].asset_source_id 不在 visual_source 已批准卡片中。")
        elif scene["type"] == "video":
            if scene.get("motion") != "none":
                raise VideoError("video 场景必须使用 motion=none。")
            asset = safe_input(
                path.parent, scene.get("asset"), f"scenes[{index}].asset", {".mp4"}
            )
            asset_role = scene.get("asset_role")
            if asset_role == "generated-broll":
                provider_manifest_raw = scene.get("provider_manifest")
                provider_manifest_sha = scene.get("provider_manifest_sha256")
                if not provider_manifest_raw or not provider_manifest_sha:
                    raise VideoError("generated-broll 场景必须提供 provider manifest 和 SHA-256。")
                provider_manifest = safe_input(
                    path.parent, provider_manifest_raw, f"scenes[{index}].provider_manifest", {".json"}
                )
                if sha256_file(provider_manifest) != provider_manifest_sha:
                    raise VideoError("generated-broll provider manifest 哈希不匹配。")
                try:
                    provider_data = json.loads(provider_manifest.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise VideoError("generated-broll provider manifest 不是有效 JSON。") from exc
                try:
                    provider_schema = json.loads(
                        (SCHEMA_DIR / "seedance-manifest.schema.json").read_text(encoding="utf-8")
                    )
                    Draft202012Validator(provider_schema).validate(provider_data)
                except (OSError, json.JSONDecodeError, JsonSchemaError) as exc:
                    raise VideoError(f"generated-broll provider manifest 不符合公开 Schema：{exc}") from exc
                output = provider_data.get("output") if isinstance(provider_data, dict) else None
                provider_result = provider_data.get("provider_result") if isinstance(provider_data, dict) else None
                if (
                    provider_data.get("schema_version") != 1
                    or provider_data.get("status") != "succeeded-downloaded-validated"
                    or provider_data.get("provider") != "seedance-ark"
                    or not str(provider_data.get("model_endpoint") or "")
                    or not str(provider_data.get("task_id") or "")
                    or not isinstance(output, dict)
                    or output.get("sha256") != sha256_file(asset)
                ):
                    raise VideoError("generated-broll provider manifest 状态或素材哈希无效。")
                if isinstance(provider_result, dict) and provider_result.get("generate_audio") is True:
                    raise VideoError("generated-broll 必须关闭提供商音频，由本地配音层负责。")
                asset_duration = float(output.get("duration_seconds") or 0)
                if asset_duration + 0.05 < duration:
                    raise VideoError("generated-broll 时长短于计划场景时长。")
                scene["_asset_duration"] = asset_duration
                scene["_provider_source"] = {
                    "provider": "seedance-ark",
                    "model_endpoint": str(provider_data.get("model_endpoint") or ""),
                    "task_id": str(provider_data.get("task_id") or ""),
                    "scene_id": scene_id,
                    "manifest_file": str(provider_manifest_raw),
                    "manifest_sha256": str(provider_manifest_sha),
                    "asset_sha256": str(output["sha256"]),
                }
            elif asset_role == "screen-recording":
                capture_manifest_raw = scene.get("capture_manifest")
                capture_manifest_sha = scene.get("capture_manifest_sha256")
                if not capture_manifest_raw or not capture_manifest_sha:
                    raise VideoError("screen-recording 场景必须提供 capture manifest 和 SHA-256。")
                capture_manifest = safe_input(
                    path.parent, capture_manifest_raw, f"scenes[{index}].capture_manifest", {".json"}
                )
                if sha256_file(capture_manifest) != capture_manifest_sha:
                    raise VideoError("screen-recording capture manifest 哈希不匹配。")
                try:
                    capture_data = json.loads(capture_manifest.read_text(encoding="utf-8"))
                    capture_schema = json.loads(CAPTURE_SCHEMA.read_text(encoding="utf-8"))
                    Draft202012Validator(capture_schema).validate(capture_data)
                except (OSError, json.JSONDecodeError, JsonSchemaError) as exc:
                    raise VideoError(f"screen-recording capture manifest 不符合公开 Schema：{exc}") from exc
                output = capture_data.get("output") if isinstance(capture_data, dict) else None
                capture = capture_data.get("capture") if isinstance(capture_data, dict) else None
                if (
                    capture_data.get("status") != "recorded-validated"
                    or not isinstance(output, dict)
                    or output.get("sha256") != sha256_file(asset)
                    or output.get("has_audio") is not False
                    or not isinstance(capture, dict)
                    or capture.get("scope_confirmed") is not True
                    or capture.get("human_privacy_review_required") is not True
                ):
                    raise VideoError("screen-recording capture manifest 状态、权限或素材哈希无效。")
                asset_duration = float(output.get("duration_seconds") or 0)
                if asset_duration + 0.05 < duration:
                    raise VideoError("screen-recording 时长短于计划场景时长。")
                scene["_asset_duration"] = asset_duration
                scene["_capture_source"] = {
                    "source_kind": str((capture_data.get("source") or {}).get("kind") or ""),
                    "scene_id": scene_id,
                    "manifest_file": str(capture_manifest_raw),
                    "manifest_sha256": str(capture_manifest_sha),
                    "asset_sha256": str(output["sha256"]),
                    "privacy_review_required": True,
                }
            elif asset_role == "deterministic-animation":
                animation_manifest_raw = scene.get("animation_manifest")
                animation_manifest_sha = scene.get("animation_manifest_sha256")
                if not animation_manifest_raw or not animation_manifest_sha:
                    raise VideoError("deterministic-animation 场景必须提供 animation manifest 和 SHA-256。")
                animation_manifest = safe_input(
                    path.parent, animation_manifest_raw, f"scenes[{index}].animation_manifest", {".json"}
                )
                if sha256_file(animation_manifest) != animation_manifest_sha:
                    raise VideoError("deterministic-animation manifest 哈希不匹配。")
                try:
                    animation_data = json.loads(animation_manifest.read_text(encoding="utf-8"))
                    animation_schema = json.loads(ANIMATION_SCHEMA.read_text(encoding="utf-8"))
                    Draft202012Validator(animation_schema).validate(animation_data)
                except (OSError, json.JSONDecodeError, JsonSchemaError) as exc:
                    raise VideoError(f"deterministic-animation manifest 不符合公开 Schema：{exc}") from exc
                output = animation_data.get("output") if isinstance(animation_data, dict) else None
                if (
                    animation_data.get("status") != "rendered-validated"
                    or not isinstance(output, dict)
                    or output.get("sha256") != sha256_file(asset)
                    or output.get("has_audio") is not False
                    or animation_data.get("publication_authorized") is not False
                ):
                    raise VideoError("deterministic-animation manifest 状态或素材哈希无效。")
                asset_duration = float(output.get("duration_seconds") or 0)
                if asset_duration + 0.05 < duration:
                    raise VideoError("deterministic-animation 时长短于计划场景时长。")
                scene["_asset_duration"] = asset_duration
                scene["_animation_source"] = {
                    "engine": str((animation_data.get("render") or {}).get("engine") or ""),
                    "scene_id": scene_id,
                    "manifest_file": str(animation_manifest_raw),
                    "manifest_sha256": str(animation_manifest_sha),
                    "asset_sha256": str(output["sha256"]),
                    "html_sha256": str((animation_data.get("source") or {}).get("html_sha256") or ""),
                }
            else:
                raise VideoError("video 场景必须使用 generated-broll、screen-recording 或 deterministic-animation。")
        elif layout == "product-demo":
            raise VideoError("product-demo 的每个场景都必须使用产品截图、已审核卡片或验证过的 B-roll。")
        if layout == "card-sequence" and (
            scene.get("type") != "screenshot" or scene.get("asset_role") != "rendered-card"
        ):
            raise VideoError("card-sequence 的每个场景都必须使用有来源清单的 rendered-card。")
        if provider == "user-audio":
            safe_input(path.parent, scene.get("audio_file"), f"scenes[{index}].audio_file", {".wav"})
    if not 3 <= total <= 45:
        raise VideoError("计划总时长必须在 3 到 45 秒之间。")
    validate_evidence_mix(layout, scenes, [float(scene["duration"]) for scene in scenes])
    return plan


def resolve_font(plan: dict[str, Any], plan_path: Path) -> Path:
    raw = (plan.get("style") or {}).get("font_file")
    if raw:
        return safe_input(plan_path.parent, raw, "style.font_file", {".ttf", ".otf", ".ttc"})
    if DEFAULT_FONT.is_file():
        return DEFAULT_FONT
    fallback = Path(r"C:\Windows\Fonts\simhei.ttf")
    if fallback.is_file():
        return fallback
    raise VideoError("未找到中文字体；请在 style.font_file 指定发布包内字体。")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def subtitle_font_size(plan: dict[str, Any]) -> int:
    width = int(plan["canvas"]["width"])
    base_size = int((plan.get("style") or {}).get("subtitle_size", 64))
    return round(base_size * width / 1080)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int, max_lines: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for char in paragraph:
            candidate = current + char
            if draw.textbbox((0, 0), candidate, font=face)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = char
                if len(lines) >= max_lines:
                    break
        if current and len(lines) < max_lines:
            lines.append(current)
        if len(lines) >= max_lines:
            break
    if len(lines) == max_lines and "".join(lines) != text.replace("\n", ""):
        while lines[-1] and draw.textbbox((0, 0), lines[-1] + "…", font=face)[2] > max_width:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "…"
    return lines


def balanced_two_lines(
    draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int
) -> list[str]:
    compact = text.replace("\n", "").strip()
    if draw.textbbox((0, 0), compact, font=face)[2] <= max_width:
        return [compact]
    closing = set("，。！？；：、）》】」』,.!?;:")
    opening = set("《【「『(")
    best: tuple[float, list[str]] | None = None
    for index in range(1, len(compact)):
        left, right = compact[:index].rstrip(), compact[index:].lstrip()
        if not left or not right or right[0] in closing or left[-1] in opening:
            continue
        left_width = draw.textbbox((0, 0), left, font=face)[2]
        right_width = draw.textbbox((0, 0), right, font=face)[2]
        if left_width > max_width or right_width > max_width:
            continue
        semantic_bonus = max_width if left[-1] in closing else 0
        score = abs(left_width - right_width) + max(left_width, right_width) * 0.05 - semantic_bonus
        if best is None or score < best[0]:
            best = (score, [left, right])
    return best[1] if best else wrap_text(draw, compact, face, max_width, 2)


def draw_lines(draw: ImageDraw.ImageDraw, lines: list[str], xy: tuple[int, int], face: ImageFont.FreeTypeFont, fill: str, spacing: int) -> int:
    x, y = xy
    height = face.size + spacing
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += height
    return y


def draw_outlined_subtitles(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    *,
    width: int,
    top: int,
    face: ImageFont.FreeTypeFont,
    spacing: int,
    stroke_width: int,
) -> None:
    line_height = face.size + spacing
    for index, line in enumerate(lines):
        box = draw.textbbox((0, 0), line, font=face, stroke_width=stroke_width)
        line_width = box[2] - box[0]
        x = max(24, (width - line_width) // 2)
        y = top + index * line_height
        draw.text(
            (x + 2, y + 3), line, font=face, fill="#000000A6",
            stroke_width=stroke_width + 1, stroke_fill="#000000A6",
        )
        draw.text(
            (x, y), line, font=face, fill="#FFFFFF",
            stroke_width=stroke_width, stroke_fill="#11131AE6",
        )


def rounded_contain(
    image: Image.Image, size: tuple[int, int], radius: int = 28
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    target_w, target_h = size
    ratio = min(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (max(1, math.floor(image.width * ratio)), max(1, math.floor(image.height * ratio))),
        Image.Resampling.LANCZOS,
    ).convert("RGBA")
    left = (target_w - resized.width) // 2
    top = (target_h - resized.height) // 2
    canvas = Image.new("RGBA", size, "white")
    canvas.alpha_composite(resized, (left, top))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, target_w, target_h), radius=radius, fill=255)
    canvas.putalpha(mask)
    return canvas, (left, top, left + resized.width, top + resized.height)


def draw_cursor(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    points = [
        (x, y),
        (x, y + size),
        (x + int(size * 0.28), y + int(size * 0.73)),
        (x + int(size * 0.48), y + int(size * 1.15)),
        (x + int(size * 0.69), y + int(size * 1.05)),
        (x + int(size * 0.49), y + int(size * 0.65)),
        (x + int(size * 0.84), y + int(size * 0.61)),
    ]
    draw.polygon(points, fill="#FFFFFF", outline="#111111", width=max(4, size // 18))


def product_demo_frame(
    plan: dict[str, Any], scene: dict[str, Any], plan_path: Path, output: Path
) -> None:
    width = int(plan["canvas"]["width"])
    height = int(plan["canvas"]["height"])
    style = {
        "background": "#08090C",
        "foreground": "#FFFFFF",
        "accent": "#6650E8",
        "muted": "#C8CBD4",
        **(plan.get("style") or {}),
    }
    font_path = resolve_font(plan, plan_path)
    image = Image.new("RGB", (width, height), style["background"])
    draw = ImageDraw.Draw(image)
    scale = width / 1440
    margin = round(68 * scale)
    mark_size = round(88 * scale)
    mark_x, mark_y = margin, round(58 * scale)
    draw.rounded_rectangle(
        (mark_x, mark_y, mark_x + mark_size, mark_y + mark_size),
        radius=round(20 * scale),
        fill=style["foreground"],
    )
    brand_mark = str(style.get("brand_mark") or "G")
    mark_face = font(font_path, round(52 * scale))
    mark_box = draw.textbbox((0, 0), brand_mark, font=mark_face)
    draw.text(
        (
            mark_x + (mark_size - (mark_box[2] - mark_box[0])) // 2,
            mark_y + (mark_size - (mark_box[3] - mark_box[1])) // 2 - mark_box[1],
        ),
        brand_mark,
        font=mark_face,
        fill=style["background"],
    )
    draw.text(
        (mark_x + mark_size + round(28 * scale), mark_y + round(17 * scale)),
        plan["title"],
        font=font(font_path, round(46 * scale)),
        fill=style["foreground"],
    )

    hook_text = str(scene.get("hook") or "").strip()
    if hook_text:
        hook_face = font(font_path, round(82 * scale))
        hook_lines = wrap_text(draw, hook_text, hook_face, width - 2 * margin, 2)
        hook_y = round(215 * scale)
        for line in hook_lines:
            line_box = draw.textbbox((0, 0), line, font=hook_face, stroke_width=round(10 * scale))
            line_x = (width - (line_box[2] - line_box[0])) // 2
            draw.text(
                (line_x, hook_y), line, font=hook_face, fill=style["foreground"],
                stroke_width=round(10 * scale), stroke_fill=style["accent"],
            )
            hook_y += round(108 * scale)

    demo_top = round((445 if hook_text else 265) * scale)
    demo_bottom = round(1395 * (height / 1920))
    box = (margin, demo_top, width - margin, demo_bottom)
    draw.rounded_rectangle(
        (box[0] - round(8 * scale), box[1] - round(8 * scale), box[2] + round(8 * scale), box[3] + round(8 * scale)),
        radius=round(34 * scale), fill="#FFFFFF", outline=style["accent"], width=round(3 * scale),
    )
    content_box = (0, 0, box[2] - box[0], box[3] - box[1])
    if scene["type"] == "screenshot":
        source = safe_input(
            plan_path.parent, scene["asset"], f"scene {scene['id']} asset",
            {".png", ".jpg", ".jpeg", ".webp"},
        )
        with Image.open(source) as source_image:
            shot, content_box = rounded_contain(
                source_image.convert("RGB"), (box[2] - box[0], box[3] - box[1]),
                radius=round(26 * scale),
            )
        image.paste(shot, (box[0], box[1]), shot)
        draw = ImageDraw.Draw(image)
        highlight = scene.get("highlight")
        content_w = content_box[2] - content_box[0]
        content_h = content_box[3] - content_box[1]
        if isinstance(highlight, dict):
            x1 = box[0] + content_box[0] + int(float(highlight["x"]) * content_w)
            y1 = box[1] + content_box[1] + int(float(highlight["y"]) * content_h)
            x2 = x1 + int(float(highlight["width"]) * content_w)
            y2 = y1 + int(float(highlight["height"]) * content_h)
            draw.rounded_rectangle(
                (x1, y1, x2, y2), radius=round(16 * scale),
                outline=style["accent"], width=round(10 * scale),
            )
        cursor = scene.get("cursor")
        if isinstance(cursor, dict):
            cursor_size = round(float(cursor.get("size", 0.1)) * content_w)
            cursor_x = box[0] + content_box[0] + int(float(cursor["x"]) * content_w)
            cursor_y = box[1] + content_box[1] + int(float(cursor["y"]) * content_h)
            draw_cursor(draw, cursor_x, cursor_y, cursor_size)
    else:
        draw.rectangle(box, fill="#11131A")
        panel_face = font(font_path, round(64 * scale))
        panel_lines = wrap_text(draw, str(scene.get("body") or scene["heading"]), panel_face, box[2] - box[0] - 120, 4)
        panel_y = box[1] + (box[3] - box[1] - len(panel_lines) * round(84 * scale)) // 2
        draw_lines(draw, panel_lines, (box[0] + round(60 * scale), panel_y), panel_face, style["foreground"], round(20 * scale))

    heading_face = font(font_path, round(76 * scale))
    heading_lines = wrap_text(draw, scene["heading"], heading_face, width - 2 * margin, 2)
    caption_y = demo_bottom + round(72 * scale)
    draw_lines(draw, heading_lines, (margin, caption_y), heading_face, style["foreground"], round(20 * scale))
    body_text = str(scene.get("body") or "").strip()
    if body_text and scene["type"] == "screenshot":
        body_face = font(font_path, round(39 * scale))
        body_y = caption_y + len(heading_lines) * round(96 * scale) + round(14 * scale)
        draw_lines(draw, wrap_text(draw, body_text, body_face, width - 2 * margin, 2), (margin, body_y), body_face, style["muted"], round(14 * scale))
    narration = str(scene.get("narration") or "").strip()
    if narration and not scene.get("subtitle_cues") and str(scene.get("overlay_mode") or "full") != "none":
        subtitle_face = font(font_path, subtitle_font_size(plan))
        subtitle_lines = balanced_two_lines(draw, narration, subtitle_face, width - round(120 * scale))
        line_height = round(74 * scale)
        total_h = len(subtitle_lines) * line_height
        draw_outlined_subtitles(
            draw, subtitle_lines, width=width,
            top=height - round(245 * (height / 1920)) - total_h,
            face=subtitle_face, spacing=round(22 * scale), stroke_width=max(3, round(4 * scale)),
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def card_sequence_frame(
    plan: dict[str, Any], scene: dict[str, Any], plan_path: Path, output: Path
) -> None:
    width = int(plan["canvas"]["width"])
    height = int(plan["canvas"]["height"])
    source = safe_input(
        plan_path.parent, scene["asset"], f"scene {scene['id']} asset",
        {".png", ".jpg", ".jpeg", ".webp"},
    )
    with Image.open(source) as source_image:
        image = ImageOps.fit(
            source_image.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def scene_frame(plan: dict[str, Any], scene: dict[str, Any], plan_path: Path, output: Path) -> None:
    if (plan.get("style") or {}).get("layout") == "card-sequence":
        card_sequence_frame(plan, scene, plan_path, output)
        return
    if (plan.get("style") or {}).get("layout") == "product-demo":
        if scene.get("asset_role") == "rendered-card":
            card_sequence_frame(plan, scene, plan_path, output)
            return
        product_demo_frame(plan, scene, plan_path, output)
        return
    width = int(plan["canvas"]["width"])
    height = int(plan["canvas"]["height"])
    style = {"background": "#F6F7FB", "foreground": "#10131C", "accent": "#4F35E8", "muted": "#626A7F", **(plan.get("style") or {})}
    font_path = resolve_font(plan, plan_path)
    image = Image.new("RGB", (width, height), style["background"])
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((72, 70, 152, 150), radius=18, fill=style["foreground"])
    draw.text((98, 77), "G", font=font(font_path, 46), fill="#FFFFFF")
    draw.text((176, 84), plan["title"], font=font(font_path, 38), fill=style["foreground"])
    heading_size = 86 if scene["type"] in {"title", "cta"} else 64
    heading = font(font_path, heading_size)
    heading_lines = wrap_text(draw, scene["heading"], heading, 900, 3)
    y = draw_lines(draw, heading_lines, (72, 230), heading, style["foreground"], 22)
    body_text = str(scene.get("body") or "").strip()
    if body_text:
        body = font(font_path, 39)
        y = draw_lines(draw, wrap_text(draw, body_text, body, 900, 4), (72, y + 22), body, style["muted"], 16)
    if scene["type"] == "screenshot":
        source = safe_input(plan_path.parent, scene["asset"], f"scene {scene['id']} asset", {".png", ".jpg", ".jpeg", ".webp"})
        box = (82, max(650, y + 70), 998, 1640)
        draw.rounded_rectangle((box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10), radius=38, fill="#FFFFFF", outline="#DADDE8", width=3)
        with Image.open(source) as source_image:
            shot, content_box = rounded_contain(
                source_image.convert("RGB"), (box[2] - box[0], box[3] - box[1])
            )
        image.paste(shot, (box[0], box[1]), shot)
        highlight = scene.get("highlight")
        if isinstance(highlight, dict):
            content_w = content_box[2] - content_box[0]
            content_h = content_box[3] - content_box[1]
            x1 = box[0] + content_box[0] + int(float(highlight["x"]) * content_w)
            y1 = box[1] + content_box[1] + int(float(highlight["y"]) * content_h)
            x2 = x1 + int(float(highlight["width"]) * content_w)
            y2 = y1 + int(float(highlight["height"]) * content_h)
            draw.rounded_rectangle((x1, y1, x2, y2), radius=18, outline=style["accent"], width=10)
    elif scene["type"] == "title":
        draw.rounded_rectangle((72, 1050, 1008, 1490), radius=42, fill="#FFFFFF", outline="#DADDE8", width=3)
        draw.text((126, 1140), "产品截图驱动", font=font(font_path, 48), fill=style["accent"])
        draw.text((126, 1240), "真实界面 · 清晰字幕 · 克制动效", font=font(font_path, 42), fill=style["foreground"])
    elif scene["type"] == "cta":
        draw.rounded_rectangle((72, 1110, 1008, 1390), radius=42, fill=style["accent"])
        cta = font(font_path, 48)
        lines = wrap_text(draw, body_text or scene["heading"], cta, 820, 2)
        draw_lines(draw, lines, (126, 1180), cta, "#FFFFFF", 18)
    elif scene["type"] == "text":
        draw.rounded_rectangle((72, 900, 1008, 1460), radius=42, fill="#FFFFFF", outline="#DADDE8", width=3)
        draw.rounded_rectangle((106, 952, 124, 1360), radius=9, fill=style["accent"])
        panel = font(font_path, 46)
        panel_lines = wrap_text(draw, body_text or scene["heading"], panel, 780, 5)
        draw_lines(draw, panel_lines, (168, 1000), panel, style["foreground"], 24)
    narration = str(scene.get("narration") or "").strip()
    if narration and not scene.get("subtitle_cues"):
        subtitle = font(font_path, subtitle_font_size(plan))
        subtitle_lines = balanced_two_lines(draw, narration, subtitle, 930)
        total_h = len(subtitle_lines) * 72
        draw_outlined_subtitles(
            draw, subtitle_lines, width=width, top=height - 86 - total_h,
            face=subtitle, spacing=20, stroke_width=4,
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def generated_video_overlay(plan: dict[str, Any], scene: dict[str, Any], plan_path: Path, output: Path) -> None:
    width = int(plan["canvas"]["width"])
    height = int(plan["canvas"]["height"])
    scale = width / 1080
    style = {
        "foreground": "#FFFFFF", "accent": "#6CFF9A", "muted": "#D7DBE7",
        **(plan.get("style") or {}),
    }
    font_path = resolve_font(plan, plan_path)
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    overlay_mode = str(scene.get("overlay_mode") or "full")
    margin = round(64 * scale)
    top = round(58 * scale)
    panel_bottom = round(410 * scale)
    if overlay_mode == "full":
        draw.rounded_rectangle(
            (margin, top, width - margin, panel_bottom),
            radius=round(30 * scale),
            fill=(8, 10, 15, 190),
        )
        draw.text(
            (margin + round(34 * scale), top + round(25 * scale)),
            plan["title"],
            font=font(font_path, round(34 * scale)),
            fill=style["accent"],
        )
        heading_face = font(font_path, round(68 * scale))
        heading_lines = wrap_text(draw, scene["heading"], heading_face, width - 2 * margin - round(68 * scale), 2)
        y = draw_lines(
            draw, heading_lines, (margin + round(34 * scale), top + round(92 * scale)),
            heading_face, style["foreground"], round(16 * scale),
        )
        body_text = str(scene.get("body") or "").strip()
        if body_text:
            body_face = font(font_path, round(35 * scale))
            draw_lines(
                draw, wrap_text(draw, body_text, body_face, width - 2 * margin - round(68 * scale), 2),
                (margin + round(34 * scale), y + round(12 * scale)),
                body_face, style["muted"], round(12 * scale),
            )
    narration = str(scene.get("narration") or "").strip()
    if narration and not scene.get("subtitle_cues") and overlay_mode != "none":
        subtitle_face = font(font_path, subtitle_font_size(plan))
        subtitle_lines = balanced_two_lines(
            draw, narration, subtitle_face, width - round(120 * scale)
        )
        line_height = round(74 * scale)
        total_h = len(subtitle_lines) * line_height
        draw_outlined_subtitles(
            draw, subtitle_lines, width=width,
            top=height - round(245 * (height / 1920)) - total_h,
            face=subtitle_face, spacing=round(22 * scale), stroke_width=max(3, round(4 * scale)),
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def subtitle_overlay(
    plan: dict[str, Any], scene: dict[str, Any], text: str, plan_path: Path, output: Path
) -> None:
    width = int(plan["canvas"]["width"])
    height = int(plan["canvas"]["height"])
    scale = width / 1080
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    face = font(resolve_font(plan, plan_path), subtitle_font_size(plan))
    lines = balanced_two_lines(draw, text, face, width - round(120 * scale))
    line_height = round(74 * scale)
    draw_outlined_subtitles(
        draw,
        lines,
        width=width,
        top=height - round(245 * (height / 1920)) - len(lines) * line_height,
        face=face,
        spacing=round(22 * scale),
        stroke_width=max(3, round(4 * scale)),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def srt_time(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def write_srt(scenes: list[dict[str, Any]], durations: list[float], path: Path) -> None:
    cursor = 0.0
    blocks: list[str] = []
    number = 1
    for scene, duration in zip(scenes, durations):
        narration = str(scene.get("narration") or "").strip()
        cues = scene.get("subtitle_cues") or []
        if cues:
            for cue in cues:
                blocks.append(
                    f"{number}\n{srt_time(cursor + float(cue['start']))} --> "
                    f"{srt_time(cursor + float(cue['end']))}\n{str(cue['text']).strip()}\n"
                )
                number += 1
        elif narration:
            blocks.append(f"{number}\n{srt_time(cursor)} --> {srt_time(cursor + duration)}\n{narration}\n")
            number += 1
        cursor += duration
    path.write_text("\n".join(blocks), encoding="utf-8")


def synthesize_sapi(text: str, output: Path, voice_name: str, rate: int) -> None:
    script_path = output.parent / "_growth_lab_sapi.ps1"
    script_path.write_text(
        "param([string]$Text,[string]$Output,[string]$Voice,[int]$Rate)\n"
        "Add-Type -AssemblyName System.Speech\n"
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
        "try {\n"
        "  if($Voice){$s.SelectVoice($Voice)}\n"
        "  $s.Rate=$Rate\n"
        "  $s.SetOutputToWaveFile($Output)\n"
        "  $s.Speak($Text)\n"
        "} finally { $s.Dispose() }\n",
        encoding="utf-8-sig",
    )
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", str(script_path), "-Text", text, "-Output", str(output),
                "-Voice", voice_name, "-Rate", str(rate),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        script_path.unlink(missing_ok=True)
    if result.returncode != 0 or not output.is_file():
        raise VideoError("Windows SAPI 配音失败：" + result.stderr.strip()[:300])


def local_tts_python() -> str:
    configured = os.environ.get("SOCIAL_TTS_PYTHON", "").strip()
    path = Path(os.path.expandvars(os.path.expanduser(configured))) if configured else (
        Path.home() / ".growth-lab" / "clients" / "social-tts-venv" / "Scripts" / "python.exe"
    )
    if not path.is_file():
        raise VideoError("未找到本地 TTS 环境；请配置 SOCIAL_TTS_PYTHON。")
    return str(path)


def synthesize_local_tts(scenes: list[dict[str, Any]], voice: dict[str, Any], audio_dir: Path) -> tuple[dict[str, Path], dict[str, Any]]:
    narrated_scenes = [scene for scene in scenes if str(scene.get("narration") or "").strip()]
    items = [
        {
            "id": scene["id"],
            "text": str(scene.get("narration") or "").strip(),
            "output": f"{index:02}-{scene['id']}.wav",
        }
        for index, scene in enumerate(narrated_scenes, start=1)
    ]
    if not items:
        raise VideoError("local-tts 模式至少需要一条 narration。")
    request_path = audio_dir / "_tts-request.json"
    request_path.write_text(
        json.dumps({"schema_version": 1, "voice": voice, "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    try:
        result = subprocess.run(
            [local_tts_python(), str(LOCAL_TTS_SCRIPT), "--request", str(request_path), "--out", str(audio_dir)],
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired as exc:
        raise VideoError("本地 TTS 超过 600 秒超时。") from exc
    finally:
        request_path.unlink(missing_ok=True)
    if result.returncode != 0:
        raise VideoError("本地 TTS 配音失败：" + (result.stderr or result.stdout)[-800:])
    manifest_path = audio_dir / "tts-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VideoError("本地 TTS 未生成有效清单。") from exc
    outputs = {item["scene_id"]: audio_dir / item["file"] for item in manifest.get("outputs", [])}
    if any(not path.is_file() for path in outputs.values()):
        raise VideoError("本地 TTS 清单引用了缺失音频。")
    return outputs, manifest


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def ffmpeg_executable() -> str:
    configured = os.environ.get("VIDEO_FFMPEG_PATH", "").strip()
    if configured:
        path = Path(os.path.expandvars(os.path.expanduser(configured)))
        if path.is_file():
            return str(path)
        raise VideoError("VIDEO_FFMPEG_PATH 指向的文件不存在。")
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise VideoError("未找到 FFmpeg；请使用视频专用 venv 或配置 VIDEO_FFMPEG_PATH。") from exc


def run_ffmpeg(command: list[str], timeout: int = 180) -> None:
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise VideoError("FFmpeg 执行失败：" + result.stderr[-1000:])


def motion_filter(motion: str, duration: float, fps: int, width: int, height: int) -> str:
    fade_out = max(0.0, duration - 0.22)
    if motion == "slow-zoom":
        frames = max(1, round(duration * fps))
        base = f"zoompan=z='min(zoom+0.0007,1.045)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s={width}x{height}:fps={fps}"
    elif motion == "pan-up":
        scaled_height = height + 120
        base = f"scale={width}:{scaled_height},crop={width}:{height}:0:'min(120,t*18)'"
    else:
        base = f"scale={width}:{height}"
    return base + f",fade=t=in:st=0:d=0.22,fade=t=out:st={fade_out:.3f}:d=0.22,format=yuv420p"


def screen_recording_filter(width: int, height: int) -> str:
    enlarged_width = math.ceil(width * 1.12 / 2) * 2
    return (
        f"scale={enlarged_width}:-2,"
        f"crop={width}:ih:(iw-ow)*0.85:0,"
        f"pad={width}:{height}:0:(oh-ih)/2:color=0xF8F7FC"
    )


def video_metadata(path: Path) -> dict[str, Any]:
    try:
        import imageio_ffmpeg
        reader = imageio_ffmpeg.read_frames(str(path), pix_fmt="rgb24")
        metadata = next(reader)
        reader.close()
    except Exception as exc:
        raise VideoError("无法读取成片元数据。") from exc
    return metadata


def extract_review_frames(ffmpeg: str, video: Path, duration: float, directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for index, ratio in enumerate((0.1, 0.5, 0.9), start=1):
        target = directory / f"review-{index}.png"
        run_ffmpeg([ffmpeg, "-y", "-ss", f"{duration * ratio:.3f}", "-i", str(video), "-frames:v", "1", str(target)], timeout=60)
        with Image.open(target) as review_image:
            stat = ImageStat.Stat(review_image.convert("RGB"))
        if max(stat.var) < 2:
            raise VideoError(f"抽检帧疑似空白：{target.name}")
        outputs.append(target)
    return outputs


def render(plan_path: Path, output_dir: Path) -> dict[str, Any]:
    package_dir = plan_path.parent
    script_path = package_dir / "video-script.json"
    evidence_path = package_dir / "asset-evidence-ledger.json"
    gate = subprocess.run(
        [
            sys.executable, str(SCRIPT_COVERAGE_VALIDATOR),
            "--script", str(script_path),
            "--evidence", str(evidence_path),
            "--plan", str(plan_path),
            "--for-production",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if gate.returncode != 0:
        detail = (gate.stdout or gate.stderr).strip()
        raise VideoError(f"完整脚本与素材证据门槛未通过：{detail[-1200:]}")
    plan = read_plan(plan_path)
    ffmpeg = ffmpeg_executable()
    version_result = subprocess.run([ffmpeg, "-version"], capture_output=True, text=True, timeout=15)
    if version_result.returncode != 0:
        raise VideoError("FFmpeg 版本检查失败。")
    ffmpeg_version = version_result.stdout.splitlines()[0].strip()
    output_dir.mkdir(parents=True, exist_ok=True)
    render_dir = output_dir / "render"
    raw_dir = output_dir / "raw"
    frames_dir = raw_dir / "frames"
    subtitle_frames_dir = raw_dir / "subtitle-frames"
    audio_dir = raw_dir / "audio"
    segments_dir = raw_dir / "segments"
    for directory in (render_dir, frames_dir, subtitle_frames_dir, audio_dir, segments_dir):
        directory.mkdir(parents=True, exist_ok=True)
    scenes = plan["scenes"]
    provider = plan["voice"]["provider"]
    fps = int(plan["canvas"]["fps"])
    width = int(plan["canvas"]["width"])
    height = int(plan["canvas"]["height"])
    durations: list[float] = []
    segments: list[Path] = []
    local_audio: dict[str, Path] = {}
    local_voice_manifest: dict[str, Any] | None = None
    if provider == "local-tts":
        local_audio, local_voice_manifest = synthesize_local_tts(scenes, plan["voice"], audio_dir)
    for index, scene in enumerate(scenes, start=1):
        frame = frames_dir / f"{index:02}-{scene['id']}.png"
        is_generated_video = scene["type"] == "video"
        if is_generated_video:
            generated_video_overlay(plan, scene, plan_path, frame)
        else:
            scene_frame(plan, scene, plan_path, frame)
        subtitle_cues = scene.get("subtitle_cues") or []
        subtitle_frames: list[Path] = []
        for cue_index, cue in enumerate(subtitle_cues, start=1):
            cue_frame = subtitle_frames_dir / f"{index:02}-{scene['id']}-{cue_index:02}.png"
            subtitle_overlay(plan, scene, str(cue["text"]), plan_path, cue_frame)
            subtitle_frames.append(cue_frame)
        audio: Path | None = None
        duration = float(scene["duration"])
        narration = str(scene.get("narration") or "").strip()
        if provider == "windows-sapi" and narration:
            audio = audio_dir / f"{index:02}-{scene['id']}.wav"
            synthesize_sapi(narration, audio, str(plan["voice"].get("voice_name") or ""), int(plan["voice"].get("rate", 0)))
            duration = max(duration, wav_duration(audio) + 0.45)
        elif provider == "local-tts" and narration:
            audio = local_audio.get(scene["id"])
            if not audio:
                raise VideoError(f"场景 {scene['id']} 缺少本地 TTS 音频。")
            duration = max(duration, wav_duration(audio) + 0.45)
        elif provider == "user-audio":
            audio = safe_input(plan_path.parent, scene["audio_file"], f"scene {scene['id']} audio", {".wav"})
            duration = max(duration, wav_duration(audio) + 0.2)
        if duration > 12:
            raise VideoError(f"场景 {scene['id']} 配音后超过 12 秒；请缩短旁白。")
        if is_generated_video and duration > float(scene["_asset_duration"]) + 0.05:
            raise VideoError(f"场景 {scene['id']} 的配音时长超过视频素材。")
        durations.append(duration)
        segment = segments_dir / f"{index:02}.mp4"
        if is_generated_video:
            source_video = safe_input(
                plan_path.parent, scene["asset"], f"scene {scene['id']} asset", {".mp4"}
            )
            command = [
                ffmpeg, "-y", "-i", str(source_video),
                "-loop", "1", "-framerate", str(fps), "-i", str(frame),
            ]
            for subtitle_frame in subtitle_frames:
                command += ["-loop", "1", "-framerate", str(fps), "-i", str(subtitle_frame)]
            if audio:
                command += ["-i", str(audio)]
            else:
                command += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
            audio_input = 2 + len(subtitle_frames)
            fade_out = max(0.0, duration - 0.22)
            if scene.get("asset_role") == "screen-recording":
                source_filter = screen_recording_filter(width, height)
            else:
                source_filter = (
                    f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                    f"crop={width}:{height}"
                )
            filters = [f"[0:v]{source_filter}[base]", "[base][1:v]overlay=0:0[visual0]"]
            current = "visual0"
            for cue_index, cue in enumerate(subtitle_cues, start=1):
                next_label = f"visual{cue_index}"
                filters.append(
                    f"[{current}][{cue_index + 1}:v]overlay=0:0:"
                    f"enable='between(t,{float(cue['start']):.3f},{float(cue['end']):.3f})'[{next_label}]"
                )
                current = next_label
            filters.append(
                f"[{current}]fade=t=in:st=0:d=0.22,fade=t=out:st={fade_out:.3f}:d=0.22,format=yuv420p[v]"
            )
            video_filter = ";".join(filters)
            command += [
                "-filter_complex", video_filter, "-map", "[v]", "-map", f"{audio_input}:a:0",
                "-t", f"{duration:.3f}", "-r", str(fps),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
                "-movflags", "+faststart", str(segment),
            ]
        else:
            command = [ffmpeg, "-y", "-loop", "1", "-framerate", str(fps), "-i", str(frame)]
            for subtitle_frame in subtitle_frames:
                command += ["-loop", "1", "-framerate", str(fps), "-i", str(subtitle_frame)]
            if audio:
                command += ["-i", str(audio)]
            else:
                command += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
            audio_input = 1 + len(subtitle_frames)
            if subtitle_frames:
                filters = [f"[0:v]{motion_filter(scene['motion'], duration, fps, width, height)}[visual0]"]
                current = "visual0"
                for cue_index, cue in enumerate(subtitle_cues, start=1):
                    next_label = f"visual{cue_index}"
                    filters.append(
                        f"[{current}][{cue_index}:v]overlay=0:0:"
                        f"enable='between(t,{float(cue['start']):.3f},{float(cue['end']):.3f})'[{next_label}]"
                    )
                    current = next_label
                filters.append(f"[{current}]format=yuv420p[v]")
                command += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", f"{audio_input}:a:0"]
            else:
                command += ["-vf", motion_filter(scene["motion"], duration, fps, width, height)]
            command += [
                "-t", f"{duration:.3f}",
                "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
                "-movflags", "+faststart", str(segment),
            ]
        run_ffmpeg(command)
        segments.append(segment)
    total_duration = sum(durations)
    if total_duration > 45.5:
        raise VideoError("配音扩展后的总时长超过 45 秒。")
    final_evidence_mix = validate_evidence_mix(
        (plan.get("style") or {}).get("layout", "classic"), scenes, durations
    )
    concat_file = raw_dir / "segments.txt"
    concat_file.write_text("\n".join(f"file '{path.as_posix()}'" for path in segments), encoding="utf-8")
    final_video = render_dir / "final.mp4"
    run_ffmpeg([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", "-movflags", "+faststart", str(final_video)])
    cover = render_dir / "cover.png"
    run_ffmpeg([ffmpeg, "-y", "-ss", "0.250", "-i", str(final_video), "-frames:v", "1", str(cover)], timeout=60)
    subtitles = render_dir / "subtitles.srt"
    write_srt(scenes, durations, subtitles)
    metadata = video_metadata(final_video)
    size = metadata.get("size") or (0, 0)
    actual_duration = float(metadata.get("duration") or total_duration)
    if tuple(size) != (width, height) or not 3 <= actual_duration <= 45.5:
        raise VideoError(f"成片元数据不合格：size={size}, duration={actual_duration}")
    if metadata.get("codec") != "h264" or metadata.get("audio_codec") != "aac":
        raise VideoError(
            f"成片编码不合格：video={metadata.get('codec')}, audio={metadata.get('audio_codec')}"
        )
    review_frames = extract_review_frames(ffmpeg, final_video, actual_duration, raw_dir / "review-frames")
    manifest = {
        "schema_version": 1,
        "status": "rendered-not-published",
        "plan_sha256": sha256_file(plan_path),
        "renderer": {"name": "growth-lab-ffmpeg-pillow", "ffmpeg_version": ffmpeg_version, "external_binary": True},
        "files": {"video": "render/final.mp4", "cover": "render/cover.png", "subtitles": "render/subtitles.srt"},
        "evidence_mix": final_evidence_mix,
        "video": {
            "width": width, "height": height, "fps": float(metadata.get("fps") or fps),
            "duration_seconds": round(actual_duration, 3), "scene_count": len(scenes),
            "codec": str(metadata.get("codec")),
            "audio_codec": str(metadata.get("audio_codec")),
            "pixel_format": str(metadata.get("pix_fmt")),
            "sha256": sha256_file(final_video),
        },
    }
    if plan.get("visual_source"):
        manifest["visual_source"] = plan["visual_source"]
    if local_voice_manifest is not None:
        voice_manifest_path = audio_dir / "tts-manifest.json"
        manifest["voice_source"] = {
            "provider": "local-tts",
            "engine": local_voice_manifest["engine"],
            "model_id": local_voice_manifest["model_id"],
            "model_revision": local_voice_manifest["model_revision"],
            "voice_name": local_voice_manifest["voice_name"],
            "language": local_voice_manifest["language"],
            "speed": local_voice_manifest["speed"],
            "license": local_voice_manifest["license"],
            "manifest_file": "raw/audio/tts-manifest.json",
            "manifest_sha256": sha256_file(voice_manifest_path),
        }
    provider_sources = [scene["_provider_source"] for scene in scenes if scene.get("_provider_source")]
    if provider_sources:
        manifest["provider_sources"] = provider_sources
    capture_sources = [scene["_capture_source"] for scene in scenes if scene.get("_capture_source")]
    if capture_sources:
        manifest["capture_sources"] = capture_sources
    animation_sources = [scene["_animation_source"] for scene in scenes if scene.get("_animation_source")]
    if animation_sources:
        manifest["animation_sources"] = animation_sources
    try:
        manifest_schema = json.loads(
            (SCHEMA_DIR / "video-manifest.schema.json").read_text(encoding="utf-8")
        )
        Draft202012Validator(manifest_schema).validate(manifest)
    except (OSError, json.JSONDecodeError, JsonSchemaError) as exc:
        raise VideoError(f"生成的 video-manifest 不符合公开 Schema：{exc}") from exc
    (output_dir / "video-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review = {
        "status": "mechanical-pass-human-review-required",
        "checks": {"resolution": True, "duration": True, "h264_video": True, "aac_audio": True, "nonblank_review_frames": True, "evidence_mix": True},
        "evidence_mix": final_evidence_mix,
        "review_frames": [str(path.relative_to(output_dir)).replace("\\", "/") for path in review_frames],
        "human_checks": ["字幕断句和读速", "产品截图隐私与真实性", "标注位置", "配音听感", "最终发布设置"],
    }
    (output_dir / "video-review.json").write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a deterministic Growth Lab social video")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = render(Path(args.plan).resolve(), Path(args.out).resolve())
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VideoError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
