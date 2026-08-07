#!/usr/bin/env python3
"""Compose one or more real screenshots onto an image-generated card.

The scene JSON controls crop, fit, focus, rounded corners, border, shadow,
rotation, and z-order. Real screenshots are only processed by Pillow; they are
never sent through the image model.

Example:
  uv run --with pillow python src/xhs-card-render/compose_screenshot_scene.py \
    --card outputs/.../img/_gen-03-effect.png \
    --scene outputs/.../scenes/03-scene.json \
    --out outputs/.../img/03-final.png --scale 2
"""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFilter


def color(value, alpha=255):
    if isinstance(value, (list, tuple)):
        values = tuple(int(v) for v in value)
        return values if len(values) == 4 else values + (alpha,)
    rgb = ImageColor.getrgb(value or "white")
    return rgb + (alpha,)


def resolve_path(scene_path, value):
    path = Path(value)
    return path if path.is_absolute() else scene_path.parent / path


def scaled_box(slot, board_size, scale):
    if "box_norm" in slot:
        x, y, w, h = slot["box_norm"]
        bw, bh = board_size
        values = (x * bw, y * bh, w * bw, h * bh)
    elif "box" in slot:
        values = slot["box"]
    else:
        raise ValueError(f"slot {slot.get('id', '?')} 缺少 box 或 box_norm")
    x, y, w, h = (round(float(v) * scale) for v in values)
    if w <= 0 or h <= 0:
        raise ValueError(f"slot {slot.get('id', '?')} 的宽高必须大于 0")
    return x, y, w, h


def crop_source(image, slot):
    if "crop_norm" in slot:
        x, y, w, h = slot["crop_norm"]
        box = (
            round(x * image.width),
            round(y * image.height),
            round((x + w) * image.width),
            round((y + h) * image.height),
        )
        return image.crop(box)
    if "crop" in slot:
        x, y, w, h = (round(float(v)) for v in slot["crop"])
        return image.crop((x, y, x + w, y + h))
    return image


def render_shot(image, size, fit, focus, pad_color):
    width, height = size
    fx, fy = (max(0.0, min(1.0, float(v))) for v in focus)
    surface = Image.new("RGBA", size, color(pad_color))

    if fit == "contain":
        ratio = min(width / image.width, height / image.height)
    elif fit == "cover":
        ratio = max(width / image.width, height / image.height)
    elif fit == "native":
        ratio = 1.0
    else:
        raise ValueError(f"未知 fit: {fit}")

    resized = image.resize(
        (max(1, round(image.width * ratio)), max(1, round(image.height * ratio))),
        Image.Resampling.LANCZOS,
    )
    left = round((width - resized.width) * fx)
    top = round((height - resized.height) * fy)
    surface.alpha_composite(resized, (left, top))
    return surface


def rounded_component(surface, radius, border, shape="rounded"):
    width, height = surface.size
    radius = max(0, min(round(radius), min(width, height) // 2))
    mask = Image.new("L", surface.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    if shape == "ellipse":
        mask_draw.ellipse((0, 0, width - 1, height - 1), fill=255)
    elif shape == "rounded":
        mask_draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    else:
        raise ValueError(f"未知 shape: {shape}")
    surface.putalpha(mask)

    border_width = round(float(border.get("width", 0)))
    if border_width > 0:
        overlay = Image.new("RGBA", surface.size, (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(overlay)
        box = (border_width // 2, border_width // 2, width - 1 - border_width // 2, height - 1 - border_width // 2)
        if shape == "ellipse":
            border_draw.ellipse(box, outline=color(border.get("color", "#D8D4E8")), width=border_width)
        else:
            border_draw.rounded_rectangle(
                box,
                radius=max(0, radius - border_width // 2),
                outline=color(border.get("color", "#D8D4E8")),
                width=border_width,
            )
        surface = Image.alpha_composite(surface, overlay)
    return surface


def add_component(board, component, x, y, rotation, shadow):
    if rotation:
        component = component.rotate(
            -float(rotation),
            resample=Image.Resampling.BICUBIC,
            expand=True,
        )
        x -= (component.width - round(shadow.pop("base_width"))) // 2
        y -= (component.height - round(shadow.pop("base_height"))) // 2

    if shadow.get("enabled", True):
        opacity = int(shadow.get("opacity", 42))
        blur = max(0, round(float(shadow.get("blur", 18))))
        ox, oy = (round(float(v)) for v in shadow.get("offset", [0, 8]))
        alpha = Image.new("L", board.size, 0)
        alpha.paste(component.getchannel("A"), (x + ox, y + oy))
        if blur:
            alpha = alpha.filter(ImageFilter.GaussianBlur(blur))
        shadow_layer = Image.new("RGBA", board.size, color(shadow.get("color", "#1D1738"), opacity))
        shadow_layer.putalpha(alpha.point(lambda value: value * opacity // 255))
        board = Image.alpha_composite(board, shadow_layer)

    layer = Image.new("RGBA", board.size, (0, 0, 0, 0))
    layer.alpha_composite(component, (x, y))
    return Image.alpha_composite(board, layer)


def compose(card_path, scene_path, out_path, scale):
    scene_path = Path(scene_path)
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    slots = scene.get("slots")
    if not isinstance(slots, list) or not slots:
        raise ValueError("scene JSON 必须包含非空 slots 数组")

    board = Image.open(card_path).convert("RGBA")
    base_size = board.size
    if scale != 1.0:
        board = board.resize(
            (round(board.width * scale), round(board.height * scale)),
            Image.Resampling.LANCZOS,
        )

    for slot in sorted(slots, key=lambda item: float(item.get("z", 0))):
        slot_id = slot.get("id", "?")
        shot_path = resolve_path(scene_path, slot["shot"])
        if not shot_path.exists():
            raise FileNotFoundError(f"slot {slot_id} 截图不存在: {shot_path}")

        x, y, width, height = scaled_box(slot, base_size, scale)
        shot = crop_source(Image.open(shot_path).convert("RGBA"), slot)
        fit = slot.get("fit", "cover")
        focus = slot.get("focus", [0.5, 0.5])
        component = render_shot(shot, (width, height), fit, focus, slot.get("pad_color", "white"))
        radius = float(slot.get("radius", 20)) * scale
        border = dict(slot.get("border", {}))
        if "width" in border:
            border["width"] = float(border["width"]) * scale
        component = rounded_component(component, radius, border, slot.get("shape", "rounded"))

        shadow = dict(slot.get("shadow", {}))
        shadow["base_width"] = width
        shadow["base_height"] = height
        if "blur" in shadow:
            shadow["blur"] = float(shadow["blur"]) * scale
        if "offset" in shadow:
            shadow["offset"] = [float(v) * scale for v in shadow["offset"]]
        board = add_component(board, component, x, y, slot.get("rotation", 0), shadow)
        print(f"slot {slot_id}: {shot_path.name} -> {width}x{height} @ ({x},{y}) fit={fit} z={slot.get('z', 0)}")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    board.convert("RGB").save(out_path)
    print(f"wrote {out_path} | canvas {board.width}x{board.height} | slots={len(slots)}")


def main():
    parser = argparse.ArgumentParser(description="按场景配置把多张真实截图合成到 image2 卡片底板。")
    parser.add_argument("--card", required=True, help="GPT Image 2 完整效果底板")
    parser.add_argument("--scene", required=True, help="截图场景 JSON")
    parser.add_argument("--out", required=True, help="输出成卡路径")
    parser.add_argument("--scale", type=float, default=1.0, help="整卡放大倍数，2 可提升截图可读性")
    args = parser.parse_args()
    if args.scale <= 0:
        parser.error("--scale 必须大于 0")
    compose(args.card, args.scene, args.out, args.scale)


if __name__ == "__main__":
    main()
