#!/usr/bin/env python3
"""Browser-first, read-only X collector with direct/proxy preflight."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Mapping
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit
import urllib.request
import urllib.error


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEFAULT_EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DEFAULT_PROFILE = r"%LOCALAPPDATA%\growth-lab\x\browser-profile"
DEFAULT_PROBE_URL = "https://x.com/robots.txt"
ALLOWED_ENV = {
    "X_BROWSER_PROFILE_DIR",
    "X_BROWSER_CDP_PORT",
    "X_CONNECTIVITY_URL",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_TEXT_MODEL",
    "SOCIAL_BROWSER_FAMILY",
    "SOCIAL_BROWSER_PATH",
    "SOCIAL_PROXY_MODE",
    "SOCIAL_PROXY_URL",
    "SOCIAL_PROXY_BYPASS",
}
MAX_MEDIA_BYTES = 25 * 1024 * 1024


class CollectorError(RuntimeError):
    """Expected failure that should be shown without a traceback."""


def log(*values: object) -> None:
    print(*values, flush=True)


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in ALLOWED_ENV:
            values[key] = value.strip().strip('"').strip("'")
    return values


def resolved_config(root: Path, environ: Mapping[str, str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for filename in (".env", ".env.local"):
        values.update(read_env_file(root / filename))
    for key in ALLOWED_ENV:
        if environ.get(key):
            values[key] = environ[key]
    return values


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value)))


def ensure_external_profile(profile: Path, repo: Path) -> None:
    resolved_profile = profile.resolve()
    resolved_repo = repo.resolve()
    try:
        resolved_profile.relative_to(resolved_repo)
    except ValueError:
        return
    raise CollectorError("X_BROWSER_PROFILE_DIR 必须位于仓库外。")


def validate_probe_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in {"x.com", "www.x.com"}:
        raise CollectorError("X_CONNECTIVITY_URL 必须是 x.com 的 HTTPS 地址。")
    return url


def validate_cdp_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise CollectorError("X_BROWSER_CDP_PORT 必须是整数。") from exc
    if not 1024 <= port <= 65535:
        raise CollectorError("X_BROWSER_CDP_PORT 必须在 1024 到 65535 之间。")
    return port


def resolve_browser(config: Mapping[str, str]) -> tuple[str, Path]:
    configured_path = config.get("SOCIAL_BROWSER_PATH", "").strip()
    family = config.get("SOCIAL_BROWSER_FAMILY", "auto").strip().lower()
    if family not in {"auto", "chrome", "edge"}:
        raise CollectorError("SOCIAL_BROWSER_FAMILY 必须是 auto、chrome 或 edge。")
    if configured_path:
        path = expand_path(configured_path)
        if not path.is_file():
            raise CollectorError(f"SOCIAL_BROWSER_PATH 指向的浏览器不存在：{path}")
        detected = "edge" if path.name.lower() == "msedge.exe" else "chrome"
        return detected, path
    browser_paths = {
        "chrome": [
            Path(DEFAULT_CHROME),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        ],
        "edge": [
            Path(DEFAULT_EDGE),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        ],
    }
    families = ("chrome", "edge") if family == "auto" else (family,)
    candidates = [
        (candidate_family, path)
        for candidate_family in families
        for path in browser_paths[candidate_family]
    ]
    for candidate_family, path in candidates:
        if path.is_file():
            return candidate_family, path
    raise CollectorError("未找到 Chrome 或 Edge；请配置 SOCIAL_BROWSER_PATH。")


def parse_count(value: object) -> int:
    text = str(value or "").strip().replace(",", "").replace("+", "")
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([KMBkmb万亿]?)", text)
    if not match:
        return 0
    multiplier = {
        "k": 1_000,
        "m": 1_000_000,
        "b": 1_000_000_000,
        "万": 10_000,
        "亿": 100_000_000,
    }.get(match.group(2).lower(), 1)
    return int(float(match.group(1)) * multiplier)


def build_search_query(keyword: str, exact: bool, excluded: list[str]) -> str:
    query = f'"{keyword}"' if exact else keyword
    for term in excluded:
        if term:
            query += f' -"{term}"'
    return query


def strict_filter(posts: list[dict[str, Any]], keyword: str, exact: bool, excluded: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for post in posts:
        text = str(post.get("text") or "")
        post_id = str(post.get("post_id") or "")
        if not post_id or post_id in seen:
            continue
        folded = text.casefold()
        if exact and keyword.casefold() not in folded:
            continue
        if any(term and term.casefold() in folded for term in excluded):
            continue
        seen.add(post_id)
        rows.append(post)
    return rows


def validate_loopback_bypass(value: str) -> str:
    hosts = {item.strip().lower() for item in value.split(",") if item.strip()}
    if not {"127.0.0.1", "localhost", "::1"}.issubset(hosts):
        raise CollectorError(
            "SOCIAL_PROXY_BYPASS 必须包含 127.0.0.1、localhost 和 ::1。"
        )
    return value


def playwright_proxy(proxy_url: str, bypass: str = "") -> dict[str, str]:
    parsed = urlsplit(proxy_url)
    if parsed.scheme not in {"http", "https", "socks4", "socks5"} or not parsed.hostname or not parsed.port:
        raise CollectorError(
            "SOCIAL_PROXY_URL 必须是包含端口的 HTTP(S)、SOCKS4 或 SOCKS5 代理 URL。"
        )
    proxy: dict[str, str] = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
    if parsed.username:
        proxy["username"] = unquote(parsed.username)
    if parsed.password:
        proxy["password"] = unquote(parsed.password)
    if bypass:
        proxy["bypass"] = bypass
    return proxy


async def probe_connection(
    playwright: Any, url: str, proxy: dict[str, str] | None, timeout_seconds: int
) -> bool:
    options: dict[str, Any] = {}
    if proxy:
        options["proxy"] = proxy
    request = await playwright.request.new_context(**options)
    try:
        response = await request.get(url, timeout=timeout_seconds * 1_000, fail_on_status_code=False)
        return response.status < 500
    except Exception:
        return False
    finally:
        await request.dispose()


def system_proxy_url(target_url: str) -> str:
    proxies = urllib.request.getproxies()
    scheme = urlsplit(target_url).scheme.lower()
    return str(proxies.get(scheme) or proxies.get("all") or "").strip()


def launch_detached_login(
    browser_path: Path,
    profile: Path,
    route: str,
    proxy: dict[str, str] | None,
    bypass: str,
    cdp_port: int,
) -> None:
    if proxy and (proxy.get("username") or proxy.get("password")):
        raise CollectorError(
            "普通浏览器登录不能安全地把代理账号密码放入启动参数；请使用系统代理/PAC。"
        )
    arguments = [
        str(browser_path),
        f"--user-data-dir={profile}",
        "--new-window",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=Translate,TranslateUI",
        "--remote-debugging-address=127.0.0.1",
        f"--remote-debugging-port={cdp_port}",
    ]
    if route == "direct":
        arguments.append("--no-proxy-server")
    elif proxy:
        arguments.append(f"--proxy-server={proxy['server']}")
        arguments.append(f"--proxy-bypass-list={bypass.replace(',', ';')}")
    arguments.append("https://x.com/i/flow/login")
    creation_flags = 0
    if os.name == "nt":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    subprocess.Popen(
        arguments,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=creation_flags,
    )


def cdp_endpoint(port: int) -> str:
    return f"http://127.0.0.1:{port}"


async def attach_cdp(playwright: Any, port: int) -> tuple[Any, Any]:
    try:
        browser = await playwright.chromium.connect_over_cdp(
            cdp_endpoint(port), timeout=8_000
        )
    except Exception as exc:
        raise CollectorError(
            "X 专用浏览器的本机 CDP 端口不可用；请关闭旧专用窗口后重新运行 --login-only。"
        ) from exc
    if not browser.contexts:
        raise CollectorError("X 专用浏览器已连接，但没有可用 browser context。")
    return browser, browser.contexts[0]


Probe = Callable[[str], Awaitable[bool]]


async def resolve_route(mode: str, has_proxy: bool, probe: Probe) -> tuple[str, dict[str, bool | str]]:
    report: dict[str, bool | str] = {
        "requested_mode": mode,
        "direct": False,
        "system": False,
        "explicit": False,
    }
    if mode == "auto":
        report["direct"] = await probe("direct")
        if report["direct"]:
            report["selected"] = "direct"
            return "direct", report
        if has_proxy:
            report["explicit"] = await probe("explicit")
            if report["explicit"]:
                report["selected"] = "explicit"
                return "explicit", report
        report["system"] = await probe("system")
        if report["system"]:
            report["selected"] = "system"
            return "system", report
        raise CollectorError(
            "X 直连测试失败，且当前已配置的代理路径也不可用。请检查 SOCIAL_PROXY_MODE 和本机代理后重试。"
        )
    if mode == "direct":
        report["direct"] = await probe("direct")
        if report["direct"]:
            report["selected"] = "direct"
            return "direct", report
        raise CollectorError("X 直连测试失败。请把 SOCIAL_PROXY_MODE 配置为 system 或 explicit。")
    if mode == "system":
        report["system"] = await probe("system")
        if report["system"]:
            report["selected"] = "system"
            return "system", report
        raise CollectorError("系统代理路径无法连接 X；请检查系统代理，或改用 explicit。")
    if mode == "explicit":
        if not has_proxy:
            raise CollectorError(
                "SOCIAL_PROXY_MODE=explicit，但未配置 SOCIAL_PROXY_URL；当前不能使用 X 采集。"
            )
        report["explicit"] = await probe("explicit")
        if report["explicit"]:
            report["selected"] = "explicit"
            return "explicit", report
        raise CollectorError("已配置代理，但通过该代理仍无法连接 X；请检查代理服务和线路。")
    raise CollectorError("SOCIAL_PROXY_MODE 必须是 auto、direct、system 或 explicit")


EXTRACT_POSTS_JS = r"""
() => Array.from(document.querySelectorAll('article[data-testid="tweet"]')).map(article => {
  const statusLink = Array.from(article.querySelectorAll('a[href*="/status/"]'))
    .map(a => a.getAttribute('href') || '')
    .find(href => /\/status\/\d+/.test(href));
  if (!statusLink) return null;
  const match = statusLink.match(/^\/([^/]+)\/status\/(\d+)/);
  if (!match) return null;
  const metric = name => article.querySelector(`[data-testid="${name}"]`)?.innerText || '';
  const time = article.querySelector('time');
  const textNode = article.querySelector('[data-testid="tweetText"]');
  const user = article.querySelector('[data-testid="User-Name"]');
  const userLines = (user?.innerText || '').split('\n').filter(Boolean);
  const images = Array.from(article.querySelectorAll('img[src*="pbs.twimg.com/media"]'))
    .map(img => img.src).filter(Boolean);
  return {
    post_id: match[2],
    author_handle: `@${match[1]}`,
    author_name: userLines.find(line => !line.startsWith('@')) || '',
    text: textNode?.innerText || '',
    original_language: textNode?.getAttribute('lang') || '',
    browser_translated: document.documentElement.classList.contains('translated-ltr') ||
      document.documentElement.classList.contains('translated-rtl'),
    published_at: time?.getAttribute('datetime') || '',
    reply_count: metric('reply'),
    repost_count: metric('retweet'),
    like_count: metric('like'),
    view_count: article.querySelector('a[href$="/analytics"]')?.innerText || '',
    media_urls: images,
    url: `https://x.com${statusLink.split('?')[0]}`,
  };
}).filter(Boolean)
"""


def normalize_post(post: dict[str, Any], keyword: str) -> dict[str, Any] | None:
    post_id = str(post.get("post_id") or "")
    url = str(post.get("url") or "")
    parsed = urlsplit(url)
    if not re.fullmatch(r"\d{1,30}", post_id):
        return None
    if parsed.scheme != "https" or parsed.hostname not in {"x.com", "www.x.com"}:
        return None
    media_urls = []
    for value in post.get("media_urls") or []:
        candidate = str(value)
        media = urlsplit(candidate)
        if media.scheme == "https" and media.hostname == "pbs.twimg.com" and "/media/" in media.path:
            media_urls.append(candidate)
    original_text = str(post.get("text") or "")
    dom_language = normalize_language_code(str(post.get("original_language") or ""))
    original_language = dom_language or detect_language(original_text)
    is_chinese = original_language.startswith("zh")
    return {
        "platform": "x",
        "post_id": post_id,
        "author_handle": str(post.get("author_handle") or ""),
        "author_name": str(post.get("author_name") or ""),
        "text": original_text,
        "original_text": original_text,
        "original_language": original_language,
        "language_detection": "x-dom" if dom_language else "local-heuristic",
        "zh_translation": original_text if is_chinese else "",
        "translation_method": "original-is-chinese" if is_chinese else "pending",
        "published_at": str(post.get("published_at") or ""),
        "reply_count": parse_count(post.get("reply_count")),
        "repost_count": parse_count(post.get("repost_count")),
        "like_count": parse_count(post.get("like_count")),
        "view_count": parse_count(post.get("view_count")),
        "media_urls": list(dict.fromkeys(media_urls)),
        "url": url,
        "source_query": keyword,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def normalize_language_code(value: str) -> str:
    language = value.strip().lower().replace("_", "-")
    if not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", language):
        return ""
    return language


def detect_language(text: str) -> str:
    letters = [character for character in text if character.isalpha()]
    if not letters:
        return "und"
    cjk = sum("\u3400" <= character <= "\u9fff" for character in letters)
    kana = sum("\u3040" <= character <= "\u30ff" for character in letters)
    hangul = sum("\uac00" <= character <= "\ud7af" for character in letters)
    latin = sum(character.isascii() and character.isalpha() for character in letters)
    if kana:
        return "ja"
    if hangul:
        return "ko"
    if cjk / len(letters) >= 0.2:
        return "zh"
    if latin / len(letters) >= 0.6:
        return "en"
    return "und"


def extract_openai_output(payload: Mapping[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    for output in payload.get("output") or []:
        if not isinstance(output, Mapping):
            continue
        for content in output.get("content") or []:
            if isinstance(content, Mapping) and content.get("type") == "output_text":
                value = content.get("text")
                if isinstance(value, str) and value.strip():
                    return value.strip()
    raise CollectorError("翻译服务没有返回可读取的文本。")


def translate_items_zh(
    items: list[dict[str, Any]], config: Mapping[str, str]
) -> None:
    pending = [item for item in items if item.get("translation_method") == "pending"]
    if not pending:
        return
    api_key = config.get("OPENAI_API_KEY", "").strip()
    model = config.get("OPENAI_TEXT_MODEL", "").strip()
    if not api_key or not model:
        raise CollectorError(
            "--translate-zh 需要在本机 .env.local 配置 OPENAI_API_KEY 和 OPENAI_TEXT_MODEL。"
        )
    base_url = config.get("OPENAI_BASE_URL", "").strip() or "https://api.openai.com"
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise CollectorError("OPENAI_BASE_URL 必须是 HTTPS 地址。")
    source = [
        {
            "post_id": item["post_id"],
            "language": item["original_language"],
            "text": item["original_text"],
        }
        for item in pending
    ]
    instruction = (
        "Translate each X post into faithful Simplified Chinese. Preserve names, URLs, "
        "hashtags, line breaks, and meaning. Return only a JSON array of objects with "
        "post_id and zh_translation; do not add commentary. Input: "
        + json.dumps(source, ensure_ascii=False)
    )
    body = json.dumps({"model": model, "input": instruction}).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/v1/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise CollectorError("X 中文翻译请求失败；原文仍保留，未写入不完整结果。") from exc
    try:
        translated = json.loads(extract_openai_output(response_payload))
    except json.JSONDecodeError as exc:
        raise CollectorError("翻译服务返回的结果不是有效 JSON；原文仍保留。") from exc
    mapping = {
        str(row.get("post_id")): str(row.get("zh_translation") or "").strip()
        for row in translated
        if isinstance(row, Mapping)
    }
    if any(not mapping.get(str(item["post_id"])) for item in pending):
        raise CollectorError("部分外文帖子没有中文翻译；为避免半成品，本轮未落盘。")
    for item in pending:
        item["zh_translation"] = mapping[str(item["post_id"])]
        item["translation_method"] = f"openai:{model}"


def original_media_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.hostname != "pbs.twimg.com" or "/media/" not in parsed.path:
        return url
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["name"] = "orig"
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


async def is_logged_in(context: Any) -> bool:
    cookies = await context.cookies("https://x.com")
    return any(cookie.get("name") == "auth_token" and cookie.get("value") for cookie in cookies)


async def wait_for_login(context: Any, page: Any, timeout_seconds: int) -> None:
    if await is_logged_in(context):
        return
    try:
        await page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded", timeout=60_000)
    except Exception as exc:
        raise CollectorError(
            "浏览器无法通过所选网络路径打开 X 登录页；请重新运行 --preflight 并检查代理继承。"
        ) from exc
    if timeout_seconds <= 0:
        if timeout_seconds == 0:
            raise CollectorError("X 尚未登录。请运行 --login-only，在可见窗口中由用户本人完成登录。")
        log("请在可见浏览器中手动登录 X；当前为无限等待，不会因超时关闭。")
        while True:
            await page.wait_for_timeout(5_000)
            if await is_logged_in(context):
                return
    log("请在可见浏览器中手动登录 X；脚本不会读取用户名或密码。")
    for _ in range(0, timeout_seconds, 5):
        await page.wait_for_timeout(5_000)
        if await is_logged_in(context):
            return
    raise CollectorError("等待 X 手动登录超时；登录 profile 已保留，可关闭窗口后重试。")


async def collect_page(page: Any, query: str, limit: int, scrolls: int, latest: bool) -> list[dict[str, Any]]:
    mode = "live" if latest else "top"
    url = f"https://x.com/search?q={quote(query)}&src=typed_query&f={mode}"
    await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    try:
        await page.wait_for_selector('article[data-testid="tweet"]', timeout=30_000)
    except Exception as exc:
        body = await page.locator("body").inner_text(timeout=5_000)
        if "rate limit" in body.lower() or "速率" in body:
            raise CollectorError("X 返回速率限制页面，已停止且不会自动重试。") from exc
        raise CollectorError("搜索页没有出现帖子；可能是登录失效、无精确结果或页面结构变化。") from exc
    captured: dict[str, dict[str, Any]] = {}
    stagnant = 0
    for _ in range(scrolls + 1):
        before = len(captured)
        for post in await page.evaluate(EXTRACT_POSTS_JS):
            captured[str(post["post_id"])] = post
        if len(captured) >= limit:
            break
        stagnant = stagnant + 1 if len(captured) == before else 0
        if stagnant >= 3:
            break
        await page.mouse.wheel(0, 2_400)
        await page.wait_for_timeout(2_500)
    return list(captured.values())


async def download_media(context: Any, items: list[dict[str, Any]], output: Path) -> tuple[int, int]:
    media_dir = output.parent / f"{output.stem}-media"
    media_dir.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    failed = 0
    for item in items:
        local_paths: list[str] = []
        for index, raw_url in enumerate(item["media_urls"], start=1):
            url = original_media_url(raw_url)
            suffix = Path(urlsplit(url).path).suffix or ".jpg"
            target = media_dir / f"{item['post_id']}-{index}{suffix}"
            try:
                response = await context.request.get(url, timeout=20_000, fail_on_status_code=False)
                if response.ok:
                    body = await response.body()
                    if len(body) > MAX_MEDIA_BYTES:
                        failed += 1
                        continue
                    target.write_bytes(body)
                    local_paths.append(str(target.relative_to(output.parent)).replace("\\", "/"))
                    downloaded += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        item["local_media_paths"] = local_paths
    return downloaded, failed


def evidence_payload(keyword: str, query: str, route: str, latest: bool, items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "platform": "x",
        "access_mode": "authorized read-only browser session",
        "keyword": keyword,
        "query": query,
        "result_mode": "latest" if latest else "top",
        "network_route": route,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": items,
    }


async def run(args: argparse.Namespace) -> int:
    from playwright.async_api import async_playwright

    config = resolved_config(ROOT, os.environ)
    browser_family, browser_path = resolve_browser(config)
    profile = expand_path(config.get("X_BROWSER_PROFILE_DIR", DEFAULT_PROFILE))
    cdp_port = validate_cdp_port(config.get("X_BROWSER_CDP_PORT", "19222"))
    proxy_url = config.get("SOCIAL_PROXY_URL", "").strip()
    mode = args.network_mode or config.get("SOCIAL_PROXY_MODE", "auto").strip().lower()
    bypass = validate_loopback_bypass(
        config.get("SOCIAL_PROXY_BYPASS", "127.0.0.1,localhost,::1")
    )
    proxy = playwright_proxy(proxy_url, bypass) if proxy_url else None
    probe_url = validate_probe_url(config.get("X_CONNECTIVITY_URL", DEFAULT_PROBE_URL))
    inherited_proxy_url = system_proxy_url(probe_url) if mode in {"auto", "system"} else ""
    inherited_proxy = (
        playwright_proxy(inherited_proxy_url, bypass) if inherited_proxy_url else None
    )

    async with async_playwright() as playwright:
        async def probe(route: str) -> bool:
            route_proxy = (
                proxy if route == "explicit" else inherited_proxy if route == "system" else None
            )
            return await probe_connection(playwright, probe_url, route_proxy, args.preflight_timeout)

        route, report = await resolve_route(mode, bool(proxy_url), probe)
        if args.preflight:
            print(json.dumps({"status": "ready", **report}, ensure_ascii=False, indent=2))
            return 0

        ensure_external_profile(profile, ROOT)
        profile.parent.mkdir(parents=True, exist_ok=True)
        if args.login_only:
            # system 模式不注入 --proxy-server：普通 Chrome/Edge 应完整继承
            # Windows 系统代理、PAC 或代理客户端的按域名规则。
            login_proxy = proxy if route == "explicit" else None
            launch_detached_login(
                browser_path, profile, route, login_proxy, bypass, cdp_port
            )
            log(
                f"已用 {browser_family} 打开 X 登录窗口；浏览器独立运行，不会被脚本超时关闭。"
                f"登录完成后可通过本机端口 {cdp_port} 做只读连接验证。"
            )
            return 0
        if args.cdp_status:
            _, attached_context = await attach_cdp(playwright, cdp_port)
            pages = attached_context.pages
            logged_in = await is_logged_in(attached_context)
            print(
                json.dumps(
                    {
                        "status": "connected",
                        "endpoint": f"127.0.0.1:{cdp_port}",
                        "logged_in": logged_in,
                        "page_count": len(pages),
                        "x_page_open": any(
                            urlsplit(page.url).hostname in {"x.com", "www.x.com"}
                            for page in pages
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        attached = args.attach
        if attached:
            _, context = await attach_cdp(playwright, cdp_port)
        else:
            context = None
        launch_options: dict[str, Any] = {
            "user_data_dir": str(profile),
            "executable_path": str(browser_path),
            "headless": args.headless,
            "viewport": {"width": 1440, "height": 900},
            "args": ["--disable-features=Translate,TranslateUI"],
        }
        if route == "direct":
            launch_options["args"].append("--no-proxy-server")
        if route == "explicit" and proxy:
            launch_options["proxy"] = proxy
        if route == "system" and inherited_proxy:
            launch_options["proxy"] = inherited_proxy
        if context is None:
            try:
                context = await playwright.chromium.launch_persistent_context(**launch_options)
            except Exception as exc:
                message = str(exc).lower()
                if "processsingleton" in message or "exitcode=21" in message or "target page" in message:
                    raise CollectorError("X 专用浏览器 profile 正被占用；请改用 --attach，或关闭对应专用浏览器窗口后重试。") from exc
                raise CollectorError("无法启动 X 专用浏览器；请检查浏览器路径、profile 权限和代理配置。") from exc
        try:
            page = context.pages[0] if context.pages else await context.new_page()
            await wait_for_login(context, page, 0)
            query = build_search_query(args.keyword, args.exact, args.exclude)
            try:
                raw = await collect_page(page, query, args.limit, args.scrolls, args.latest)
            except CollectorError:
                raise
            except Exception as exc:
                raise CollectorError("X 页面读取失败；已停止且不会自动重试。请检查页面结构或稍后人工确认。") from exc
            strict = strict_filter(raw, args.keyword, args.exact, args.exclude)
            if any(post.get("browser_translated") for post in strict):
                raise CollectorError(
                    "检测到浏览器已翻译 X 页面，无法保证原文完整；请关闭专用浏览器并用 --login-only 重新启动后再采集。"
                )
            items = [row for post in strict if (row := normalize_post(post, args.keyword))]
            items = items[: args.limit]
            if args.translate_zh:
                translate_items_zh(items, config)
            if args.download_media and not args.out:
                raise CollectorError("下载媒体必须同时提供 --out，以便保存图片映射。")
            output = Path(args.out).resolve() if args.out else None
            downloaded = failed = 0
            if args.download_media and output:
                downloaded, failed = await download_media(context, items, output)
            payload = evidence_payload(args.keyword, query, route, args.latest, items)
            if output:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                log(f"X 只读采集完成：{len(items)} 条 -> {output}")
            else:
                log(f"X 只读采集完成：{len(items)} 条；用户未选择保存，本轮不落盘。")
            if args.download_media:
                log(f"媒体下载：成功 {downloaded}，失败 {failed}")
            return 0
        finally:
            if not attached:
                await context.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Growth Lab X browser-first 只读采集器")
    parser.add_argument("keyword", nargs="?", help="搜索关键词")
    parser.add_argument("--preflight", action="store_true", help="仅检查直连/代理，不登录或采集")
    parser.add_argument("--network-mode", choices=("auto", "direct", "system", "explicit"), help="覆盖 SOCIAL_PROXY_MODE")
    parser.add_argument("--preflight-timeout", type=int, default=8, help="单条线路检测超时秒数")
    parser.add_argument("--login-only", action="store_true", help="打开可见浏览器，仅完成人工登录")
    parser.add_argument("--cdp-status", action="store_true", help="只读检查已打开的 X 专用浏览器连接与登录状态")
    parser.add_argument("--attach", action="store_true", help="连接已打开的 X 专用浏览器执行只读采集，不关闭窗口")
    parser.add_argument("--limit", type=int, default=25, help="期望条数，默认 25，硬上限 50")
    parser.add_argument("--scrolls", type=int, default=6, help="最多滚动次数，默认 6，硬上限 20")
    parser.add_argument("--latest", action="store_true", help="使用 Latest 而不是 Top")
    parser.add_argument("--exact", action="store_true", help="把关键词作为完整短语，并在落盘前严格复核")
    parser.add_argument("--exclude", action="append", default=[], help="排除含该短语的帖子，可重复")
    parser.add_argument("--out", help="选择保存时提供 JSON 路径；省略则不落盘")
    parser.add_argument("--download-media", action="store_true", help="下载帖子图片到输出文件旁的独立目录")
    parser.add_argument("--translate-zh", action="store_true", help="把外文原文批量翻译为中文并同时保存；会调用已配置的文本模型")
    parser.add_argument("--headless", action="store_true", help="无界面运行；首次登录不要使用")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.preflight and not args.login_only and not args.cdp_status and not args.keyword:
        raise CollectorError("请提供关键词，或使用 --preflight / --login-only / --cdp-status。")
    if not 1 <= args.limit <= 50:
        raise CollectorError("--limit 必须在 1 到 50 之间。")
    if not 0 <= args.scrolls <= 20:
        raise CollectorError("--scrolls 必须在 0 到 20 之间。")
    if not 2 <= args.preflight_timeout <= 30:
        raise CollectorError("--preflight-timeout 必须在 2 到 30 秒之间。")
    return asyncio.run(run(args))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CollectorError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
    except KeyboardInterrupt:
        print("已由用户中断。", file=sys.stderr)
        raise SystemExit(130)
    except Exception:
        print("错误：X Collector 遇到未预期错误；已停止，未自动重试。", file=sys.stderr)
        raise SystemExit(1)
