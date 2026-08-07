#!/usr/bin/env python3
"""Render a bounded workflow-led social card pack from exact copy and one background."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


LAYOUTS = {"flow", "stack", "converge", "gate", "loop"}
DEFAULT_FONT = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")
FALLBACK_FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
BOLD_FONT = Path(r"C:\Windows\Fonts\msyhbd.ttc")


class RenderError(RuntimeError):
    pass


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = BOLD_FONT if bold and BOLD_FONT.is_file() else DEFAULT_FONT
    if not path.is_file():
        path = FALLBACK_FONT
    if not path.is_file():
        raise RenderError("未找到 Noto Sans SC 或微软雅黑字体。")
    return ImageFont.truetype(str(path), size=size)


def read_spec(path: Path) -> dict[str, Any]:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RenderError("卡片 spec 不存在或不是有效 JSON。") from exc
    if not isinstance(spec, dict) or spec.get("schema_version") != 1:
        raise RenderError("卡片 spec schema_version 必须是 1。")
    canvas = spec.get("canvas") or {}
    if (canvas.get("width"), canvas.get("height")) != (1080, 1440):
        raise RenderError("工作流卡片仅支持 1080x1440。")
    cards = spec.get("cards")
    if not isinstance(cards, list) or not 3 <= len(cards) <= 8:
        raise RenderError("卡片数量必须在 3 到 8 之间。")
    seen: set[str] = set()
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            raise RenderError(f"cards[{index}] 必须是对象。")
        card_id = str(card.get("id") or "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", card_id) or card_id in seen:
            raise RenderError(f"cards[{index}].id 无效或重复。")
        seen.add(card_id)
        if card.get("layout") not in LAYOUTS:
            raise RenderError(f"cards[{index}].layout 无效。")
        for field in ("eyebrow", "title", "body", "footer"):
            if not isinstance(card.get(field), str) or not card[field].strip():
                raise RenderError(f"cards[{index}].{field} 不能为空。")
        nodes = card.get("nodes")
        if not isinstance(nodes, list) or not 3 <= len(nodes) <= 4:
            raise RenderError(f"cards[{index}].nodes 必须包含 3 到 4 项。")
        if any(not isinstance(node, str) or not node.strip() or len(node) > 18 for node in nodes):
            raise RenderError(f"cards[{index}].nodes 包含无效文本。")
    return spec


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int, lines: int) -> list[str]:
    result: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if draw.textbbox((0, 0), candidate, font=face)[2] <= width:
            current = candidate
        else:
            if current:
                result.append(current)
            current = char
            if len(result) >= lines:
                break
    if current and len(result) < lines:
        result.append(current)
    if len(result) == lines and "".join(result) != text:
        while result[-1] and draw.textbbox((0, 0), result[-1] + "…", font=face)[2] > width:
            result[-1] = result[-1][:-1]
        result[-1] += "…"
    return result


def centered_text(
    draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str,
    face: ImageFont.FreeTypeFont, fill: str, max_lines: int = 2,
) -> None:
    left, top, right, bottom = box
    lines = wrap(draw, text, face, right - left - 30, max_lines)
    line_height = face.size + 10
    y = top + (bottom - top - len(lines) * line_height) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=face)
        x = left + (right - left - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=face, fill=fill)
        y += line_height


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str) -> None:
    draw.line((*start, *end), fill=color, width=5)
    x, y = end
    if abs(end[0] - start[0]) >= abs(end[1] - start[1]):
        direction = 1 if end[0] > start[0] else -1
        points = [(x, y), (x - direction * 18, y - 12), (x - direction * 18, y + 12)]
    else:
        direction = 1 if end[1] > start[1] else -1
        points = [(x, y), (x - 12, y - direction * 18), (x + 12, y - direction * 18)]
    draw.polygon(points, fill=color)


def node(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, accent: str) -> None:
    draw.rounded_rectangle(box, radius=24, fill="#12161DEB", outline=accent, width=3)
    centered_text(draw, box, text, load_font(30, bold=True), "#FFFFFF", 2)


def draw_evidence(draw: ImageDraw.ImageDraw, card: dict[str, Any], accent: str) -> None:
    nodes = card["nodes"]
    layout = card["layout"]
    if layout == "flow":
        boxes = [(70 + index * 250, 690, 270 + index * 250, 850) for index in range(len(nodes))]
        for index, (box, label) in enumerate(zip(boxes, nodes)):
            node(draw, box, label, accent)
            if index:
                arrow(draw, (boxes[index - 1][2] + 8, 770), (box[0] - 8, 770), accent)
    elif layout == "stack":
        boxes = [(70, 610 + index * 150, 440, 720 + index * 150) for index in range(len(nodes))]
        for index, (box, label) in enumerate(zip(boxes, nodes)):
            node(draw, box, label, accent)
            if index:
                arrow(draw, (255, boxes[index - 1][3] + 7), (255, box[1] - 7), accent)
        draw.rounded_rectangle((520, 610, 1010, 1050), radius=34, fill="#0B0E14E8", outline="#FFFFFF44", width=2)
        centered_text(draw, (550, 650, 980, 1010), card["body"], load_font(42), "#FFFFFF", 5)
    elif layout == "converge":
        boxes = [(70, 610 + index * 140, 390, 710 + index * 140) for index in range(len(nodes) - 1)]
        result_box = (660, 700, 1010, 920)
        for box, label in zip(boxes, nodes[:-1]):
            node(draw, box, label, accent)
            arrow(draw, (box[2] + 10, (box[1] + box[3]) // 2), (result_box[0] - 10, 810), accent)
        node(draw, result_box, nodes[-1], "#FFFFFF")
    elif layout == "gate":
        top_boxes = [(70 + index * 320, 640, 330 + index * 320, 770) for index in range(len(nodes) - 1)]
        gate_box = (300, 900, 780, 1050)
        targets = [410, 540, 670]
        for target_x, box, label in zip(targets, top_boxes, nodes[:-1]):
            node(draw, box, label, accent)
            arrow(draw, ((box[0] + box[2]) // 2, box[3] + 8), (target_x, gate_box[1] - 8), accent)
        node(draw, gate_box, nodes[-1], "#FFFFFF")
    else:
        boxes = [(80, 620, 390, 760), (690, 620, 1000, 760), (690, 900, 1000, 1040), (80, 900, 390, 1040)]
        for box, label in zip(boxes, nodes[:4]):
            node(draw, box, label, accent)
        arrow(draw, (400, 690), (680, 690), accent)
        arrow(draw, (845, 770), (845, 890), accent)
        arrow(draw, (680, 970), (400, 970), accent)
        arrow(draw, (235, 890), (235, 770), accent)


def render_card(
    spec: dict[str, Any], card: dict[str, Any], index: int, background: Image.Image, output: Path
) -> None:
    canvas = ImageOps.fit(background.convert("RGB"), (1080, 1440), method=Image.Resampling.LANCZOS)
    image = canvas.convert("RGBA")
    image.alpha_composite(Image.new("RGBA", image.size, "#05070BC8"))
    draw = ImageDraw.Draw(image)
    accent = (spec.get("palette") or {}).get("accent", "#68F58A")
    secondary = (spec.get("palette") or {}).get("secondary", "#8067FF")
    draw.rounded_rectangle((60, 55, 130, 125), radius=16, fill=accent)
    mark = load_font(38)
    centered_text(draw, (60, 55, 130, 125), str(spec.get("brand_mark") or "G"), mark, "#05070B", 1)
    draw.text((155, 68), str(spec.get("brand") or "Growth Lab"), font=load_font(38), fill="#FFFFFF")
    draw.text((870, 75), f"{index:02} / {len(spec['cards']):02}", font=load_font(26), fill="#C6CBD6")
    draw.rounded_rectangle((60, 175, 300, 225), radius=25, outline=secondary, width=2)
    centered_text(draw, (60, 175, 300, 225), card["eyebrow"], load_font(24, bold=True), secondary, 1)
    title_face = load_font(76, bold=True)
    title_lines = wrap(draw, card["title"], title_face, 950, 2)
    y = 275
    for line in title_lines:
        draw.text((60, y), line, font=title_face, fill="#FFFFFF")
        y += 96
    if card["layout"] != "stack":
        body_lines = wrap(draw, card["body"], load_font(34), 940, 3)
        body_y = y + 20
        for line in body_lines:
            draw.text((62, body_y), line, font=load_font(34), fill="#C6CBD6")
            body_y += 48
    draw_evidence(draw, card, accent)
    draw.line((60, 1230, 1020, 1230), fill="#FFFFFF33", width=2)
    draw.text((60, 1270), card["footer"], font=load_font(34, bold=True), fill="#FFFFFF")
    draw.text((60, 1355), "本地测试样片 · 未发布", font=load_font(24), fill="#8E96A7")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, format="PNG", optimize=True)


def render(spec_path: Path, background_path: Path, output_dir: Path) -> dict[str, Any]:
    spec = read_spec(spec_path)
    if not background_path.is_file():
        raise RenderError("背景图片不存在。")
    with Image.open(background_path) as source:
        background = source.copy()
    render_dir = output_dir / "render"
    cards = []
    for index, card in enumerate(spec["cards"], start=1):
        filename = f"{index:02}-{card['id']}.png"
        render_card(spec, card, index, background, render_dir / filename)
        cards.append(
            {
                "id": card["id"], "role": card.get("role", card["layout"]),
                "output": f"render/{filename}", "copy_source": "../copy.md",
                "source_mode": "separable-layer", "status": "approved",
            }
        )
    manifest = {
        "schema_version": 1,
        "platform": "xiaohongshu",
        "production_mode": "separable-layer",
        "canvas": {"width": 1080, "height": 1440, "format": "png", "color_modes": ["RGB"]},
        "cards": cards,
    }
    (output_dir / "visual-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--background", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = render(args.spec.resolve(), args.background.resolve(), args.out.resolve())
    except (OSError, ValueError, RenderError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"output": str(args.out), "cards": len(manifest["cards"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
