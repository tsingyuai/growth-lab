#!/usr/bin/env python3
"""微信公众号发布 CLI。

命令:
  preview 生成人工审阅用 preview.html
  render  生成 article.html、preview.html
  draft   上传素材并创建草稿
  publish 显式确认后发布草稿
  status  查询发布状态
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

from client import WechatAPIError, WechatClient, WechatConfigError, load_config, load_dotenv
from payload_builder import (
    PLACEHOLDER_MARK,
    apply_defaults,
    build_draft_payload,
    build_preview_html,
    dump_json,
    load_simple_yaml,
    markdown_to_html,
    replace_local_images,
    resolve_theme,
)


def now_iso() -> str:
    """当前时间字符串。"""
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def load_state(post_dir: Path) -> dict[str, object]:
    """读取发布状态。"""
    path = post_dir / "publish-state.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(post_dir: Path, updates: dict[str, object]) -> None:
    """合并写入发布状态。"""
    state = load_state(post_dir)
    state.update(updates)
    state["updated_at"] = now_iso()
    dump_json(post_dir / "publish-state.json", state)


def require_post_files(post_dir: Path) -> tuple[Path, Path]:
    """检查必需文件。"""
    article = post_dir / "article.md"
    config = post_dir / "wechat.yml"
    missing = [str(p) for p in (article, config) if not p.exists()]
    if missing:
        raise FileNotFoundError(f"缺少文件: {', '.join(missing)}")
    return article, config


def render_post_files(post_dir: Path) -> tuple[Path, Path, dict[str, object], str]:
    """渲染文章正文和人工审阅预览。"""
    article_path, config_path = require_post_files(post_dir)
    load_dotenv()
    config = apply_defaults(load_simple_yaml(config_path))
    html = markdown_to_html(article_path.read_text(encoding="utf-8"), resolve_theme(config))
    article_html_path = post_dir / "article.html"
    preview_html_path = post_dir / "preview.html"
    article_html_path.write_text(html, encoding="utf-8")
    preview_html_path.write_text(build_preview_html(config, html), encoding="utf-8")
    return article_html_path, preview_html_path, config, html


def open_preview(path: Path) -> None:
    """用系统默认浏览器打开预览页。"""
    if sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", str(path)], check=False)
    elif sys.platform.startswith("win"):
        subprocess.run(["cmd", "/c", "start", str(path)], check=False)


def command_preview(args: argparse.Namespace) -> int:
    """生成人工审阅用 preview.html。"""
    post_dir = Path(args.post_dir)
    _, preview_html_path, _, _ = render_post_files(post_dir)
    print(f"✓ rendered {preview_html_path}")
    if args.open:
        open_preview(preview_html_path)
        print(f"✓ opened {preview_html_path}")
    return 0


def command_render(args: argparse.Namespace) -> int:
    """渲染 article.md 到 article.html 和 preview.html。"""
    post_dir = Path(args.post_dir)
    article_html_path, preview_html_path, config, html = render_post_files(post_dir)
    print(f"✓ rendered {article_html_path}")
    print(f"✓ rendered {preview_html_path}")
    if args.payload:
        cover = Path(str(config.get("cover", "cover.png")))
        payload = build_draft_payload(config, html, thumb_media_id=f"DRY_RUN:{cover}")
        dump_json(post_dir / "payload.json", payload)
        print(f"✓ wrote dry-run payload {post_dir / 'payload.json'}")
    return 0


def command_draft(args: argparse.Namespace) -> int:
    """上传素材并创建草稿。"""
    post_dir = Path(args.post_dir)
    article_path, config_path = require_post_files(post_dir)
    client = WechatClient(load_config())
    config = apply_defaults(load_simple_yaml(config_path))
    html_path = post_dir / "article.html"
    if not html_path.exists():
        html_path.write_text(
            markdown_to_html(article_path.read_text(encoding="utf-8"), resolve_theme(config)),
            encoding="utf-8",
        )

    # 先完成全部本地校验,再上传任何素材,避免被拒绝的文章在后台留下永久素材。
    html_text = html_path.read_text(encoding="utf-8")
    if PLACEHOLDER_MARK in html_text:
        raise ValueError("正文仍有 ::: figure 配图位,请换成真实图片后重新 render 再创建草稿。")
    unsupported_external_images = find_unsupported_external_image_sources(html_text)
    if unsupported_external_images:
        joined = ", ".join(unsupported_external_images)
        raise ValueError(f"正文图片不能使用外链,请改为本地 assets 图片: {joined}")
    local_images = {src: resolve_local_image_path(post_dir, src) for src in find_local_image_sources(html_text)}
    cover_path = post_dir / str(config.get("cover", "cover.png"))
    if not cover_path.exists():
        raise FileNotFoundError(f"封面不存在: {cover_path}")

    thumb_media_id = client.upload_cover_material(cover_path)
    image_mapping: dict[str, str] = {}
    for src, image_path in local_images.items():
        image_mapping[src] = client.upload_image_for_content(image_path)
    if image_mapping:
        html_text = replace_local_images(html_text, image_mapping)
        html_path.write_text(html_text, encoding="utf-8")

    payload = build_draft_payload(config, html_text, thumb_media_id=thumb_media_id)
    dump_json(post_dir / "payload.json", payload)
    result = client.add_draft(payload)
    media_id = str(result.get("media_id", ""))
    save_state(
        post_dir,
        {
            "status": "draft_created",
            "draft_media_id": media_id,
            "account": config.get("account", ""),
            "image_mapping": image_mapping,
        },
    )
    print(f"✓ draft created media_id={media_id}")
    return 0


def command_publish(args: argparse.Namespace) -> int:
    """提交发布。"""
    post_dir = Path(args.post_dir)
    _, config_path = require_post_files(post_dir)
    config = load_simple_yaml(config_path)
    publish_config = config.get("publish")
    if not isinstance(publish_config, dict):
        publish_config = {}

    client_config = load_config()
    if not client_config.enable_auto_publish:
        raise PermissionError("WECHAT_ENABLE_AUTO_PUBLISH 未开启,拒绝发布。")
    if publish_config.get("approved") is not True:
        raise PermissionError("wechat.yml publish.approved 不是 true,拒绝发布。")
    if not args.confirm_publish:
        raise PermissionError("缺少 --confirm-publish,拒绝发布。")

    state = load_state(post_dir)
    media_id = str(state.get("draft_media_id", ""))
    if not media_id:
        raise ValueError("publish-state.json 缺少 draft_media_id,请先创建草稿。")

    client = WechatClient(client_config)
    result = client.publish(media_id)
    publish_id = str(result.get("publish_id", ""))
    save_state(post_dir, {"status": "publish_submitted", "publish_id": publish_id})
    print(f"✓ publish submitted publish_id={publish_id}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    """查询发布状态。"""
    post_dir = Path(args.post_dir)
    state = load_state(post_dir)
    publish_id = str(state.get("publish_id", ""))
    if not publish_id:
        raise ValueError("publish-state.json 缺少 publish_id。")
    client = WechatClient(load_config())
    result = client.publish_status(publish_id)
    updates: dict[str, object] = {"publish_status_response": result}
    if "article_id" in result:
        updates["article_id"] = result["article_id"]
    if "article_url" in result:
        updates["article_url"] = result["article_url"]
    save_state(post_dir, updates)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def find_local_image_sources(html_text: str) -> list[str]:
    """提取本地图片 src。"""
    out: list[str] = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html_text):
        if not re.match(r"^https?://", src) and not src.startswith("//"):
            out.append(src)
    return out


def find_unsupported_external_image_sources(html_text: str) -> list[str]:
    """提取无法保证在微信正文里稳定加载的外链图片。"""
    out: list[str] = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html_text):
        parsed = urlparse(src)
        if parsed.scheme in {"http", "https"} and parsed.netloc != "mmbiz.qpic.cn":
            out.append(src)
    return out


def resolve_local_image_path(post_dir: Path, src: str) -> Path:
    """把正文图片 src 解析为文章目录内的本地文件。"""
    parsed = urlparse(src)
    rel = Path(unquote(parsed.path))
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"非法正文图片路径: {src}")

    root = post_dir.resolve()
    image_path = (root / rel).resolve()
    if root != image_path and root not in image_path.parents:
        raise ValueError(f"正文图片路径越界: {src}")
    if not image_path.exists():
        raise FileNotFoundError(f"正文图片不存在: {src}")
    if not image_path.is_file():
        raise FileNotFoundError(f"正文图片不是文件: {src}")
    return image_path


def build_parser() -> argparse.ArgumentParser:
    """构建参数解析器。"""
    parser = argparse.ArgumentParser(description="微信公众号发布 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    preview = sub.add_parser("preview", help="生成人工审阅用 preview.html")
    preview.add_argument("post_dir")
    preview.add_argument("--open", action="store_true", help="生成后用系统默认浏览器打开")
    preview.set_defaults(func=command_preview)

    render = sub.add_parser("render", help="渲染 article.md 到 article.html 和 preview.html")
    render.add_argument("post_dir")
    render.add_argument("--payload", action="store_true", help="同时生成 dry-run payload")
    render.set_defaults(func=command_render)

    draft = sub.add_parser("draft", help="创建微信草稿")
    draft.add_argument("post_dir")
    draft.set_defaults(func=command_draft)

    publish = sub.add_parser("publish", help="发布微信草稿")
    publish.add_argument("post_dir")
    publish.add_argument("--confirm-publish", action="store_true")
    publish.set_defaults(func=command_publish)

    status = sub.add_parser("status", help="查询发布状态")
    status.add_argument("post_dir")
    status.set_defaults(func=command_status)
    return parser


def main() -> int:
    """命令行入口。"""
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except (FileNotFoundError, PermissionError, ValueError, WechatConfigError, WechatAPIError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
