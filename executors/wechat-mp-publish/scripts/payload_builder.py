#!/usr/bin/env python3
"""微信公众号文章配置解析与 payload 构建。"""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path


def parse_scalar(value: str) -> object:
    """解析简单 YAML 标量。"""
    value = value.strip()
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", ""}:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def load_simple_yaml(path: Path) -> dict[str, object]:
    """加载本项目约定的简单 YAML 子集。"""
    data: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, data)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "":
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(value)
    return data


def apply_defaults(config: dict[str, object]) -> dict[str, object]:
    """用环境变量补齐 wechat.yml 中留空的作者和原文链接。"""
    merged = dict(config)
    if not merged.get("author"):
        merged["author"] = os.environ.get("WECHAT_MP_DEFAULT_AUTHOR", "")
    if not merged.get("content_source_url"):
        merged["content_source_url"] = os.environ.get("WECHAT_MP_DEFAULT_SOURCE_URL", "")
    return merged


# 渲染模板以默认主题的颜色书写,再按 wechat.yml 的 theme 整体替换。
DEFAULT_THEME: dict[str, str] = {
    "accent": "118, 110, 222",
    "text": "62, 62, 62",
    "background": "199, 206, 246",
    "link": "87, 107, 149",
    "ink": "40, 38, 70",
    "tint": "241, 240, 252",
    "muted": "120, 120, 135",
    "line": "225, 225, 235",
    "generic": "200, 200, 210",
    # 非颜色项:off 时去掉标题与首屏卡片的强调色投影
    "shadow": "on",
}

THEMES: dict[str, dict[str, str]] = {
    "default": DEFAULT_THEME,
    # 品牌色只作点缀(编号、线条、标记、强调字),所有底色为白色,辅助色为中性灰。
    # 用法: theme 下写 base: white-accent,再用 accent / link 覆盖为品牌色。
    "white-accent": {
        "accent": "44, 62, 140",
        "text": "34, 34, 38",
        "background": "255, 255, 255",
        "link": "44, 62, 140",
        "ink": "34, 34, 38",
        "tint": "255, 255, 255",
        "muted": "112, 112, 120",
        "line": "232, 232, 236",
        "generic": "200, 200, 206",
        "shadow": "off",
    },
}


def hex_to_rgb(value: str) -> str:
    """`#2C3E8C` / `44, 62, 140` → `44, 62, 140`。"""
    value = value.strip()
    if value.startswith("#") and len(value) == 7:
        return ", ".join(str(int(value[i : i + 2], 16)) for i in (1, 3, 5))
    return value


def resolve_theme(config: dict[str, object]) -> dict[str, str]:
    """wechat.yml 的 theme 可以是主题名,也可以是 base + DEFAULT_THEME 中各颜色键的覆盖项。"""
    raw = config.get("theme", "default")
    if isinstance(raw, dict):
        base = dict(THEMES.get(str(raw.get("base", "default")), DEFAULT_THEME))
        base.update({k: hex_to_rgb(str(v)) for k, v in raw.items() if k in DEFAULT_THEME})
        return base
    name = str(raw or "default")
    if name not in THEMES:
        raise ValueError(f"未知 theme: {name},可选 {', '.join(THEMES)}")
    return dict(THEMES[name])


def apply_theme(html_text: str, theme: dict[str, str]) -> str:
    """把默认主题颜色替换为目标主题颜色。"""
    if theme.get("shadow") == "off":
        html_text = re.sub(r"box-shadow: 8px 8px 0 rgba\(118, 110, 222, [0-9.]+\);", "", html_text)
    for key, default in DEFAULT_THEME.items():
        if key == "shadow":
            continue
        html_text = html_text.replace(f"rgb({default})", f"rgb({theme[key]})")
        html_text = html_text.replace(f"rgba({default},", f"rgba({theme[key]},")
    return html_text


def dump_json(path: Path, payload: dict[str, object]) -> None:
    """写 JSON 文件。"""
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def markdown_to_html(markdown: str, theme: dict[str, str] | None = None) -> str:
    """Markdown 到微信内联排版 HTML。

    支持标题、段落、无序/有序列表、图片、可点击图片和加粗。首个标题前的
    图片或配图位之后的段落会进入首屏痛点卡片。`::: <block>` 到 `:::` 之间
    是排版块,见 BLOCK_RENDERERS。
    """
    lines, blocks = extract_blocks(markdown.splitlines())
    chunks: list[str] = []
    list_open: str | None = None
    intro_open = False
    seen_heading = False
    seen_lead_image = False

    def close_list() -> None:
        nonlocal list_open
        if list_open:
            list_open = None

    def close_intro() -> None:
        nonlocal intro_open
        if intro_open:
            chunks.append(
                '<p style="margin: -4px 0 0;padding: 0;box-sizing: border-box;'
                'font-size: 24px;line-height: 1;color: rgb(118, 110, 222);">✦</p>'
                "</section>"
            )
            intro_open = False

    def open_intro() -> None:
        nonlocal intro_open
        if not intro_open:
            chunks.append(
                '<section style="margin: 8px 0 30px;padding: 20px 20px 10px;'
                'border: 1px solid rgb(62, 62, 62);box-shadow: 8px 8px 0 rgba(118, 110, 222, 0.18);'
                'background: rgba(255, 255, 255, 0.68);box-sizing: border-box;overflow: hidden;">'
            )
            intro_open = True

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            close_list()
            continue
        block = re.fullmatch(r"\x00BLOCK(\d+)", line)
        if block:
            close_list()
            name, args, body = blocks[int(block.group(1))]
            if name != "figure" or seen_heading:
                close_intro()
            elif not seen_heading:
                seen_lead_image = True
            chunks.append(BLOCK_RENDERERS[name](args, body))
            continue
        linked_image = re.match(r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)", line.strip())
        if linked_image:
            close_list()
            alt = html.escape(linked_image.group(1))
            src = html.escape(linked_image.group(2))
            href = html.escape(linked_image.group(3))
            chunks.append(linked_image_block(src, alt, href))
            continue
        image = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if image:
            close_list()
            alt = html.escape(image.group(1))
            src = html.escape(image.group(2))
            chunks.append(image_block(src, alt))
            if not seen_heading:
                seen_lead_image = True
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            close_list()
            close_intro()
            seen_heading = True
            level = len(heading.group(1))
            if level == 2:
                chunks.append(section_heading(heading.group(2)))
            else:
                chunks.append(step_heading(heading.group(2)))
            continue
        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        if bullet:
            list_open = "ul"
            chunks.append(list_item(bullet.group(1)))
            continue
        ordered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if ordered:
            list_open = "ol"
            chunks.append(list_item(ordered.group(1)))
            continue
        close_list()
        if seen_lead_image and not seen_heading:
            open_intro()
            chunks.append(intro_paragraph(line))
        else:
            chunks.append(paragraph(line))
    close_list()
    close_intro()
    return apply_theme(wrap_wechat_article("\n".join(chunks) + "\n"), theme or DEFAULT_THEME)


def wrap_wechat_article(body: str) -> str:
    """包一层微信正文背景与内容容器。"""
    return f"""<section style="background-image: linear-gradient(to top, rgb(199, 206, 246), rgb(255, 255, 255));box-sizing: border-box;font-style: normal;font-weight: 400;text-align: justify;font-size: 16px;color: rgb(62, 62, 62);padding: 8px 0 28px;">
  <section style="box-sizing: border-box;padding: 0 18px;">
{body.rstrip()}
  </section>
</section>
"""


def paragraph(text: str) -> str:
    """渲染正文段落。"""
    return (
        '<p style="margin: 0 0 18px;padding: 0;box-sizing: border-box;'
        'font-size: 16px;line-height: 1.9;color: rgb(62, 62, 62);'
        f'letter-spacing: 0;text-align: justify;">{format_inline(text)}</p>'
    )


def intro_paragraph(text: str) -> str:
    """渲染首屏痛点卡片段落;`**加粗**` 在卡片内显示为强调色。"""
    highlighted = format_inline(text).replace(
        "<strong>", '<strong style="color: rgb(118, 110, 222);">'
    )
    return (
        '<p style="margin: 0 0 13px;padding: 0;box-sizing: border-box;'
        'font-size: 16px;line-height: 1.9;color: rgb(62, 62, 62);'
        f'letter-spacing: 0;text-align: justify;">{highlighted}</p>'
    )


def list_item(text: str) -> str:
    """用自绘圆点渲染列表,避免微信重排原生 ul/li。"""
    return (
        '<p style="margin: 0 0 10px;padding: 0;box-sizing: border-box;'
        'font-size: 16px;line-height: 1.85;color: rgb(62, 62, 62);'
        'letter-spacing: 0;text-align: left;">'
        '<span style="display: inline-block;margin-right: 8px;color: rgb(118, 110, 222);'
        'font-size: 16px;line-height: 1;">•</span>'
        f'<span>{format_inline(text)}</span>'
        "</p>"
    )


def image_block(src: str, alt: str) -> str:
    """渲染图片块。"""
    return f"""<section style="text-align: center;margin: 18px 0 28px;line-height: 0;box-sizing: border-box;">
  <section style="vertical-align: middle;display: block;line-height: 0;box-sizing: border-box;">
    <img src="{src}" alt="{alt}" style="vertical-align: middle;display: block;margin-left: auto;margin-right: auto;box-sizing: border-box;border-radius: 6px;border: 1px solid rgba(62, 62, 62, 0.12);height: auto;" />
  </section>
</section>"""


def linked_image_block(src: str, alt: str, href: str) -> str:
    """渲染可点击图片入口,图片下方用 alt 作为入口文字。"""
    label = alt or "点击查看"
    return f"""<section style="text-align: center;margin: 28px 0 10px;line-height: 0;box-sizing: border-box;">
  <a href="{href}" style="display: block;text-decoration: none;line-height: 0;">
    <img src="{src}" alt="{alt}" style="vertical-align: middle;display: block;margin-left: auto;margin-right: auto;box-sizing: border-box;border-radius: 6px;border: 1px solid rgba(62, 62, 62, 0.12);height: auto;" />
  </a>
</section>
<p style="margin: 0 0 8px;padding: 0;box-sizing: border-box;text-align: center;font-size: 14px;line-height: 1.7;color: rgb(87, 107, 149);">
  <a href="{href}" style="color: rgb(87, 107, 149);text-decoration: none;">{label}</a>
</p>"""


def section_heading(text: str) -> str:
    """渲染一级章节标题;`01 标题` 形式的两位编号显示为强调色。"""
    numbered = re.match(r"^(\d{2})\s+(.+)$", text)
    if numbered:
        label = (
            f'<span style="color: rgb(118, 110, 222);margin-right: 10px;">{numbered.group(1)}</span>'
            f"{format_inline(numbered.group(2))}"
        )
    else:
        label = format_inline(text)
    return f"""<section style="margin: 34px 0 18px;text-align: left;box-sizing: border-box;">
  <section style="display: inline-block;border-style: solid;border-width: 1px;border-color: rgb(62, 62, 62);padding: 10px 16px;background: rgba(255, 255, 255, 0.68);box-shadow: 8px 8px 0 rgba(118, 110, 222, 0.16);box-sizing: border-box;">
    <strong style="font-size: 18px;line-height: 1.45;color: rgb(62, 62, 62);">{label}</strong>
  </section>
</section>"""


def step_heading(text: str) -> str:
    """渲染步骤标题。"""
    return f"""<section style="margin: 30px 0 14px;padding: 12px 16px;border-left: 4px solid rgb(118, 110, 222);background: rgba(255, 255, 255, 0.72);box-sizing: border-box;">
  <strong style="font-size: 17px;line-height: 1.55;color: rgb(62, 62, 62);">{format_inline(text)}</strong>
</section>"""


def format_inline(text: str) -> str:
    """处理行内 Markdown。"""
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


# ---------------------------------------------------------------- 排版块
# 语法:
#   ::: card [dark|soft]      #### 眉题 / ### 标题 / 段落 / --- 分隔 / - 列表项 [| 标签]
#   ::: steps                 - 标题 | 说明 | 补充
#   ::: stats                 - 数值 | 说明
#   ::: bars 系列A | 系列B      - 指标 | A 百分比 | B 百分比
#   ::: figure                首行为图题,其余为配图说明;草稿同步前必须换成真实图片
#   :::
# 颜色一律写默认主题的 token,由 apply_theme 统一换色。

PLACEHOLDER_MARK = "data-wechat-placeholder"


def extract_blocks(lines: list[str]) -> tuple[list[str], list[tuple[str, str, list[str]]]]:
    """把 `::: name args ... :::` 替换成占位行,返回剩余行与块内容。"""
    out: list[str] = []
    blocks: list[tuple[str, str, list[str]]] = []
    i = 0
    while i < len(lines):
        start = re.match(r"^:::\s*([a-z]+)\s*(.*)$", lines[i].strip())
        if not start:
            out.append(lines[i])
            i += 1
            continue
        name, args = start.group(1), start.group(2).strip()
        if name not in BLOCK_RENDERERS:
            raise ValueError(f"未知排版块 ::: {name},可选 {', '.join(BLOCK_RENDERERS)}")
        body: list[str] = []
        i += 1
        while i < len(lines) and lines[i].strip() != ":::":
            body.append(lines[i].rstrip())
            i += 1
        if i == len(lines):
            raise ValueError(f"排版块 ::: {name} 缺少结束行 :::")
        i += 1
        out.append(f"\x00BLOCK{len(blocks)}")
        blocks.append((name, args, [line for line in body if line.strip()]))
    return out, blocks


def split_cells(text: str) -> list[str]:
    return [cell.strip() for cell in text.split("|")]


def list_body(line: str) -> str | None:
    match = re.match(r"^\s*[-*]\s+(.+)$", line)
    return match.group(1) if match else None


def render_card(args: str, body: list[str]) -> str:
    """卡片:默认白底细边;accent 为强调色边框;soft 为浅色底;dark 为深色底。"""
    dark = args == "dark"
    bg = "rgb(40, 38, 70)" if dark else ("rgb(241, 240, 252)" if args == "soft" else "rgb(255, 255, 255)")
    border = "rgb(40, 38, 70)" if dark else ("rgb(118, 110, 222)" if args == "accent" else "rgb(225, 225, 235)")
    text = "rgba(255, 255, 255, 0.86)" if dark else "rgb(62, 62, 62)"
    strong = "rgb(255, 255, 255)" if dark else "rgb(62, 62, 62)"
    soft = "rgba(255, 255, 255, 0.62)" if dark else "rgb(120, 120, 135)"
    mark = "rgba(255, 255, 255, 0.9)" if dark else "rgb(118, 110, 222)"
    divider = "rgba(255, 255, 255, 0.16)" if dark else "rgb(225, 225, 235)"
    parts: list[str] = []
    for line in body:
        stripped = line.strip()
        item = list_body(line)
        if stripped.startswith("#### "):
            parts.append(
                f'<p style="margin: 0 0 4px;font-size: 12px;line-height: 1.6;letter-spacing: 1px;color: {mark};">'
                f"{format_inline(stripped[5:])}</p>"
            )
        elif stripped.startswith("### "):
            parts.append(
                f'<p style="margin: 0 0 10px;font-size: 18px;line-height: 1.45;font-weight: bold;color: {strong};">'
                f"{format_inline(stripped[4:])}</p>"
            )
        elif stripped == "---":
            parts.append(f'<section style="margin: 12px 0;height: 1px;background: {divider};"></section>')
        elif item is not None:
            cells = split_cells(item)
            tag = ""
            if len(cells) > 1 and cells[1]:
                tag = (
                    f'<span style="display: inline-block;margin-left: 8px;padding: 0 8px;border-radius: 10px;'
                    f'font-size: 12px;line-height: 18px;color: {mark};border: 1px solid {mark};">'
                    f"{format_inline(cells[1])}</span>"
                )
            parts.append(
                f'<p style="margin: 0 0 8px;font-size: 15px;line-height: 1.7;color: {text};text-align: left;">'
                f'<span style="color: {mark};margin-right: 8px;">✓</span>{format_inline(cells[0])}{tag}</p>'
            )
        else:
            parts.append(
                f'<p style="margin: 0 0 10px;font-size: 15px;line-height: 1.75;color: {text};text-align: justify;">'
                f"{format_inline(stripped)}</p>"
            )
    return (
        f'<section style="margin: 16px 0 20px;padding: 18px 18px 10px;border: 1px solid {border};'
        f'border-radius: 12px;background: {bg};box-sizing: border-box;">\n'
        + "\n".join(parts)
        + "\n</section>"
    )


def render_steps(_: str, body: list[str]) -> str:
    """编号步骤:每项 `标题 | 说明 | 补充`。"""
    rows: list[str] = []
    items = [list_body(line) for line in body]
    for index, item in enumerate(filter(None, items), 1):
        cells = split_cells(item) + ["", ""]
        extra = ""
        if cells[2]:
            extra = (
                '<p style="margin: 8px 0 0;padding-top: 8px;border-top: 1px dashed rgb(225, 225, 235);'
                f'font-size: 13px;line-height: 1.65;color: rgb(120, 120, 135);">{format_inline(cells[2])}</p>'
            )
        rows.append(
            '<section style="margin: 0 0 10px;padding: 12px 14px;border: 1px solid rgb(225, 225, 235);'
            'border-left: 3px solid rgb(118, 110, 222);border-radius: 8px;background: rgb(255, 255, 255);box-sizing: border-box;">'
            f'<p style="margin: 0;font-size: 16px;line-height: 1.5;font-weight: bold;color: rgb(62, 62, 62);">'
            f'<span style="font-family: Menlo, monospace;font-size: 13px;color: rgb(118, 110, 222);margin-right: 8px;">{index:02d}</span>'
            f"{format_inline(cells[0])}</p>"
            f'<p style="margin: 4px 0 0;font-size: 15px;line-height: 1.7;color: rgb(62, 62, 62);">{format_inline(cells[1])}</p>'
            f"{extra}</section>"
        )
    return '<section style="margin: 16px 0 20px;box-sizing: border-box;">\n' + "\n".join(rows) + "\n</section>"


def render_stats(_: str, body: list[str]) -> str:
    """大号数字:每项 `数值 | 说明`,两列排布。"""
    cells_html: list[str] = []
    for item in filter(None, (list_body(line) for line in body)):
        value, label = (split_cells(item) + [""])[:2]
        cells_html.append(
            '<section style="display: inline-block;width: 50%;vertical-align: top;padding: 10px 8px 10px 0;box-sizing: border-box;">'
            f'<p style="margin: 0;font-size: 28px;line-height: 1.2;font-weight: bold;color: rgb(118, 110, 222);">{html.escape(value)}</p>'
            f'<p style="margin: 4px 0 0;font-size: 13px;line-height: 1.6;color: rgb(120, 120, 135);">{format_inline(label)}</p>'
            "</section>"
        )
    return (
        '<section style="margin: 16px 0 20px;padding: 6px 0;border-top: 1px solid rgb(62, 62, 62);'
        'border-bottom: 1px solid rgb(225, 225, 235);box-sizing: border-box;font-size: 0;">'
        + "".join(cells_html)
        + "</section>"
    )


def _bar(value: str, fill: str, strong: bool) -> str:
    try:
        width = max(0.0, min(100.0, float(value.rstrip("%"))))
    except ValueError as exc:
        raise ValueError(f"::: bars 数值必须是百分比: {value}") from exc
    weight = "bold" if strong else "normal"
    color = "rgb(62, 62, 62)" if strong else "rgb(120, 120, 135)"
    return (
        '<section style="margin: 4px 0;font-size: 0;box-sizing: border-box;">'
        '<section style="display: inline-block;width: 78%;vertical-align: middle;height: 8px;border-radius: 4px;'
        'background: rgb(225, 225, 235);overflow: hidden;box-sizing: border-box;">'
        f'<section style="width: {width:g}%;height: 8px;border-radius: 4px;background: {fill};"></section></section>'
        f'<section style="display: inline-block;width: 22%;vertical-align: middle;text-align: right;font-size: 13px;'
        f'line-height: 1.4;font-weight: {weight};color: {color};box-sizing: border-box;">{width:g}%</section>'
        "</section>"
    )


def render_bars(args: str, body: list[str]) -> str:
    """成对横向条形:`::: bars 系列A | 系列B`,每项 `指标 | A | B`(百分比)。"""
    series = (split_cells(args) + ["A", "B"])[:2] if args else ["A", "B"]
    legend = (
        '<p style="margin: 0 0 6px;font-size: 12px;line-height: 1.6;color: rgb(120, 120, 135);">'
        '<span style="display: inline-block;width: 10px;height: 10px;border-radius: 2px;background: rgb(118, 110, 222);'
        f'vertical-align: middle;margin-right: 6px;"></span>{html.escape(series[0])}'
        '<span style="display: inline-block;width: 10px;height: 10px;border-radius: 2px;background: rgb(200, 200, 210);'
        f'vertical-align: middle;margin: 0 6px 0 16px;"></span>{html.escape(series[1])}</p>'
    )
    rows: list[str] = []
    for item in filter(None, (list_body(line) for line in body)):
        label, a, b = (split_cells(item) + ["0", "0"])[:3]
        rows.append(
            '<section style="padding: 10px 0;border-bottom: 1px solid rgb(225, 225, 235);box-sizing: border-box;">'
            f'<p style="margin: 0 0 4px;font-size: 14px;line-height: 1.5;font-weight: bold;color: rgb(62, 62, 62);">{format_inline(label)}</p>'
            + _bar(a, "rgb(118, 110, 222)", True)
            + _bar(b, "rgb(200, 200, 210)", False)
            + "</section>"
        )
    return '<section style="margin: 16px 0 20px;box-sizing: border-box;">' + legend + "".join(rows) + "</section>"


def render_figure(_: str, body: list[str]) -> str:
    """配图位:只用于预览与排版评审,草稿同步会拒绝仍含配图位的正文。"""
    caption = format_inline(body[0].strip()) if body else "配图"
    notes = "".join(
        f'<p style="margin: 4px 0 0;font-size: 13px;line-height: 1.6;color: rgb(120, 120, 135);">{format_inline(line.strip())}</p>'
        for line in body[1:]
    )
    return (
        f'<section {PLACEHOLDER_MARK}="figure" style="margin: 18px 0 26px;padding: 22px 18px;border: 1.5px dashed rgb(118, 110, 222);'
        'border-radius: 10px;background: rgb(241, 240, 252);text-align: center;box-sizing: border-box;">'
        '<p style="margin: 0 0 4px;font-size: 12px;letter-spacing: 2px;color: rgb(118, 110, 222);">配图待生成</p>'
        f'<p style="margin: 0;font-size: 15px;line-height: 1.6;font-weight: bold;color: rgb(62, 62, 62);">{caption}</p>'
        f"{notes}</section>"
    )


BLOCK_RENDERERS = {
    "card": render_card,
    "steps": render_steps,
    "stats": render_stats,
    "bars": render_bars,
    "figure": render_figure,
}


def replace_local_images(html_text: str, mapping: dict[str, str]) -> str:
    """用微信图片 URL 替换本地图片路径。"""
    out = html_text
    for local, remote in mapping.items():
        out = out.replace(f'src="{html.escape(local)}"', f'src="{html.escape(remote)}"')
    return out


def build_preview_html(config: dict[str, object], content_html: str) -> str:
    """构建给人工审阅的公众号阅读页预览。"""
    accent = f"rgb({resolve_theme(config)['accent']})"
    title = html.escape(str(config.get("title", "")))
    author = html.escape(str(config.get("author", "")))
    digest = html.escape(str(config.get("digest", "")))
    source_url = html.escape(str(config.get("content_source_url", "")))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - 微信预览</title>
<style>
  :root {{
    color-scheme: light;
    --text: #1f2329;
    --muted: #767676;
    --line: #e9e9e9;
    --accent: {accent};
    --soft: #f6f8f8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: #f3f4f6;
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
    letter-spacing: 0;
  }}
  .phone-wrap {{
    max-width: 760px;
    margin: 0 auto;
    padding: 24px 14px 48px;
  }}
  .wechat-page {{
    min-height: 100vh;
    padding: 28px 22px 44px;
    background: #fff;
    box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
  }}
  .title {{
    margin: 0 0 12px;
    color: #111827;
    font-size: 25px;
    font-weight: 700;
    line-height: 1.32;
  }}
  .meta {{
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 18px;
    color: var(--muted);
    font-size: 14px;
  }}
  .meta .account {{ color: #576b95; }}
  .digest {{
    margin: 0 0 20px;
    padding: 14px 15px;
    border-left: 4px solid var(--accent);
    background: var(--soft);
    color: #374151;
    font-size: 15px;
    line-height: 1.72;
  }}
  .cover {{
    display: block;
    width: 100%;
    margin: 0 0 24px;
    border: 1px solid var(--line);
    border-radius: 6px;
  }}
  .content {{
    overflow-wrap: anywhere;
    font-size: 16px;
    line-height: 1.88;
  }}
  .content h2 {{
    margin: 30px 0 14px;
    color: #111827;
    font-size: 21px;
    line-height: 1.42;
  }}
  .content h3 {{
    margin: 34px 0 14px;
    padding-left: 11px;
    border-left: 4px solid var(--accent);
    color: #111827;
    font-size: 18px;
    line-height: 1.48;
  }}
  .content p {{ margin: 0 0 16px; }}
  .content img {{
    display: block;
    width: 100%;
    max-width: 100%;
    height: auto;
    margin: 20px auto 24px;
    border: 1px solid var(--line);
    border-radius: 6px;
  }}
  .content ul,
  .content ol {{
    margin: 2px 0 18px;
    padding-left: 1.35em;
  }}
  .content li {{ margin: 6px 0; }}
  .content section {{ max-width: 100%; }}
  .source {{
    margin-top: 34px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 14px;
  }}
  .source a {{
    color: #576b95;
    text-decoration: none;
  }}
  @media (min-width: 760px) {{
    .wechat-page {{ border-radius: 8px; }}
  }}
</style>
</head>
<body>
  <main class="phone-wrap">
    <article class="wechat-page">
      <h1 class="title">{title}</h1>
      <div class="meta"><span class="account">{author}</span><span>今天</span></div>
      <p class="digest">{digest}</p>
      <section class="content">
{content_html.rstrip()}
      </section>
      <footer class="source">原文入口: <a href="{source_url}">{source_url}</a></footer>
    </article>
  </main>
</body>
</html>
"""


def build_draft_payload(config: dict[str, object], content_html: str, thumb_media_id: str) -> dict[str, object]:
    """构建 /cgi-bin/draft/add payload。"""
    publish = config.get("publish")
    if not isinstance(publish, dict):
        publish = {}
    article = {
        "title": str(config.get("title", "")),
        "author": str(config.get("author", "")),
        "digest": str(config.get("digest", "")),
        "content": content_html,
        "content_source_url": str(config.get("content_source_url", "")),
        "thumb_media_id": thumb_media_id,
        "need_open_comment": int(config.get("need_open_comment", 0) or 0),
        "only_fans_can_comment": int(config.get("only_fans_can_comment", 0) or 0),
    }
    # 封面裁剪:X1_Y1_X2_Y2 为 0~1 的相对坐标,留空时由微信默认裁剪
    for key in ("pic_crop_235_1", "pic_crop_1_1"):
        if config.get(key):
            article[key] = str(config[key])
    if not article["title"]:
        raise ValueError("wechat.yml 缺少 title")
    return {"articles": [article]}
