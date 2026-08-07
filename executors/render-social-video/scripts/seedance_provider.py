#!/usr/bin/env python3
"""Create, resume, download, validate, and delete Seedance Ark B-roll tasks."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Mapping
import urllib.error
import urllib.parse
import urllib.request

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaError


ROOT = Path(__file__).resolve().parents[3]
PROVIDER = "seedance-ark"
STATE_FILE = "task-state.json"
AMBIGUOUS_FILE = "ambiguous-create.json"
MANIFEST_FILE = "seedance-manifest.json"
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled"}
URL_ENV_PATTERN = re.compile(r"SEEDANCE_INPUT_[A-Z0-9_]{1,64}")
SCENE_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,31}")
MAX_DOWNLOAD_BYTES = 500 * 1024 * 1024
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"


class SeedanceError(RuntimeError):
    pass


class AmbiguousCreateError(SeedanceError):
    pass


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SeedanceError(f"{label} 不存在或不是有效 JSON。") from exc
    if not isinstance(value, dict):
        raise SeedanceError(f"{label} 必须是 JSON 对象。")
    return value


def validate_public_schema(value: dict[str, Any], filename: str, label: str) -> None:
    try:
        schema = json.loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(value)
    except (OSError, json.JSONDecodeError, JsonSchemaError) as exc:
        raise SeedanceError(f"{label} 不符合公开 Schema：{exc}") from exc


def load_env_file(path: Path) -> dict[str, str]:
    allowed = {"ARK_API_KEY", "ARK_BASE_URL", "SEEDANCE_MODEL_ENDPOINT"}
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in allowed:
            result[key] = value.strip().strip('"').strip("'")
    return result


def normalize_base_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise SeedanceError("ARK_BASE_URL 必须是无凭据的 HTTPS 地址。")
    if parsed.query or parsed.fragment:
        raise SeedanceError("ARK_BASE_URL 不得包含查询参数或片段。")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def settings(root: Path = ROOT, environ: Mapping[str, str] | None = None) -> dict[str, str]:
    values: dict[str, str] = {}
    for filename in (".env", ".env.local"):
        values.update(load_env_file(root / filename))
    source = os.environ if environ is None else environ
    for key in ("ARK_API_KEY", "ARK_BASE_URL", "SEEDANCE_MODEL_ENDPOINT"):
        if source.get(key):
            values[key] = str(source[key])
    values.setdefault("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    if values.get("ARK_BASE_URL"):
        values["ARK_BASE_URL"] = normalize_base_url(values["ARK_BASE_URL"])
    return values


def configuration_report(values: Mapping[str, str]) -> dict[str, Any]:
    missing = [key for key in ("ARK_API_KEY", "SEEDANCE_MODEL_ENDPOINT") if not values.get(key)]
    parsed = urllib.parse.urlsplit(values.get("ARK_BASE_URL", ""))
    return {
        "provider": PROVIDER,
        "status": "configured-not-verified" if not missing else "optional-missing-configuration",
        "missing": missing,
        "base_origin": f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else "invalid",
        "model_endpoint": "present" if values.get("SEEDANCE_MODEL_ENDPOINT") else "missing",
        "api_key": "present" if values.get("ARK_API_KEY") else "missing",
        "paid_generation_requires_confirmation": True,
    }


def safe_https_url(value: str, *, allow_query: bool) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise SeedanceError("Seedance 参考素材必须使用无内嵌凭据的 HTTPS URL。")
    if parsed.fragment or (parsed.query and not allow_query):
        raise SeedanceError("带查询参数的临时素材 URL 必须通过 url_env 提供，不能写入请求文件。")
    host = parsed.hostname.lower()
    if host == "localhost" or host.endswith(".local"):
        raise SeedanceError("Seedance 参考素材 URL 不得指向本机地址。")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address and (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved):
        raise SeedanceError("Seedance 参考素材 URL 不得指向私有或保留 IP。")
    return value


def resolve_content(
    raw_content: Any, environ: Mapping[str, str] | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(raw_content, list) or not 1 <= len(raw_content) <= 12:
        raise SeedanceError("content 必须包含 1 到 12 项。")
    source = os.environ if environ is None else environ
    resolved: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    text_count = 0
    remote_count = 0
    for index, item in enumerate(raw_content):
        if not isinstance(item, dict):
            raise SeedanceError(f"content[{index}] 必须是对象。")
        kind = item.get("type")
        if kind == "text":
            if set(item) != {"type", "text"}:
                raise SeedanceError(f"content[{index}] text 项含有未知字段。")
            text = str(item.get("text") or "").strip()
            if not text or len(text) > 2000:
                raise SeedanceError(f"content[{index}].text 必须为 1 到 2000 个字符。")
            text_count += 1
            resolved.append({"type": "text", "text": text})
            summary.append({"type": "text", "length": len(text), "sha256": sha256_bytes(text.encode("utf-8"))})
            continue
        field_by_type = {
            "image_url": "image_url",
            "audio_url": "audio_url",
            "video_url": "video_url",
        }
        field = field_by_type.get(str(kind))
        if not field:
            raise SeedanceError(f"content[{index}].type 不受支持。")
        allowed = {"type", "url", "url_env", "role"}
        if set(item) - allowed:
            raise SeedanceError(f"content[{index}] 含有未知字段。")
        direct = str(item.get("url") or "").strip()
        env_name = str(item.get("url_env") or "").strip()
        if bool(direct) == bool(env_name):
            raise SeedanceError(f"content[{index}] 必须且只能提供 url 或 url_env。")
        if env_name:
            if not URL_ENV_PATTERN.fullmatch(env_name):
                raise SeedanceError(f"content[{index}].url_env 必须以 SEEDANCE_INPUT_ 开头。")
            actual_url = str(source.get(env_name) or "").strip()
            if not actual_url:
                raise SeedanceError(f"环境变量 {env_name} 未配置。")
            actual_url = safe_https_url(actual_url, allow_query=True)
            source_mode = "environment"
        else:
            actual_url = safe_https_url(direct, allow_query=False)
            source_mode = "public-url"
        role = str(item.get("role") or "").strip()
        if len(role) > 40:
            raise SeedanceError(f"content[{index}].role 过长。")
        provider_item: dict[str, Any] = {"type": kind, field: {"url": actual_url}}
        if role:
            provider_item["role"] = role
        resolved.append(provider_item)
        summary.append({
            "type": kind,
            "role": role,
            "source": source_mode,
            "url_sha256": sha256_bytes(actual_url.encode("utf-8")),
        })
        remote_count += 1
    if text_count != 1:
        raise SeedanceError("content 必须且只能包含一个 text prompt。")
    return resolved, summary


def validate_options(raw: Any) -> dict[str, Any]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise SeedanceError("options 必须是对象。")
    allowed = {
        "return_last_frame", "service_tier", "execution_expires_after", "priority",
        "generate_audio", "draft", "camera_fixed", "watermark", "seed",
        "resolution", "ratio", "duration", "frames",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise SeedanceError("options 含有未知字段：" + ", ".join(sorted(unknown)))
    options = {
        "return_last_frame": bool(raw.get("return_last_frame", True)),
        "service_tier": str(raw.get("service_tier") or "default"),
        "execution_expires_after": int(raw.get("execution_expires_after", 3600)),
        "priority": int(raw.get("priority", 0)),
        "generate_audio": bool(raw.get("generate_audio", False)),
        "draft": bool(raw.get("draft", False)),
        "camera_fixed": bool(raw.get("camera_fixed", False)),
        "watermark": bool(raw.get("watermark", False)),
    }
    for key in ("seed", "frames"):
        if raw.get(key) is not None:
            options[key] = int(raw[key])
    for key in ("resolution", "ratio"):
        if raw.get(key) is not None:
            options[key] = str(raw[key])
    if raw.get("duration") is not None:
        options["duration"] = int(raw["duration"])
    if not 300 <= options["execution_expires_after"] <= 86400:
        raise SeedanceError("execution_expires_after 必须在 300 到 86400 秒之间。")
    if not -10 <= options["priority"] <= 10:
        raise SeedanceError("priority 必须在 -10 到 10 之间。")
    if options.get("duration") is not None and not 2 <= options["duration"] <= 15:
        raise SeedanceError("duration 必须在 2 到 15 秒之间。")
    if options.get("ratio") and options["ratio"] not in {"9:16", "16:9", "1:1", "3:4", "4:3", "21:9"}:
        raise SeedanceError("ratio 不在允许范围内。")
    if options.get("resolution") and not re.fullmatch(r"(?:[0-9]{3,4}p|2k)", options["resolution"], re.I):
        raise SeedanceError("resolution 格式无效。")
    if options["generate_audio"]:
        raise SeedanceError("Growth Lab Seedance B-roll 必须设置 generate_audio=false；配音由本地层负责。")
    return options


def read_generation_request(
    path: Path, environ: Mapping[str, str] | None = None
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    request = read_json(path, "Seedance request")
    validate_public_schema(request, "seedance-request.schema.json", "Seedance request")
    if request.get("schema_version") != 1 or request.get("provider") != PROVIDER:
        raise SeedanceError("Seedance request schema_version/provider 无效。")
    if request.get("purpose") != "b-roll":
        raise SeedanceError("Seedance provider 当前只接受 purpose=b-roll。")
    allowed = {
        "schema_version", "provider", "purpose", "scene_id", "content", "options",
        "input_rights_confirmed", "remote_asset_upload_authorized",
    }
    if set(request) - allowed:
        raise SeedanceError("Seedance request 含有未知字段。")
    scene_id = str(request.get("scene_id") or "")
    if not SCENE_ID_PATTERN.fullmatch(scene_id):
        raise SeedanceError("scene_id 无效。")
    if request.get("input_rights_confirmed") is not True:
        raise SeedanceError("必须明确记录 input_rights_confirmed=true。")
    content, summary = resolve_content(request.get("content"), environ)
    if any(item["type"] != "text" for item in summary) and request.get("remote_asset_upload_authorized") is not True:
        raise SeedanceError("使用远程参考素材前必须记录 remote_asset_upload_authorized=true。")
    normalized = {
        "schema_version": 1,
        "provider": PROVIDER,
        "purpose": "b-roll",
        "scene_id": scene_id,
        "content": content,
        "options": validate_options(request.get("options")),
    }
    return normalized, summary


def request_sha256(path: Path) -> str:
    return sha256_file(path)


def redact_message(value: str, secret: str = "") -> str:
    result = value
    if secret:
        result = result.replace(secret, "[REDACTED]")
    result = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", result, flags=re.I)
    result = re.sub(r"https?://[^\s\"']+", "[redacted-url]", result)
    return result[:1000]


class ArkContentClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 60.0):
        self.base_url = normalize_base_url(base_url)
        self.api_key = api_key
        self.timeout = timeout

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None, *, ambiguous: bool = False
    ) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "growth-lab-seedance/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read(2048).decode("utf-8", errors="replace")
            raise SeedanceError(f"Ark HTTP {exc.code}: {redact_message(detail, self.api_key)}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            message = redact_message(str(exc), self.api_key)
            if ambiguous:
                raise AmbiguousCreateError("创建请求传输状态不明；禁止自动重试：" + message) from exc
            raise SeedanceError("Ark 请求失败：" + message) from exc
        try:
            value = json.loads(raw.decode("utf-8")) if raw else {}
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SeedanceError("Ark 返回了无效 JSON。") from exc
        if not isinstance(value, dict):
            raise SeedanceError("Ark 返回值必须是 JSON 对象。")
        return value

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/contents/generations/tasks", payload, ambiguous=True)

    def get(self, task_id: str) -> dict[str, Any]:
        return self._request("GET", f"/contents/generations/tasks/{urllib.parse.quote(task_id, safe='')}")

    def delete(self, task_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/contents/generations/tasks/{urllib.parse.quote(task_id, safe='')}")


def provider_payload(request: dict[str, Any], model_endpoint: str) -> dict[str, Any]:
    return {"model": model_endpoint, "content": request["content"], **request["options"]}


def sanitized_summary(
    request: dict[str, Any], content_summary: list[dict[str, Any]], model_endpoint: str, source_sha: str
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "provider": PROVIDER,
        "purpose": request["purpose"],
        "scene_id": request["scene_id"],
        "model_endpoint": model_endpoint,
        "request_sha256": source_sha,
        "content": content_summary,
        "options": request["options"],
        "paid_generation_requires_confirmation": True,
    }


def wait_for_task(
    client: ArkContentClient,
    state_path: Path,
    state: dict[str, Any],
    wait_timeout: float,
    poll_interval: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + wait_timeout
    transient_failures = 0
    while True:
        try:
            task = client.get(state["task_id"])
            transient_failures = 0
        except SeedanceError:
            transient_failures += 1
            if transient_failures >= 3 or time.monotonic() >= deadline:
                raise
            time.sleep(poll_interval)
            continue
        status = str(task.get("status") or "unknown")
        state.update({"status": status, "last_checked_at": now_iso()})
        write_json(state_path, state)
        print(json.dumps({"task_id": state["task_id"], "status": status}, ensure_ascii=False), flush=True)
        if status in TERMINAL_STATUSES:
            return task
        if time.monotonic() >= deadline:
            raise SeedanceError("等待 Seedance 任务超时；状态已保存，可使用 resume 继续。")
        time.sleep(poll_interval)


def download_https(url: str, destination: Path) -> None:
    safe_https_url(url, allow_query=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": "growth-lab-seedance/1"})
    total = 0
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
            safe_https_url(response.geturl(), allow_query=True)
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise SeedanceError("Seedance 下载文件超过 500 MiB 限制。")
                output.write(chunk)
        if total == 0:
            raise SeedanceError("Seedance 返回了空视频。")
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def ffmpeg_executable() -> str:
    configured = os.environ.get("VIDEO_FFMPEG_PATH", "").strip()
    if configured:
        path = Path(os.path.expandvars(os.path.expanduser(configured)))
        if path.is_file():
            return str(path)
        raise SeedanceError("VIDEO_FFMPEG_PATH 指向的文件不存在。")
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise SeedanceError("未找到 FFmpeg；请使用视频专用 venv。") from exc


def validate_video(path: Path) -> dict[str, Any]:
    ffmpeg = ffmpeg_executable()
    decode = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(path), "-map", "0:v:0", "-f", "null", os.devnull],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if decode.returncode != 0:
        raise SeedanceError("Seedance 视频完整解码失败：" + decode.stderr[-600:])
    probe = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True, timeout=30
    )
    text = probe.stderr
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):([0-9.]+)", text)
    size_match = re.search(r"Video:[^\n]*?\b(\d{2,5})x(\d{2,5})\b", text)
    fps_match = re.search(r"Video:[^\n]*?\b([0-9.]+) fps\b", text)
    if not duration_match or not size_match:
        raise SeedanceError("无法读取 Seedance 视频时长或分辨率。")
    hours, minutes, seconds = duration_match.groups()
    duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    if not 1 <= duration <= 30:
        raise SeedanceError("Seedance B-roll 时长不在 1 到 30 秒范围内。")
    return {
        "duration_seconds": round(duration, 3),
        "width": int(size_match.group(1)),
        "height": int(size_match.group(2)),
        "fps": float(fps_match.group(1)) if fps_match else None,
        "has_audio": "Audio:" in text,
    }


def finalize_success(
    task: dict[str, Any],
    output_dir: Path,
    state: dict[str, Any],
    request_summary: dict[str, Any],
    downloader: Callable[[str, Path], None] = download_https,
    validator: Callable[[Path], dict[str, Any]] = validate_video,
) -> dict[str, Any]:
    content = task.get("content")
    if not isinstance(content, dict) or not isinstance(content.get("video_url"), str):
        raise SeedanceError("成功任务缺少 content.video_url。")
    video = output_dir / "raw" / "seedance.mp4"
    if not video.is_file():
        downloader(content["video_url"], video)
    media = validator(video)
    manifest = {
        "schema_version": 1,
        "status": "succeeded-downloaded-validated",
        "provider": PROVIDER,
        "model_endpoint": state["model_endpoint"],
        "task_id": state["task_id"],
        "request_sha256": state["request_sha256"],
        "request": request_summary,
        "provider_result": {
            "revised_prompt": str(task.get("revised_prompt") or ""),
            "usage": task.get("usage") if isinstance(task.get("usage"), dict) else {},
            "seed": task.get("seed"),
            "duration": task.get("duration"),
            "ratio": task.get("ratio"),
            "resolution": task.get("resolution"),
            "frames": task.get("frames"),
            "frames_per_second": task.get("framespersecond"),
            "generate_audio": bool(task.get("generate_audio", False)),
            "service_tier": task.get("service_tier"),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at"),
        },
        "output": {
            "file": "raw/seedance.mp4",
            "sha256": sha256_file(video),
            **media,
        },
        "remote_urls_persisted": False,
        "publication_authorized": False,
        "finished_at": now_iso(),
    }
    validate_public_schema(manifest, "seedance-manifest.schema.json", "Seedance manifest")
    write_json(output_dir / MANIFEST_FILE, manifest)
    state.update({"status": "succeeded-downloaded-validated", "finished_at": now_iso()})
    write_json(output_dir / STATE_FILE, state)
    return manifest


def run_generation(
    request_path: Path,
    output_dir: Path,
    *,
    confirm_paid_generation: bool,
    wait_timeout: float,
    poll_interval: float,
    environ: Mapping[str, str] | None = None,
    configured: dict[str, str] | None = None,
    client: ArkContentClient | None = None,
    downloader: Callable[[str, Path], None] = download_https,
    validator: Callable[[Path], dict[str, Any]] = validate_video,
    allow_create: bool = True,
) -> dict[str, Any]:
    request_path = request_path.resolve()
    output_dir = output_dir.resolve()
    request, content_summary = read_generation_request(request_path, environ)
    values = settings(environ=environ) if configured is None else configured
    report = configuration_report(values)
    if report["missing"]:
        raise SeedanceError("Seedance 配置缺失：" + ", ".join(report["missing"]))
    model_endpoint = values["SEEDANCE_MODEL_ENDPOINT"]
    source_sha = request_sha256(request_path)
    summary = sanitized_summary(request, content_summary, model_endpoint, source_sha)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "request-summary.json", summary)
    existing_manifest = output_dir / MANIFEST_FILE
    if existing_manifest.is_file():
        manifest = read_json(existing_manifest, "Seedance manifest")
        if manifest.get("request_sha256") != source_sha:
            raise SeedanceError("输出目录已有不同请求的 Seedance manifest。")
        return manifest
    if (output_dir / AMBIGUOUS_FILE).exists():
        raise SeedanceError("此前创建请求状态不明；请先在 Ark 控制台核对，禁止自动重复创建。")
    service = client or ArkContentClient(values["ARK_BASE_URL"], values["ARK_API_KEY"])
    state_path = output_dir / STATE_FILE
    if state_path.is_file():
        state = read_json(state_path, "Seedance task state")
        if state.get("request_sha256") != source_sha or state.get("model_endpoint") != model_endpoint:
            raise SeedanceError("输出目录中的任务状态与当前请求不匹配。")
    else:
        if not allow_create:
            raise SeedanceError("resume 未找到 task-state.json；不会创建新的付费任务。")
        if not confirm_paid_generation:
            raise SeedanceError("创建 Seedance 付费任务前必须传入 --confirm-paid-generation。")
        try:
            created = service.create(provider_payload(request, model_endpoint))
            task_id = str(created.get("id") or "")
            if not task_id:
                raise AmbiguousCreateError("Ark 创建响应缺少任务 ID；禁止自动重试。")
        except AmbiguousCreateError as exc:
            write_json(output_dir / AMBIGUOUS_FILE, {
                "schema_version": 1,
                "provider": PROVIDER,
                "request_sha256": source_sha,
                "model_endpoint": model_endpoint,
                "recorded_at": now_iso(),
                "reason": redact_message(str(exc), values.get("ARK_API_KEY", "")),
            })
            raise
        state = {
            "schema_version": 1,
            "provider": PROVIDER,
            "task_id": task_id,
            "model_endpoint": model_endpoint,
            "request_sha256": source_sha,
            "status": "created",
            "created_at": now_iso(),
            "remote_delete_confirmed": False,
        }
        write_json(state_path, state)
    task = wait_for_task(service, state_path, state, wait_timeout, poll_interval)
    status = str(task.get("status") or "unknown")
    if status != "succeeded":
        error = task.get("error") if isinstance(task.get("error"), dict) else {}
        write_json(output_dir / "failure.json", {
            "schema_version": 1,
            "provider": PROVIDER,
            "task_id": state["task_id"],
            "status": status,
            "code": str(error.get("code") or ""),
            "message": redact_message(str(error.get("message") or ""), values.get("ARK_API_KEY", "")),
        })
        raise SeedanceError(f"Seedance 任务结束但未成功：{status}")
    return finalize_success(task, output_dir, state, summary, downloader, validator)


def delete_remote_task(
    output_dir: Path,
    *,
    confirm_delete: bool,
    configured: dict[str, str] | None = None,
    client: ArkContentClient | None = None,
) -> dict[str, Any]:
    if not confirm_delete:
        raise SeedanceError("删除远程任务必须传入 --confirm-delete。")
    state_path = output_dir.resolve() / STATE_FILE
    state = read_json(state_path, "Seedance task state")
    values = settings() if configured is None else configured
    report = configuration_report(values)
    if report["missing"]:
        raise SeedanceError("Seedance 配置缺失：" + ", ".join(report["missing"]))
    service = client or ArkContentClient(values["ARK_BASE_URL"], values["ARK_API_KEY"])
    service.delete(str(state["task_id"]))
    state.update({"remote_delete_confirmed": True, "remote_deleted_at": now_iso()})
    write_json(state_path, state)
    return {"task_id": state["task_id"], "remote_deleted": True, "local_files_deleted": False}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check")
    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("--request", required=True, type=Path)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--request", required=True, type=Path)
    run_parser.add_argument("--out", required=True, type=Path)
    run_parser.add_argument("--confirm-paid-generation", action="store_true")
    run_parser.add_argument("--wait-timeout", type=float, default=900)
    run_parser.add_argument("--poll-interval", type=float, default=5)
    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--request", required=True, type=Path)
    resume_parser.add_argument("--out", required=True, type=Path)
    resume_parser.add_argument("--wait-timeout", type=float, default=900)
    resume_parser.add_argument("--poll-interval", type=float, default=5)
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("--out", required=True, type=Path)
    delete_parser.add_argument("--confirm-delete", action="store_true")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "check":
        report = configuration_report(settings())
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if not report["missing"] else 1
    if args.command == "inspect":
        request, summary = read_generation_request(args.request.resolve())
        values = settings()
        model = values.get("SEEDANCE_MODEL_ENDPOINT", "missing")
        print(json.dumps(sanitized_summary(request, summary, model, request_sha256(args.request.resolve())), ensure_ascii=False, indent=2))
        return 0
    if args.command in {"run", "resume"}:
        if not 30 <= args.wait_timeout <= 3600 or not 2 <= args.poll_interval <= 60:
            raise SeedanceError("wait-timeout 必须为 30–3600 秒，poll-interval 必须为 2–60 秒。")
        manifest = run_generation(
            args.request,
            args.out,
            confirm_paid_generation=args.command == "run" and args.confirm_paid_generation,
            wait_timeout=args.wait_timeout,
            poll_interval=args.poll_interval,
            allow_create=args.command == "run",
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    result = delete_remote_task(args.out, confirm_delete=args.confirm_delete)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SeedanceError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
