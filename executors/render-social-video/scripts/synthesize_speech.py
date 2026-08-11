#!/usr/bin/env python3
"""Synthesize a bounded batch of Mandarin narration with pinned Kokoro assets."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
from typing import Any, Callable
import wave


MODEL_ID = "hexgrad/Kokoro-82M-v1.1-zh"
MODEL_REVISION = "01e7505bd6a7a2ac4975463114c3a7650a9f7218"
MODEL_FILE = "kokoro-v1_1-zh.pth"
LICENSE = "Apache-2.0"
VOICE_PATTERN = re.compile(r"z[fm]_\d{3}")
SCENE_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,31}")


class SpeechError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_request(path: Path) -> dict[str, Any]:
    try:
        request = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpeechError("TTS request 不存在或不是有效 JSON。") from exc
    if not isinstance(request, dict) or request.get("schema_version") != 1:
        raise SpeechError("TTS request schema_version 必须为 1。")
    config = request.get("voice")
    items = request.get("items")
    if not isinstance(config, dict) or not isinstance(items, list) or not 1 <= len(items) <= 8:
        raise SpeechError("TTS request 必须包含 voice 和 1 到 8 条 items。")
    expected = {
        "engine": "kokoro",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "license": LICENSE,
        "language": "zh",
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise SpeechError(f"voice.{key} 必须为 {value}。")
    voice = str(config.get("voice_name") or "")
    speed = config.get("speed", 1.0)
    if not VOICE_PATTERN.fullmatch(voice):
        raise SpeechError("voice.voice_name 必须是 Kokoro 中文音色 ID，例如 zf_001。")
    if not isinstance(speed, (int, float)) or not 0.8 <= float(speed) <= 1.2:
        raise SpeechError("voice.speed 必须在 0.8 到 1.2 之间。")
    ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise SpeechError(f"items[{index}] 必须是对象。")
        scene_id = str(item.get("id") or "")
        text = str(item.get("text") or "").strip()
        output = str(item.get("output") or "")
        if not SCENE_ID_PATTERN.fullmatch(scene_id) or scene_id in ids:
            raise SpeechError(f"items[{index}].id 无效或重复。")
        if not text or len(text) > 300:
            raise SpeechError(f"items[{index}].text 必须为 1 到 300 个字符。")
        if output != f"{index + 1:02}-{scene_id}.wav":
            raise SpeechError(f"items[{index}].output 不符合受控命名规则。")
        segments = item.get("segments") or []
        segment_ids: set[str] = set()
        for segment_index, segment in enumerate(segments):
            if not isinstance(segment, dict):
                raise SpeechError(f"items[{index}].segments[{segment_index}] 必须是对象。")
            segment_id = str(segment.get("id") or "")
            segment_text = str(segment.get("text") or "").strip()
            pause_after_ms = segment.get("pause_after_ms")
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", segment_id) or segment_id in segment_ids:
                raise SpeechError(f"items[{index}].segments[{segment_index}].id 无效或重复。")
            if not segment_text or len(segment_text) > 80:
                raise SpeechError(f"items[{index}].segments[{segment_index}].text 必须为 1 到 80 个字符。")
            if not isinstance(pause_after_ms, int) or not 0 <= pause_after_ms <= 2000:
                raise SpeechError(f"items[{index}].segments[{segment_index}].pause_after_ms 无效。")
            segment_ids.add(segment_id)
        ids.add(scene_id)
    return request


def combine_segment_wavs(
    parts: list[tuple[dict[str, Any], Path]], output: Path
) -> list[dict[str, Any]]:
    if not parts:
        raise SpeechError("分段 TTS 没有可合并的音频。")
    timeline: list[dict[str, Any]] = []
    total_frames = 0
    expected: tuple[int, int, int] | None = None
    with wave.open(str(output), "wb") as target:
        for segment, part in parts:
            try:
                with wave.open(str(part), "rb") as source:
                    current = (source.getnchannels(), source.getsampwidth(), source.getframerate())
                    if expected is None:
                        expected = current
                        target.setnchannels(current[0])
                        target.setsampwidth(current[1])
                        target.setframerate(current[2])
                    elif current != expected:
                        raise SpeechError("分段 TTS 返回了不一致的 WAV 参数。")
                    start = total_frames / current[2]
                    frames = source.getnframes()
                    target.writeframes(source.readframes(frames))
                    total_frames += frames
                    end = total_frames / current[2]
                    pause_frames = round(current[2] * int(segment["pause_after_ms"]) / 1000)
                    if pause_frames:
                        target.writeframes(b"\x00" * pause_frames * current[0] * current[1])
                        total_frames += pause_frames
                    timeline.append({
                        "id": segment["id"],
                        "text": segment["text"],
                        "start_seconds": round(start, 3),
                        "end_seconds": round(end, 3),
                        "pause_after_ms": int(segment["pause_after_ms"]),
                    })
            except (OSError, wave.Error) as exc:
                raise SpeechError(f"分段 WAV 无效：{part.name}") from exc
    return timeline


def make_kokoro_backend(config: dict[str, Any]) -> Callable[[str, Path], dict[str, Any]]:
    try:
        import numpy as np
        import soundfile as sf
        import torch
        from huggingface_hub import hf_hub_download
        from kokoro import KModel, KPipeline
    except ImportError as exc:
        raise SpeechError("Kokoro TTS 依赖未安装；请使用独立 social-tts-venv。") from exc

    model_id = config["model_id"]
    revision = config["model_revision"]
    voice_name = config["voice_name"]
    common = {"repo_id": model_id, "revision": revision}
    config_path = hf_hub_download(filename="config.json", **common)
    model_path = hf_hub_download(filename=MODEL_FILE, **common)
    voice_path = hf_hub_download(filename=f"voices/{voice_name}.pt", **common)
    model = KModel(repo_id=model_id, config=config_path, model=model_path).to("cpu").eval()
    pipeline = KPipeline(lang_code="z", repo_id=model_id, model=model, device="cpu")
    voice_tensor = torch.load(voice_path, map_location="cpu", weights_only=True)
    speed = float(config.get("speed", 1.0))

    def synthesize(text: str, output: Path) -> dict[str, Any]:
        chunks = []
        for result in pipeline(text, voice=voice_tensor, speed=speed):
            audio = result.audio if hasattr(result, "audio") else result[2]
            chunks.append(np.asarray(audio, dtype=np.float32))
        if not chunks:
            raise SpeechError("Kokoro 没有返回音频。")
        waveform = np.concatenate(chunks)
        sf.write(output, waveform, 24000, subtype="PCM_16")
        return {"sample_rate": 24000, "duration_seconds": round(len(waveform) / 24000, 3)}

    return synthesize


def wave_metadata(path: Path) -> dict[str, Any]:
    try:
        with wave.open(str(path), "rb") as audio:
            duration = audio.getnframes() / audio.getframerate()
            return {"sample_rate": audio.getframerate(), "duration_seconds": round(duration, 3)}
    except (OSError, wave.Error) as exc:
        raise SpeechError(f"生成的 WAV 无效：{path.name}") from exc


def synthesize_request(
    request_path: Path,
    output_dir: Path,
    backend_factory: Callable[[dict[str, Any]], Callable[[str, Path], dict[str, Any]]] = make_kokoro_backend,
) -> dict[str, Any]:
    request = read_request(request_path)
    config = request["voice"]
    output_dir.mkdir(parents=True, exist_ok=True)
    backend = backend_factory(config)
    outputs = []
    for item in request["items"]:
        output = output_dir / item["output"]
        segment_timeline: list[dict[str, Any]] = []
        if item.get("segments"):
            parts: list[tuple[dict[str, Any], Path]] = []
            try:
                for segment_index, segment in enumerate(item["segments"], start=1):
                    part = output_dir / f".{output.stem}.segment-{segment_index:02}.wav"
                    backend(segment["text"], part)
                    parts.append((segment, part))
                segment_timeline = combine_segment_wavs(parts, output)
            finally:
                for _, part in parts:
                    part.unlink(missing_ok=True)
        else:
            backend(item["text"], output)
        if not output.is_file():
            raise SpeechError(f"TTS 未生成 {output.name}。")
        media = wave_metadata(output)
        outputs.append({
            "scene_id": item["id"],
            "file": output.name,
            "text_sha256": hashlib.sha256(item["text"].encode("utf-8")).hexdigest(),
            "sha256": sha256_file(output),
            **media,
            **({"segments": segment_timeline} if segment_timeline else {}),
        })
    try:
        engine_version = importlib.metadata.version("kokoro")
    except importlib.metadata.PackageNotFoundError:
        engine_version = "unavailable-test-backend"
    manifest = {
        "schema_version": 1,
        "status": "generated-not-published",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "engine": "kokoro",
        "engine_version": engine_version,
        "model_id": config["model_id"],
        "model_revision": config["model_revision"],
        "voice_name": config["voice_name"],
        "language": config["language"],
        "speed": float(config.get("speed", 1.0)),
        "license": config["license"],
        "source": "https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh",
        "outputs": outputs,
    }
    (output_dir / "tts-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    manifest = synthesize_request(args.request.resolve(), args.out.resolve())
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SpeechError as exc:
        print(f"错误：{exc}")
        raise SystemExit(1)
