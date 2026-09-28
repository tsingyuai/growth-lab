#!/usr/bin/env python3
"""微信公众号 API 客户端。

只使用标准库,不引入包管理。密钥来自进程环境或 Growth Lab 根目录
`.env.local` / `.env`;token 缓存在仓库外路径,不会写入仓库或 Memory。
"""

from __future__ import annotations

import json
import mimetypes
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


API_BASE = "https://api.weixin.qq.com"
REPO = Path(__file__).resolve().parents[3]


class WechatConfigError(RuntimeError):
    """微信配置缺失或不合法。"""


class WechatAPIError(RuntimeError):
    """微信接口返回错误。"""


@dataclass
class WechatConfig:
    app_id: str
    app_secret: str
    account_label: str
    default_author: str
    default_source_url: str
    enable_auto_publish: bool
    token_cache_path: Path


def load_dotenv() -> None:
    """轻量加载根 `.env.local` / `.env`,不覆盖已有环境变量。"""
    for env_path in (REPO / ".env.local", REPO / ".env"):
        if env_path.exists():
            _load_env_file(env_path)


def _load_env_file(env_path: Path) -> None:
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config() -> WechatConfig:
    """读取微信配置。"""
    load_dotenv()
    app_id = os.environ.get("WECHAT_MP_APP_ID", "").strip()
    app_secret = os.environ.get("WECHAT_MP_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        raise WechatConfigError("缺少 WECHAT_MP_APP_ID / WECHAT_MP_APP_SECRET,请先通过 onboard-growth-lab 配置。")

    cache = os.environ.get("WECHAT_TOKEN_CACHE_PATH", "~/.growth-lab/wechat/access-token.json")
    return WechatConfig(
        app_id=app_id,
        app_secret=app_secret,
        account_label=os.environ.get("WECHAT_MP_ACCOUNT_LABEL", "wechat-mp"),
        default_author=os.environ.get("WECHAT_MP_DEFAULT_AUTHOR", ""),
        default_source_url=os.environ.get("WECHAT_MP_DEFAULT_SOURCE_URL", ""),
        enable_auto_publish=os.environ.get("WECHAT_ENABLE_AUTO_PUBLISH", "false").lower()
        in {"1", "true", "yes", "on"},
        token_cache_path=Path(cache).expanduser(),
    )


def _read_token_cache(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if int(data.get("expires_at", 0)) - 120 > int(time.time()):
        token = data.get("access_token")
        return str(token) if token else None
    return None


def _write_token_cache(path: Path, access_token: str, expires_in: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "access_token": access_token,
        "expires_at": int(time.time()) + max(0, expires_in),
        "updated_at": int(time.time()),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    path.chmod(0o600)


class WechatClient:
    """微信公众号接口封装。"""

    def __init__(self, config: WechatConfig) -> None:
        self.config = config

    def get_access_token(self, force_refresh: bool = False) -> str:
        """获取 access_token,默认读缓存。"""
        if not force_refresh:
            cached = _read_token_cache(self.config.token_cache_path)
            if cached:
                return cached

        params = urllib.parse.urlencode(
            {
                "grant_type": "client_credential",
                "appid": self.config.app_id,
                "secret": self.config.app_secret,
            }
        )
        data = self._request_json("GET", f"/cgi-bin/token?{params}", access_token=None)
        token = data.get("access_token")
        if not token:
            raise WechatAPIError(f"获取 access_token 失败: {data}")
        _write_token_cache(self.config.token_cache_path, str(token), int(data.get("expires_in", 7200)))
        return str(token)

    def post_json(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        """POST JSON 到微信接口。"""
        token = self.get_access_token()
        return self._request_json("POST", path, payload=payload, access_token=token)

    def upload_image_for_content(self, image_path: Path) -> str:
        """上传正文图片,返回微信图片 URL。"""
        token = self.get_access_token()
        data = self._post_multipart(
            "/cgi-bin/media/uploadimg", image_path=image_path, fields={}, access_token=token
        )
        url = data.get("url")
        if not url:
            raise WechatAPIError(f"正文图片上传失败: {data}")
        return str(url)

    def upload_cover_material(self, image_path: Path) -> str:
        """上传永久图片素材作为封面,返回 media_id。"""
        token = self.get_access_token()
        data = self._post_multipart(
            "/cgi-bin/material/add_material",
            image_path=image_path,
            fields={"type": "image"},
            access_token=token,
        )
        media_id = data.get("media_id")
        if not media_id:
            raise WechatAPIError(f"封面素材上传失败: {data}")
        return str(media_id)

    def add_draft(self, payload: dict[str, object]) -> dict[str, object]:
        """新增草稿。"""
        return self.post_json("/cgi-bin/draft/add", payload)

    def publish(self, media_id: str) -> dict[str, object]:
        """提交发布。"""
        return self.post_json("/cgi-bin/freepublish/submit", {"media_id": media_id})

    def publish_status(self, publish_id: str) -> dict[str, object]:
        """查询发布状态。"""
        return self.post_json("/cgi-bin/freepublish/get", {"publish_id": publish_id})

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
        access_token: str | None = None,
    ) -> dict[str, object]:
        url = f"{API_BASE}{path}"
        sep = "&" if "?" in url else "?"
        if access_token:
            url = f"{url}{sep}access_token={urllib.parse.quote(access_token)}"
        body = None
        headers = {"User-Agent": "growth-lab-wechat/1.0"}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise WechatAPIError(f"HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise WechatAPIError(f"请求微信接口失败: {exc}") from exc

        errcode = data.get("errcode")
        if errcode not in (None, 0):
            raise WechatAPIError(f"微信接口错误 errcode={errcode}: {data}")
        return data

    def _post_multipart(
        self,
        path: str,
        image_path: Path,
        fields: dict[str, str],
        access_token: str,
    ) -> dict[str, object]:
        boundary = f"----growthLab{int(time.time() * 1000)}"
        parts: list[bytes] = []
        for name, value in fields.items():
            parts.append(f"--{boundary}\r\n".encode("utf-8"))
            parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
            parts.append(f"{value}\r\n".encode("utf-8"))

        mime = mimetypes.guess_type(str(image_path))[0] or "application/octet-stream"
        filename = image_path.name
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(
            f'Content-Disposition: form-data; name="media"; filename="{filename}"\r\n'.encode(
                "utf-8"
            )
        )
        parts.append(f"Content-Type: {mime}\r\n\r\n".encode("utf-8"))
        parts.append(image_path.read_bytes())
        parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))
        body = b"".join(parts)

        url = f"{API_BASE}{path}?access_token={urllib.parse.quote(access_token)}"
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "growth-lab-wechat/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise WechatAPIError(f"HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise WechatAPIError(f"上传微信素材失败: {exc}") from exc

        errcode = data.get("errcode")
        if errcode not in (None, 0):
            raise WechatAPIError(f"微信素材接口错误 errcode={errcode}: {data}")
        return data
