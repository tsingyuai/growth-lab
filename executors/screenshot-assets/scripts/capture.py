#!/usr/bin/env python3
"""Capture an authenticated Chrome page over CDP using a user-controlled session."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def capture(args: argparse.Namespace) -> None:
    destination = Path(args.out).expanduser().resolve()
    if destination.exists() and not args.force:
        raise SystemExit(f"output exists: {destination}; pass --force to replace it")
    destination.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(args.cdp)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        pages = context.pages
        page = pages[0] if pages else await context.new_page()
        await page.set_viewport_size({"width": args.width, "height": args.height})
        await page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout_ms)
        if args.wait_selector:
            await page.locator(args.wait_selector).wait_for(state="visible", timeout=args.timeout_ms)
        if args.delay_ms:
            await page.wait_for_timeout(args.delay_ms)
        if args.selector:
            target = page.locator(args.selector).first
            await target.wait_for(state="visible", timeout=args.timeout_ms)
            await target.screenshot(path=str(destination))
        else:
            await page.screenshot(path=str(destination), full_page=args.full_page)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cdp", default="http://127.0.0.1:9222")
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--selector")
    parser.add_argument("--wait-selector")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--delay-ms", type=int, default=0)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--full-page", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.width < 320 or args.height < 240:
        parser.error("viewport is too small")
    asyncio.run(capture(args))


if __name__ == "__main__":
    main()
