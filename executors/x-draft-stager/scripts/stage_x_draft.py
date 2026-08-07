#!/usr/bin/env python3
"""Save approved copy into X drafts through a loopback-only CDP session."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


SAVE_LABELS = {
    "save",
    "save draft",
    "保存",
    "保存草稿",
    "保存为草稿",
    "存入草稿",
    "下書き保存",
    "下書きに保存",
    "保存する",
}
DELETE_LABELS = {"delete", "delete draft", "删除", "删除草稿", "削除"}
EDIT_LABELS = {"edit", "编辑", "編集"}
SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


class DraftError(RuntimeError):
    pass


def package_digest(text: str, assets: list[Path], package_root: Path) -> str:
    asset_rows = [
        {
            "path": str(path.relative_to(package_root)).replace("\\", "/"),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in assets
    ]
    payload = json.dumps(
        {"text": text, "assets": asset_rows},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def resolve_assets(manifest: dict[str, Any], manifest_path: Path) -> list[Path]:
    values = manifest.get("asset_files") or []
    if not isinstance(values, list) or len(values) > 4:
        raise DraftError("X 图文草稿最多支持 4 张图片。")
    root = manifest_path.parent.resolve()
    assets: list[Path] = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise DraftError("asset_files 必须是非空相对路径列表。")
        path = (root / value).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise DraftError("X 草稿图片必须位于发布包目录内。") from exc
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            raise DraftError(f"X 草稿图片不存在或格式不支持：{value}")
        assets.append(path)
    return assets


def read_package(manifest_path: Path) -> tuple[dict[str, Any], str, list[Path]]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DraftError("发布清单不存在或不是有效 JSON。") from exc
    if manifest.get("platform") != "x":
        raise DraftError("发布清单平台必须是 x。")
    staging = manifest.get("draft_staging") or {}
    publish = manifest.get("publish") or {}
    governance = manifest.get("content_governance") or {}
    authorization = manifest.get("content_authorization") or {}
    if staging.get("approved") is not True:
        raise DraftError("发布清单没有批准保存到 X 草稿箱。")
    if publish.get("approved") is not False or publish.get("auto_publish") is not False:
        raise DraftError("草稿暂存要求真实发布和自动发布都保持关闭。")
    assets = resolve_assets(manifest, manifest_path)
    copy_file = manifest.get("copy_file")
    if not isinstance(copy_file, str) or not copy_file:
        raise DraftError("发布清单缺少 copy_file。")
    copy_path = (manifest_path.parent / copy_file).resolve()
    try:
        copy_path.relative_to(manifest_path.parent.resolve())
    except ValueError as exc:
        raise DraftError("copy_file 必须位于发布包目录内。") from exc
    try:
        text = copy_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise DraftError("无法读取发布文案。") from exc
    if copy_path.suffix.lower() == ".md":
        lines = text.splitlines()
        if lines and lines[0].startswith("# X 文案"):
            text = "\n".join(lines[1:]).strip()
    if not text:
        raise DraftError("发布文案为空。")
    if len(text) > 280:
        raise DraftError("发布文案超过本 Executor 的 280 字符安全上限。")
    required_governance = (
        "all_stages_scope_acknowledged",
        "skill_neutrality_persistent_acknowledged",
        "publisher_responsibility_accepted",
        "account_authority_confirmed",
        "safety_rules_remain_applicable_acknowledged",
    )
    missing_governance = [
        name for name in required_governance if governance.get(name) is not True
    ]
    if missing_governance:
        raise DraftError(
            "未接受贯穿所有环节的 Skill 中立性与发布者责任门禁："
            + ", ".join(missing_governance)
        )
    if not isinstance(governance.get("confirmed_at"), str) or not governance["confirmed_at"].strip():
        raise DraftError("content_governance.confirmed_at 必须记录生命周期确认时间。")
    required_authorizations = (
        "rights_confirmed",
        "final_content_reviewed",
        "generation_disclosed",
        "proxy_action_authorized",
        "target_account_confirmed",
        "distribution_settings_reviewed",
        "responsibility_accepted",
        "skill_neutrality_acknowledged",
    )
    missing_authorizations = [
        name for name in required_authorizations if authorization.get(name) is not True
    ]
    if missing_authorizations:
        raise DraftError(
            "缺少针对最终完整内容的明确授权确认："
            + ", ".join(missing_authorizations)
        )
    if not isinstance(authorization.get("confirmed_at"), str) or not authorization["confirmed_at"].strip():
        raise DraftError("content_authorization.confirmed_at 必须记录本次确认时间。")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if authorization.get("content_sha256") != digest:
        raise DraftError("最终文案已变化或授权哈希不匹配；必须重新展示并取得确认。")
    if assets:
        approved_package_digest = package_digest(text, assets, manifest_path.parent.resolve())
        if authorization.get("package_sha256") != approved_package_digest:
            raise DraftError("最终图片或文案与发布包授权哈希不匹配；必须重新展示并确认。")
    return manifest, text, assets


def cdp_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise DraftError("X_BROWSER_CDP_PORT 必须是整数。") from exc
    if not 1024 <= port <= 65535:
        raise DraftError("X_BROWSER_CDP_PORT 必须在 1024 到 65535 之间。")
    return port


def is_save_label(label: str) -> bool:
    return " ".join(label.strip().lower().split()) in SAVE_LABELS


def is_delete_label(label: str) -> bool:
    return " ".join(label.strip().lower().split()) in DELETE_LABELS


def is_edit_label(label: str) -> bool:
    return " ".join(label.strip().lower().split()) in EDIT_LABELS


async def upload_assets(page: Any, assets: list[Path]) -> None:
    if not assets:
        return
    file_input = page.locator('input[data-testid="fileInput"], input[type="file"]').first
    await file_input.wait_for(state="attached", timeout=15_000)
    await file_input.set_input_files([str(path) for path in assets])
    assigned = await file_input.evaluate("node => node.files ? node.files.length : 0")
    if assigned != len(assets):
        raise DraftError("X 编辑器接收的图片数量与批准发布包不一致。")
    try:
        await page.wait_for_function(
            """expected => {
              const busy = document.querySelectorAll('[role="progressbar"], [aria-busy="true"]');
              return expected > 0 && busy.length === 0;
            }""",
            len(assets),
            timeout=30_000,
        )
    except Exception as exc:
        raise DraftError("X 图片上传在 30 秒内未完成；已停止且未保存或发布。") from exc


async def visible_save_button(page: Any) -> tuple[Any, str] | tuple[None, str]:
    buttons = page.locator("button")
    for index in range(await buttons.count()):
        button = buttons.nth(index)
        if not await button.is_visible():
            continue
        testid = (await button.get_attribute("data-testid") or "").strip()
        if testid in {"tweetButton", "tweetButtonInline"}:
            continue
        text = (await button.inner_text()).strip()
        aria = (await button.get_attribute("aria-label") or "").strip()
        for label in (text, aria):
            if is_save_label(label):
                return button, label
    return None, ""


async def real_pointer_click(page: Any, locator: Any) -> None:
    box = await locator.bounding_box()
    if not box:
        raise DraftError("目标按钮没有可点击的屏幕位置。")
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    await page.mouse.move(x, y, steps=12)
    await page.wait_for_timeout(300)
    await page.mouse.click(x, y)


async def locator_is_topmost(page: Any, locator: Any) -> bool:
    return bool(
        await locator.evaluate(
            """node => {
              const rect = node.getBoundingClientRect();
              const hit = document.elementFromPoint(
                rect.x + rect.width / 2,
                rect.y + rect.height / 2
              );
              return hit === node || node.contains(hit);
            }"""
        )
    )


async def draft_present_in_open_list(page: Any, text: str) -> bool:
    await page.wait_for_url("**/compose/post/unsent/drafts", timeout=10_000)
    dialogs = page.locator('[role="dialog"]')
    normalized_text = " ".join(text.split())
    for index in range(await dialogs.count()):
        dialog = dialogs.nth(index)
        if not await dialog.is_visible():
            continue
        content = " ".join((await dialog.inner_text()).split())
        is_draft_list = "草稿" in content and (
            "未发送的帖子" in content or "预排期" in content
        )
        if is_draft_list and normalized_text in content:
            return True
    return False


async def stage(
    manifest_path: Path, port: int, stop_at_save_prompt: bool = False
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    _, text, assets = read_package(manifest_path)
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{port}", timeout=8_000
            )
        except Exception as exc:
            raise DraftError("无法连接 X 专用浏览器的本机 CDP 端口。") from exc
        if not browser.contexts:
            raise DraftError("专用浏览器没有可用 context。")
        context = browser.contexts[0]
        cookies = await context.cookies("https://x.com")
        if not any(c.get("name") == "auth_token" and c.get("value") for c in cookies):
            raise DraftError("X 专用浏览器尚未登录。")
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60_000)
        existing_drafts = page.locator('[data-testid="unsentButton"]')
        try:
            await existing_drafts.wait_for(state="visible", timeout=20_000)
            drafts_ready = True
        except Exception:
            drafts_ready = False
        if drafts_ready:
            await existing_drafts.click()
            await page.wait_for_timeout(1_000)
            if await draft_present_in_open_list(page, text):
                return {
                    "status": "existing-draft-verified-not-published",
                    "platform": "x",
                    "endpoint": f"127.0.0.1:{port}",
                    "characters": len(text),
                    "publish_clicked": False,
                }
            await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60_000)
        # X 可能同时渲染 compose modal 与首页内嵌编辑器；第一个是当前 modal。
        # 只操作 modal，避免把内容写入底层首页编辑框。
        editor = page.locator('[data-testid="tweetTextarea_0"]').first
        await editor.wait_for(state="visible", timeout=30_000)
        await editor.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.insert_text(text)
        await page.wait_for_timeout(500)
        editor_text = (await editor.inner_text()).strip()
        if " ".join(editor_text.split()) != " ".join(text.split()):
            raise DraftError("编辑器内容与批准文案不一致；已停止且未关闭或发布。")
        await upload_assets(page, assets)
        close_button = page.locator('[data-testid="app-bar-close"]')
        await close_button.wait_for(state="visible", timeout=10_000)
        # 使用真实鼠标路径，让 X 的悬停/焦点/最上层命中逻辑与人工点击一致。
        # 坐标来自 app-bar-close 自身，远离并且绝不复用发帖按钮坐标。
        save_button = None
        label = ""
        for attempt in range(2):
            await real_pointer_click(page, close_button)
            await page.wait_for_timeout(800)
            save_button, label = await visible_save_button(page)
            if save_button is not None:
                break
            if attempt == 0:
                if not await close_button.is_visible():
                    break
                if not await locator_is_topmost(page, close_button):
                    break
        if save_button is None:
            visible_buttons = await page.locator("button").evaluate_all(
                """nodes => nodes.filter(node => {
                  const rect = node.getBoundingClientRect();
                  return rect.width > 0 && rect.height > 0;
                }).map(node => ({
                  text: (node.innerText || '').trim(),
                  aria: (node.getAttribute('aria-label') || '').trim(),
                  testid: (node.getAttribute('data-testid') || '').trim()
                })).filter(item => item.text || item.aria || item.testid)"""
            )
            raise DraftError(
                "真实指针点击关闭后仍未找到文字明确的保存按钮；当前可见按钮："
                + json.dumps(visible_buttons, ensure_ascii=False)
            )
        if stop_at_save_prompt:
            return {
                "status": "save-prompt-ready-not-clicked",
                "label": label,
                "publish_clicked": False,
            }
        if not await locator_is_topmost(page, save_button):
            raise DraftError("保存按钮不是最上层命中目标；已停止且未发布。")
        # 保存只点击一次。X 可能延迟数秒关闭确认层；重复点击会在界面切换后
        # 落到下层控件，因此必须等待，再以真实草稿列表作为最终验证。
        await real_pointer_click(page, save_button)
        try:
            await save_button.wait_for(state="hidden", timeout=12_000)
        except Exception as exc:
            raise DraftError("保存确认层在 12 秒内未消失；已停止且不会重复点击。") from exc
        drafts = page.locator('[data-testid="unsentButton"]')
        if not await drafts.is_visible():
            await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60_000)
            await drafts.wait_for(state="visible", timeout=20_000)
        await drafts.click()
        await page.wait_for_timeout(1_500)
        if not await draft_present_in_open_list(page, text):
            raise DraftError("已点击保存，但在草稿列表中未找到完整文案；未发布。")
        return {
            "status": "saved-and-verified-draft-not-published",
            "platform": "x",
            "endpoint": f"127.0.0.1:{port}",
            "characters": len(text),
            "media_count": len(assets),
            "publish_clicked": False,
        }


async def find_unique_button(container: Any, predicate: Any, purpose: str) -> tuple[Any, str]:
    matches: list[tuple[Any, str]] = []
    buttons = container.locator("button")
    for index in range(await buttons.count()):
        button = buttons.nth(index)
        if not await button.is_visible():
            continue
        for label in (
            (await button.inner_text()).strip(),
            (await button.get_attribute("aria-label") or "").strip(),
        ):
            if predicate(label):
                matches.append((button, label))
                break
    if len(matches) != 1:
        raise DraftError(f"{purpose}需要唯一的白名单按钮，实际找到 {len(matches)} 个。")
    return matches[0]


async def delete_draft(manifest_path: Path, port: int) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    _, text, assets = read_package(manifest_path)
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{port}", timeout=8_000
            )
        except Exception as exc:
            raise DraftError("无法连接 X 专用浏览器的本机 CDP 端口。") from exc
        if not browser.contexts:
            raise DraftError("专用浏览器没有可用 context。")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60_000)
        drafts = page.locator('[data-testid="unsentButton"]')
        await drafts.wait_for(state="visible", timeout=20_000)
        await drafts.click()
        await page.wait_for_timeout(1_000)
        dialog = page.locator('[role="dialog"]:visible').last
        rows = dialog.locator('[data-testid="cellInnerDiv"]').filter(has_text=text)
        if await rows.count() != 1:
            raise DraftError("无法按批准文案唯一定位 X 草稿；未执行删除。")
        edit_button, _ = await find_unique_button(dialog, is_edit_label, "进入草稿编辑模式")
        await real_pointer_click(page, edit_button)
        await page.wait_for_timeout(500)
        row = dialog.locator('[data-testid="cellInnerDiv"]').filter(has_text=text)
        if await row.count() != 1:
            raise DraftError("编辑模式中无法唯一定位目标草稿；未执行删除。")
        await real_pointer_click(page, row.first)
        delete_button, _ = await find_unique_button(dialog, is_delete_label, "删除草稿")
        if not await locator_is_topmost(page, delete_button):
            raise DraftError("删除草稿按钮不是最上层命中目标；未执行删除。")
        await real_pointer_click(page, delete_button)
        await page.wait_for_timeout(500)
        confirm_dialog = page.locator('[role="dialog"]:visible').last
        confirm_button, label = await find_unique_button(
            confirm_dialog, is_delete_label, "确认删除草稿"
        )
        if not await locator_is_topmost(page, confirm_button):
            raise DraftError("确认删除按钮不是最上层命中目标；未执行删除。")
        await real_pointer_click(page, confirm_button)
        await page.wait_for_timeout(1_500)
        return {
            "status": "deleted-draft",
            "platform": "x",
            "characters": len(text),
            "media_count": len(assets),
            "confirmation_label": label,
            "publish_clicked": False,
        }


async def inspect_controls(port: int) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{port}", timeout=8_000
            )
        except Exception as exc:
            raise DraftError("无法连接 X 专用浏览器的本机 CDP 端口。") from exc
        if not browser.contexts:
            raise DraftError("专用浏览器没有可用 context。")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_timeout(2_000)
        controls = await page.locator("button,a").evaluate_all(
            """nodes => nodes.map(node => ({
              text: (node.innerText || '').trim(),
              aria: (node.getAttribute('aria-label') || '').trim(),
              testid: (node.getAttribute('data-testid') || '').trim()
            })).filter(item => {
              const value = `${item.text} ${item.aria} ${item.testid}`.toLowerCase();
              return /draft|save|草稿|保存|下書き|未发送|未送信/.test(value);
            })"""
        )
        compose_nodes = await page.locator(
            '[data-testid="tweetTextarea_0"], [data-testid="app-bar-close"]'
        ).evaluate_all(
            """nodes => nodes.map((node, index) => {
              const rect = node.getBoundingClientRect();
              let parent = node.parentElement;
              const ancestors = [];
              while (parent && ancestors.length < 8) {
                const testid = parent.getAttribute('data-testid');
                const role = parent.getAttribute('role');
                if (testid || role) ancestors.push({testid: testid || '', role: role || ''});
                parent = parent.parentElement;
              }
              return {
                index,
                testid: node.getAttribute('data-testid') || '',
                aria: node.getAttribute('aria-label') || '',
                visible: rect.width > 0 && rect.height > 0,
                rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                ancestors
              };
            })"""
        )
        close_hit = await page.evaluate(
            """() => {
              const close = document.querySelector('[data-testid="app-bar-close"]');
              if (!close) return null;
              const rect = close.getBoundingClientRect();
              const node = document.elementFromPoint(
                rect.x + rect.width / 2,
                rect.y + rect.height / 2
              );
              if (!node) return null;
              return {
                tag: node.tagName,
                testid: node.getAttribute('data-testid') || '',
                aria: node.getAttribute('aria-label') || '',
                className: typeof node.className === 'string' ? node.className : '',
                isCloseOrChild: node === close || close.contains(node),
                outer: node.outerHTML.slice(0, 500)
              };
            }"""
        )
        return {
            "status": "inspected-not-modified",
            "controls": controls,
            "compose_nodes": compose_nodes,
            "close_hit": close_hit,
        }


async def verify_draft(manifest_path: Path, port: int) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    _, text, _ = read_package(manifest_path)
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{port}", timeout=8_000
            )
        except Exception as exc:
            raise DraftError("无法连接 X 专用浏览器的本机 CDP 端口。") from exc
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60_000)
        drafts = page.locator('[data-testid="unsentButton"]')
        await drafts.wait_for(state="visible", timeout=20_000)
        await drafts.click()
        await page.wait_for_timeout(1_500)
        found = await draft_present_in_open_list(page, text)
        return {
            "status": "verified" if found else "not-found",
            "draft_found": found,
            "publish_clicked": False,
        }


async def inspect_drafts_ui(port: int) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(
            f"http://127.0.0.1:{port}", timeout=8_000
        )
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60_000)
        drafts = page.locator('[data-testid="unsentButton"]')
        await drafts.wait_for(state="visible", timeout=20_000)
        await drafts.click()
        await page.wait_for_timeout(1_500)
        dialogs = await page.locator('[role="dialog"]').evaluate_all(
            """nodes => nodes.map((node, index) => ({
              index,
              text: (node.innerText || '').trim().slice(0, 2000),
              visible: (() => { const r = node.getBoundingClientRect(); return r.width > 0 && r.height > 0; })(),
              testids: Array.from(node.querySelectorAll('[data-testid]'))
                .map(item => item.getAttribute('data-testid')).filter(Boolean).slice(0, 100)
            }))"""
        )
        return {
            "status": "inspected-drafts-not-modified",
            "url": page.url,
            "dialogs": dialogs,
        }


async def inspect_current_ui(port: int) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(
            f"http://127.0.0.1:{port}", timeout=8_000
        )
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        buttons = await page.locator("button").evaluate_all(
            """nodes => nodes.map((node, index) => {
              const text = (node.innerText || '').trim();
              const aria = (node.getAttribute('aria-label') || '').trim();
              const value = `${text} ${aria}`.toLowerCase();
              if (!/save|保存|下書き/.test(value)) return null;
              const rect = node.getBoundingClientRect();
              const hit = document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2);
              return {
                index, text, aria,
                testid: node.getAttribute('data-testid') || '',
                disabled: node.disabled || node.getAttribute('aria-disabled') === 'true',
                visible: rect.width > 0 && rect.height > 0,
                rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                topmost: hit === node || node.contains(hit),
                hit: hit ? {
                  tag: hit.tagName,
                  testid: hit.getAttribute('data-testid') || '',
                  aria: hit.getAttribute('aria-label') || ''
                } : null
              };
            }).filter(Boolean)"""
        )
        return {"status": "inspected-current-not-modified", "url": page.url, "buttons": buttons}


async def confirm_current_save(manifest_path: Path, port: int) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    _, text, _ = read_package(manifest_path)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(
            f"http://127.0.0.1:{port}", timeout=8_000
        )
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        save_button, label = await visible_save_button(page)
        if save_button is None or not is_save_label(label):
            raise DraftError("当前页面没有唯一、明确的保存按钮。")
        if not await locator_is_topmost(page, save_button):
            raise DraftError("当前保存按钮不是最上层命中目标；已停止。")
        await real_pointer_click(page, save_button)
        try:
            await save_button.wait_for(state="hidden", timeout=12_000)
        except Exception as exc:
            raise DraftError("当前保存确认层在 12 秒内未消失；不会重复点击。") from exc
        await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=60_000)
        drafts = page.locator('[data-testid="unsentButton"]')
        await drafts.wait_for(state="visible", timeout=20_000)
        await drafts.click()
        await page.wait_for_timeout(1_500)
        if not await draft_present_in_open_list(page, text):
            raise DraftError("保存后在真实草稿列表中未找到完整文案；未发布。")
        return {
            "status": "saved-and-verified-draft-not-published",
            "draft_found": True,
            "publish_clicked": False,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Save approved copy to X drafts; never publish")
    parser.add_argument("--manifest")
    parser.add_argument("--confirm-save-draft", action="store_true")
    parser.add_argument("--inspect-controls", action="store_true")
    parser.add_argument("--verify-draft", action="store_true")
    parser.add_argument("--inspect-drafts-ui", action="store_true")
    parser.add_argument("--inspect-current-ui", action="store_true")
    parser.add_argument("--stop-at-save-prompt", action="store_true")
    parser.add_argument("--confirm-current-save", action="store_true")
    parser.add_argument("--delete-draft", action="store_true")
    parser.add_argument("--confirm-delete-draft", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    port = cdp_port(os.environ.get("X_BROWSER_CDP_PORT", "19222"))
    if args.delete_draft:
        if not args.manifest or not args.confirm_delete_draft:
            raise DraftError("删除 X 草稿必须提供 --manifest 和 --confirm-delete-draft。")
        print(
            json.dumps(
                asyncio.run(delete_draft(Path(args.manifest).resolve(), port)),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.inspect_controls:
        print(json.dumps(asyncio.run(inspect_controls(port)), ensure_ascii=False, indent=2))
        return 0
    if args.inspect_drafts_ui:
        print(json.dumps(asyncio.run(inspect_drafts_ui(port)), ensure_ascii=False, indent=2))
        return 0
    if args.inspect_current_ui:
        print(json.dumps(asyncio.run(inspect_current_ui(port)), ensure_ascii=False, indent=2))
        return 0
    if args.confirm_current_save:
        if not args.manifest:
            raise DraftError("确认当前保存框必须提供 --manifest。")
        print(
            json.dumps(
                asyncio.run(confirm_current_save(Path(args.manifest).resolve(), port)),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.verify_draft:
        if not args.manifest:
            raise DraftError("验证草稿必须提供 --manifest。")
        print(
            json.dumps(
                asyncio.run(verify_draft(Path(args.manifest).resolve(), port)),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if not args.manifest:
        raise DraftError("保存草稿必须提供 --manifest。")
    if not args.confirm_save_draft:
        raise DraftError("必须显式提供 --confirm-save-draft。")
    result = asyncio.run(
        stage(Path(args.manifest).resolve(), port, args.stop_at_save_prompt)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DraftError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
    except KeyboardInterrupt:
        print("已由用户中断；未点击发布。", file=sys.stderr)
        raise SystemExit(130)
