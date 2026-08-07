#!/usr/bin/env python3
"""Create a self-contained product-video fixture for local acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont


def create(directory: Path, layout: str = "classic", card_source: bool = False) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    screenshot = Image.new("RGB", (1440, 980), "#F5F6FA")
    draw = ImageDraw.Draw(screenshot)
    font_path = r"C:\Windows\Fonts\NotoSansSC-VF.ttf"
    title = ImageFont.truetype(font_path, 46)
    body = ImageFont.truetype(font_path, 30)
    draw.rounded_rectangle((38, 38, 1402, 942), radius=28, fill="white", outline="#D8DCE8", width=3)
    draw.rectangle((38, 38, 1402, 112), fill="#11131A")
    draw.text((78, 53), "Growth Lab · 产品内容工作区", font=title, fill="white")
    draw.rounded_rectangle((80, 160, 430, 880), radius=24, fill="#F0EEFF")
    for index, label in enumerate(("产品事实", "平台研究", "内容草稿", "效果复盘"), start=1):
        y = 220 + (index - 1) * 135
        draw.rounded_rectangle((115, y, 395, y + 82), radius=18, fill="#FFFFFF")
        draw.text((145, y + 22), label, font=body, fill="#292D3A")
    draw.text((500, 185), "本轮增长任务", font=title, fill="#11131A")
    draw.rounded_rectangle((500, 270, 1330, 520), radius=26, fill="#F7F8FC", outline="#D8DCE8", width=2)
    draw.text((550, 320), "从产品信息生成小红书与 X 内容", font=body, fill="#11131A")
    draw.text((550, 385), "证据、素材和发布权限分别管理", font=body, fill="#626A7F")
    draw.rounded_rectangle((500, 600, 900, 690), radius=22, fill="#4F35E8")
    draw.text((615, 625), "生成内容包", font=body, fill="white")
    screenshot.save(directory / "product-ui.png")
    product_demo = layout == "product-demo"
    plan = {
        "schema_version": 1,
        "title": "Growth Lab",
        "canvas": {"width": 1440 if product_demo else 1080, "height": 1920, "fps": 24},
        "voice": {"provider": "windows-sapi", "voice_name": "Microsoft Huihui Desktop", "rate": 1},
        "style": {
            "background": "#08090C" if product_demo else "#F6F7FB",
            "foreground": "#FFFFFF" if product_demo else "#10131C",
            "accent": "#6650E8" if product_demo else "#4F35E8",
            "muted": "#C8CBD4" if product_demo else "#626A7F",
            "layout": layout,
            "brand_mark": "G",
        },
        "scenes": [
            {"id": "intro", "type": "title", "heading": "从产品信息到增长内容", "body": "一条可检查、可复现的本地工作流", "narration": "把产品事实、平台研究和内容生成，接进同一个增长工作流。", "duration": 2.4, "motion": "slow-zoom"},
            {
                "id": "product-proof", "type": "screenshot",
                "heading": "真实产品截图作为证据", "body": "不让模型虚构界面和功能",
                "hook": "产品界面就是证据" if product_demo else "",
                "narration": "视频使用真实产品截图，并用确定性的高亮标注解释关键功能。",
                "asset": "product-ui.png", "duration": 3.0, "motion": "slow-zoom",
                "highlight": {"x": 0.28, "y": 0.20, "width": 0.55, "height": 0.30},
                **({"cursor": {"x": 0.65, "y": 0.62, "size": 0.09}} if product_demo else {}),
            },
            {"id": "bounded-motion", "type": "text", "heading": "字幕、配音和动效都有边界", "body": "只调用审核过的预设，不生成任意动画代码", "narration": "字幕、配音和动效都来自审核后的计划，失败时不会生成假成片。", "duration": 3.0, "motion": "pan-up"},
            {"id": "cta", "type": "cta", "heading": "先生成，再审核，最后发布", "body": "Growth Lab", "narration": "生成完成后先检查画面和声音，再决定是否发布。", "duration": 2.4, "motion": "none"}
        ]
    }
    if product_demo:
        for index, scene in enumerate(plan["scenes"], start=1):
            scene["type"] = "screenshot"
            scene["asset"] = (
                f"source-card-pack/render/card-{index:02}.png" if card_source else "product-ui.png"
            )
            scene["asset_role"] = "rendered-card" if card_source else "product-screenshot"
            if card_source:
                scene["asset_source_id"] = f"card-{index:02}"
    if card_source:
        if not product_demo:
            raise ValueError("--card-source 仅用于 product-demo fixture")
        source_package = directory / "source-card-pack"
        source_render = source_package / "render"
        source_render.mkdir(parents=True, exist_ok=True)
        for index in range(1, len(plan["scenes"]) + 1):
            shutil.copy2(directory / "product-ui.png", source_render / f"card-{index:02}.png")
        source_manifest = source_package / "visual-manifest.json"
        source_manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "platform": "social-video",
                    "production_mode": "deterministic",
                    "canvas": {
                        "width": 1440, "height": 980, "format": "png",
                        "color_modes": ["RGB", "RGBA"],
                    },
                    "cards": [
                        {"id": f"card-{index:02}", "output": f"render/card-{index:02}.png", "status": "approved"}
                        for index in range(1, len(plan["scenes"]) + 1)
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        plan["visual_source"] = {
            "mode": "reused-card-pack",
            "manifest_file": source_manifest.relative_to(directory).as_posix(),
            "manifest_sha256": hashlib.sha256(source_manifest.read_bytes()).hexdigest(),
        }
    path = directory / "video-plan.json"
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--layout", choices=("classic", "product-demo"), default="classic")
    parser.add_argument("--card-source", action="store_true")
    args = parser.parse_args()
    print(create(Path(args.out).resolve(), args.layout, args.card_source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
