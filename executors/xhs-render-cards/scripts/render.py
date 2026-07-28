"""Render xhs cards: cards.json -> PNG files.

Usage:
    uv run --with playwright --with jinja2 \\
      executors/xhs-render-cards/scripts/render.py \\
      --input memory/example-loop/outputs/example-post/cards.json \\
      --output memory/example-loop/outputs/example-post/img

Layouts: cover / intro / question / shot / tools

A `shot` card embeds a screenshot via an `image` field (path relative to the
cards.json dir); render.py copies it into the temp render dir so file:// resolves.
"""

import argparse
import asyncio
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"


def render_html(card: dict, page_num: str) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    tpl = env.get_template("card.html.j2")
    return tpl.render(page_num=page_num, **card)


async def shoot(
    html_dir: Path, out_dir: Path, cards: list[dict], assets_dir: Path, browser_channel: str
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        launch_options = {"channel": browser_channel} if browser_channel else {}
        browser = await p.chromium.launch(**launch_options)
        ctx = await browser.new_context(
            viewport={"width": 1080, "height": 1440},
            device_scale_factor=2,
        )
        page = await ctx.new_page()
        for i, card in enumerate(cards, 1):
            page_num = f"{i:02d}/{len(cards):02d}"
            # If the card references an image, copy it next to the HTML so the
            # file:// src resolves inside the temp render dir.
            if card.get("image"):
                src = (assets_dir / card["image"]).resolve()
                if not src.exists():
                    print(f"  WARN: image not found: {src}", file=sys.stderr)
                else:
                    shutil.copy(src, html_dir / src.name)
                    card = {**card, "image": src.name}
            html = render_html(card, page_num)
            html_file = html_dir / f"{i:02d}.html"
            html_file.write_text(html, encoding="utf-8")
            await page.goto(f"file://{html_file}")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(300)
            png = out_dir / f"{i:02d}-{card.get('slug', card['layout'])}.png"
            await page.screenshot(path=str(png), full_page=False, omit_background=False)
            print(f"  rendered {png.name}")
        await browser.close()


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="cards.json path")
    ap.add_argument("--output", required=True, help="output dir for PNGs")
    ap.add_argument("--browser-channel", default=os.environ.get("XHS_BROWSER_CHANNEL", "chrome"),
                    help="Playwright browser channel (default: chrome; empty uses bundled Chromium)")
    args = ap.parse_args()

    cards_file = Path(args.input).resolve()
    out_dir = Path(args.output).resolve()
    if not cards_file.exists():
        print(f"error: {cards_file} not found", file=sys.stderr)
        return 1

    cards = json.loads(cards_file.read_text(encoding="utf-8"))
    print(f"rendering {len(cards)} cards from {cards_file.name}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        shutil.copy(TEMPLATES / "base.css", tmp_dir / "base.css")
        await shoot(tmp_dir, out_dir, cards, cards_file.parent, args.browser_channel)

    print(f"done -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
