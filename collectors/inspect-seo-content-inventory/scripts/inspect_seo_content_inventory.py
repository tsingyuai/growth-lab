#!/usr/bin/env python3
"""Inventory public SEO content without making SEO action decisions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


USER_AGENT = "GrowthLabContentInventory/1.0"
SKIP_TEXT_TAGS = {"script", "style", "noscript", "svg", "template"}
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.I,
)
LONG_ID_RE = re.compile(r"^(?=.{16,}$)(?=.*[a-z])(?=.*\d)[a-z0-9_-]+$", re.I)
CJK_RUN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")
WORD_RE = re.compile(r"[a-z0-9]{2,}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_url(value: str) -> str:
    value = value.strip()
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        return value
    host = (parsed.hostname or "").lower()
    port = parsed.port
    if port and not ((parsed.scheme == "http" and port == 80) or (parsed.scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = parsed.path or "/"
    return urllib.parse.urlunsplit((parsed.scheme.lower(), host, path, parsed.query, ""))


def origin(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    host = parsed.hostname.lower()
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return f"{parsed.scheme.lower()}://{host}"


def path_pattern(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    segments: list[str] = []
    for segment in parsed.path.split("/"):
        decoded = urllib.parse.unquote(segment)
        if UUID_RE.fullmatch(decoded):
            segments.append("{uuid}")
        elif decoded.isdigit() and decoded:
            segments.append("{id}")
        elif LONG_ID_RE.fullmatch(decoded):
            segments.append("{id}")
        else:
            segments.append(segment)
    path = "/".join(segments) or "/"
    if parsed.query:
        keys = sorted({key for key, _ in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)})
        if keys:
            path += "?" + "&".join(f"{key}={{value}}" for key in keys)
    return path


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def content_tokens(value: str) -> set[str]:
    value = compact_text(value).lower()
    tokens = set(WORD_RE.findall(value))
    for run in CJK_RUN_RE.findall(value):
        if len(run) == 1:
            tokens.add(run)
        else:
            tokens.update(run[index : index + 2] for index in range(len(run) - 1))
    return tokens


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


class PageParser(HTMLParser):
    def __init__(self, page_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.headings: list[dict[str, str]] = []
        self.links: list[str] = []
        self.description = ""
        self.robots = ""
        self.canonical = ""
        self.lang = ""
        self.json_ld_parts: list[str] = []
        self._title_depth = 0
        self._heading_tag = ""
        self._heading_parts: list[str] = []
        self._skip_depth = 0
        self._json_ld_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag == "html":
            self.lang = values.get("lang", "")
        if tag in SKIP_TEXT_TAGS:
            self._skip_depth += 1
        if tag == "title":
            self._title_depth += 1
        if tag in {"h1", "h2", "h3"}:
            self._heading_tag = tag
            self._heading_parts = []
        if tag == "meta":
            name = (values.get("name") or values.get("property") or "").lower()
            content = values.get("content", "")
            if name in {"description", "og:description"} and not self.description:
                self.description = compact_text(content)
            if name in {"robots", "googlebot", "bingbot"} and not self.robots:
                self.robots = compact_text(content).lower()
        if tag == "link" and "canonical" in values.get("rel", "").lower().split():
            href = values.get("href", "")
            if href and not self.canonical:
                self.canonical = normalize_url(urllib.parse.urljoin(self.page_url, href))
        if tag == "a":
            href = values.get("href", "")
            if href and not href.lower().startswith(("javascript:", "mailto:", "tel:")):
                joined = urllib.parse.urljoin(self.page_url, href)
                if urllib.parse.urlsplit(joined).scheme in {"http", "https"}:
                    self.links.append(normalize_url(joined))
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._json_ld_depth += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title" and self._title_depth:
            self._title_depth -= 1
        if tag == self._heading_tag:
            text = compact_text(" ".join(self._heading_parts))
            if text:
                self.headings.append({"level": tag, "text": text})
            self._heading_tag = ""
            self._heading_parts = []
        if tag == "script" and self._json_ld_depth:
            self._json_ld_depth -= 1
        if tag in SKIP_TEXT_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        text = compact_text(data)
        if not text:
            return
        if self._title_depth:
            self.title_parts.append(text)
        if self._heading_tag:
            self._heading_parts.append(text)
        if self._json_ld_depth:
            self.json_ld_parts.append(data)
        if not self._skip_depth:
            self.text_parts.append(text)

    def result(self) -> dict[str, Any]:
        text = compact_text(" ".join(self.text_parts))
        json_ld_types: set[str] = set()
        for part in self.json_ld_parts:
            try:
                collect_json_ld_types(json.loads(part), json_ld_types)
            except (json.JSONDecodeError, TypeError):
                continue
        return {
            "title": compact_text(" ".join(self.title_parts)),
            "meta_description": self.description,
            "canonical": self.canonical,
            "robots": self.robots,
            "lang": self.lang,
            "headings": self.headings,
            "h1": [item["text"] for item in self.headings if item["level"] == "h1"],
            "visible_text": text,
            "visible_text_chars": len(text),
            "links": list(dict.fromkeys(self.links)),
            "json_ld_types": sorted(json_ld_types),
        }


def collect_json_ld_types(value: Any, output: set[str]) -> None:
    if isinstance(value, dict):
        item_type = value.get("@type")
        if isinstance(item_type, str):
            output.add(item_type)
        elif isinstance(item_type, list):
            output.update(str(item) for item in item_type)
        for child in value.values():
            collect_json_ld_types(child, output)
    elif isinstance(value, list):
        for child in value:
            collect_json_ld_types(child, output)


def read_source(source: str, timeout: float, max_bytes: int) -> tuple[str, str]:
    parsed = urllib.parse.urlsplit(source)
    if parsed.scheme in {"http", "https"}:
        request = urllib.request.Request(source, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise ValueError(f"source exceeds {max_bytes} bytes: {source}")
            charset = response.headers.get_content_charset() or "utf-8"
            try:
                return raw.decode(charset), response.geturl()
            except (LookupError, UnicodeDecodeError):
                return raw.decode("utf-8", errors="replace"), response.geturl()
    path = Path(source).resolve()
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raise ValueError(f"source exceeds {max_bytes} bytes: {path}")
    return raw.decode("utf-8-sig"), str(path)


def resolve_sitemap_location(parent: str, location: str) -> str:
    if urllib.parse.urlsplit(parent).scheme in {"http", "https"}:
        return urllib.parse.urljoin(parent, location)
    child = Path(location)
    return str(child if child.is_absolute() else (Path(parent).parent / child).resolve())


def read_sitemaps(
    sources: list[str],
    timeout: float,
    max_sitemaps: int,
    max_urls: int,
    allowed_origin: str,
) -> tuple[list[str], dict[str, str], list[str]]:
    queue = deque(sources)
    seen_sitemaps: set[str] = set()
    urls: list[str] = []
    lastmod: dict[str, str] = {}
    warnings: list[str] = []
    while queue and len(seen_sitemaps) < max_sitemaps and len(urls) < max_urls:
        source = queue.popleft()
        if source in seen_sitemaps:
            continue
        seen_sitemaps.add(source)
        try:
            text, resolved_source = read_source(source, timeout, 10_000_000)
            root = ET.fromstring(text)
        except (OSError, ValueError, ET.ParseError, urllib.error.URLError) as error:
            warnings.append(f"Could not read sitemap {source}: {error}")
            continue
        root_name = root.tag.rsplit("}", 1)[-1].lower()
        if root_name == "sitemapindex":
            for item in root:
                loc = next((child.text or "" for child in item if child.tag.rsplit("}", 1)[-1] == "loc"), "").strip()
                if not loc:
                    continue
                nested = resolve_sitemap_location(resolved_source, loc)
                if allowed_origin and origin(nested) and origin(nested) != allowed_origin:
                    warnings.append(f"Skipped off-origin sitemap: {nested}")
                    continue
                queue.append(nested)
        elif root_name == "urlset":
            for item in root:
                fields = {child.tag.rsplit("}", 1)[-1]: (child.text or "").strip() for child in item}
                value = normalize_url(fields.get("loc", ""))
                if not value:
                    continue
                if allowed_origin and origin(value) != allowed_origin:
                    warnings.append(f"Skipped off-origin URL: {value}")
                    continue
                if value not in lastmod:
                    urls.append(value)
                if fields.get("lastmod"):
                    lastmod[value] = fields["lastmod"]
                if len(urls) >= max_urls:
                    break
        else:
            warnings.append(f"Unsupported sitemap root {root_name}: {source}")
    if queue:
        warnings.append("Sitemap traversal stopped at configured sitemap or URL limit")
    return list(dict.fromkeys(urls)), lastmod, warnings


def read_url_lists(paths: list[str]) -> list[str]:
    urls: list[str] = []
    for value in paths:
        path = Path(value)
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                fields = reader.fieldnames or []
                field = next((item for item in fields if item.lower() in {"url", "page", "loc", "canonical"}), fields[0] if fields else "")
                for row in reader:
                    if field and row.get(field):
                        urls.append(normalize_url(row[field]))
        else:
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(normalize_url(line))
    return list(dict.fromkeys(urls))


def select_pattern_samples(urls: list[str], max_pages: int, samples_per_pattern: int) -> list[str]:
    groups: dict[str, list[str]] = defaultdict(list)
    order: list[str] = []
    for value in urls:
        pattern = path_pattern(value)
        if pattern not in groups:
            order.append(pattern)
        groups[pattern].append(value)
    selected: list[str] = []
    for index in range(samples_per_pattern):
        for pattern in order:
            if index < len(groups[pattern]):
                selected.append(groups[pattern][index])
                if len(selected) >= max_pages:
                    return selected
    return selected


def build_robot_parser(base_origin: str, timeout: float, warnings: list[str]) -> urllib.robotparser.RobotFileParser | None:
    if not base_origin:
        return None
    robots_url = urllib.parse.urljoin(base_origin + "/", "robots.txt")
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        text, _ = read_source(robots_url, timeout, 1_000_000)
        parser.parse(text.splitlines())
        return parser
    except (OSError, ValueError, urllib.error.URLError) as error:
        warnings.append(f"Could not read robots.txt; page inspection continued within the configured cap: {error}")
        return None


def inspect_http_page(
    page_url: str,
    timeout: float,
    max_html_bytes: int,
    base_origin: str,
    robot_parser: urllib.robotparser.RobotFileParser | None,
) -> dict[str, Any]:
    record: dict[str, Any] = {"url": page_url, "source": "http", "path_pattern": path_pattern(page_url), "flags": []}
    if robot_parser and not robot_parser.can_fetch(USER_AGENT, page_url):
        record.update({"skipped": "robots_disallowed", "status": None})
        return record
    request = urllib.request.Request(page_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(max_html_bytes + 1)
            content_type = response.headers.get_content_type()
            charset = response.headers.get_content_charset() or "utf-8"
            record.update({"status": response.status, "final_url": normalize_url(response.geturl()), "content_type": content_type})
            if len(raw) > max_html_bytes:
                record["flags"].append("html_truncated")
                raw = raw[:max_html_bytes]
            if content_type not in {"text/html", "application/xhtml+xml"}:
                record["flags"].append("non_html")
                return record
            try:
                html = raw.decode(charset)
            except (LookupError, UnicodeDecodeError):
                html = raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        record.update({"status": error.code, "error": str(error)})
        record["flags"].append("http_error")
        return record
    except (OSError, urllib.error.URLError) as error:
        record.update({"status": None, "error": str(error)})
        record["flags"].append("request_failed")
        return record
    parser = PageParser(record.get("final_url") or page_url)
    parser.feed(html)
    parsed = parser.result()
    visible_text = parsed.pop("visible_text")
    links = parsed.pop("links")
    internal = [link for link in links if origin(link) == base_origin]
    record.update(parsed)
    record["internal_links"] = internal[:200]
    record["internal_link_count"] = len(internal)
    record["external_link_count"] = len(links) - len(internal)
    record["content_hash"] = hashlib.sha256(visible_text.encode("utf-8")).hexdigest() if visible_text else ""
    record["similarity_text"] = compact_text(" ".join([record.get("title", ""), " ".join(record.get("h1", [])), record.get("meta_description", ""), " ".join(item["text"] for item in record.get("headings", []))]))
    add_page_flags(record, page_url, base_origin)
    return record


def inspect_snapshot(path: Path, snapshot_root: Path, base_url: str) -> dict[str, Any]:
    relative = path.relative_to(snapshot_root).as_posix()
    if relative.endswith("/index.html"):
        route = relative[: -len("index.html")]
    elif relative == "index.html":
        route = ""
    else:
        route = relative[:-5] if relative.endswith(".html") else relative
    page_url = normalize_url(urllib.parse.urljoin(base_url.rstrip("/") + "/", route)) if base_url else str(path.resolve())
    html = path.read_text(encoding="utf-8-sig")
    parser = PageParser(page_url)
    parser.feed(html)
    parsed = parser.result()
    visible_text = parsed.pop("visible_text")
    links = parsed.pop("links")
    base_origin = origin(base_url)
    internal = [link for link in links if not base_origin or origin(link) == base_origin]
    record: dict[str, Any] = {
        "url": page_url,
        "source": str(path.resolve()),
        "path_pattern": path_pattern(page_url),
        "status": 200,
        "final_url": page_url,
        "content_type": "text/html",
        "flags": [],
        **parsed,
        "internal_links": internal[:200],
        "internal_link_count": len(internal),
        "external_link_count": len(links) - len(internal),
        "content_hash": hashlib.sha256(visible_text.encode("utf-8")).hexdigest() if visible_text else "",
    }
    record["similarity_text"] = compact_text(" ".join([record.get("title", ""), " ".join(record.get("h1", [])), record.get("meta_description", ""), " ".join(item["text"] for item in record.get("headings", []))]))
    add_page_flags(record, page_url, base_origin)
    return record


def add_page_flags(record: dict[str, Any], requested_url: str, base_origin: str) -> None:
    flags = record["flags"]
    if record.get("final_url") and normalize_url(record["final_url"]) != normalize_url(requested_url):
        flags.append("redirected")
    if not record.get("title"):
        flags.append("missing_title")
    if not record.get("meta_description"):
        flags.append("missing_meta_description")
    h1 = record.get("h1", [])
    if not h1:
        flags.append("missing_h1")
    elif len(h1) > 1:
        flags.append("multiple_h1")
    if not record.get("canonical"):
        flags.append("missing_canonical")
    else:
        canonical = record["canonical"]
        if base_origin and origin(canonical) != base_origin:
            flags.append("off_origin_canonical")
        if normalize_url(canonical) != normalize_url(record.get("final_url") or requested_url):
            flags.append("canonical_points_elsewhere")
    if "noindex" in record.get("robots", ""):
        flags.append("noindex")
    if record.get("visible_text_chars", 0) < 300:
        flags.append("low_static_text")


def build_groups(items: Iterable[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for item in items:
        value = compact_text(str(item.get(field, "")))
        if value:
            groups[value].append(item["url"])
    return [
        {"value": value, "count": len(urls), "urls": urls}
        for value, urls in groups.items()
        if len(urls) > 1
    ]


def analyze_pages(pages: list[dict[str, Any]], base_url: str, similarity_threshold: float) -> dict[str, Any]:
    inspectable = [page for page in pages if page.get("content_type") == "text/html" and not page.get("skipped")]
    duplicate_titles = build_groups(inspectable, "title")
    duplicate_canonicals = build_groups(inspectable, "canonical")
    exact_content_duplicates = build_groups(inspectable, "content_hash")
    similarities: list[dict[str, Any]] = []
    token_sets = [(page, content_tokens(page.get("similarity_text", ""))) for page in inspectable]
    for index, (left, left_tokens) in enumerate(token_sets):
        if len(left_tokens) < 3:
            continue
        for right, right_tokens in token_sets[index + 1 :]:
            if len(right_tokens) < 3:
                continue
            score = jaccard(left_tokens, right_tokens)
            if score >= similarity_threshold:
                similarities.append({"left": left["url"], "right": right["url"], "score": round(score, 3)})
    similarities.sort(key=lambda item: item["score"], reverse=True)
    known_urls = {normalize_url(page["url"]) for page in inspectable}
    incoming: Counter[str] = Counter()
    for page in inspectable:
        for link in page.get("internal_links", []):
            normalized = normalize_url(link)
            if normalized in known_urls:
                incoming[normalized] += 1
    home = normalize_url(base_url) if base_url else ""
    orphan_candidates = [
        page["url"]
        for page in inspectable
        if normalize_url(page["url"]) != home and incoming[normalize_url(page["url"])] == 0
    ]
    return {
        "status_counts": dict(Counter(str(page.get("status")) for page in pages)),
        "flag_counts": dict(Counter(flag for page in pages for flag in page.get("flags", []))),
        "duplicate_titles": duplicate_titles,
        "duplicate_canonicals": duplicate_canonicals,
        "exact_content_duplicates": exact_content_duplicates,
        "similarity_candidates": similarities[:200],
        "orphan_candidates": orphan_candidates,
    }


def pattern_summary(urls: list[str]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for value in urls:
        groups[path_pattern(value)].append(value)
    return sorted(
        (
            {"pattern": pattern, "count": len(values), "sample_urls": values[:3]}
            for pattern, values in groups.items()
        ),
        key=lambda item: (-item["count"], item["pattern"]),
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sitemap", action="append", default=[], help="Public URL or local Sitemap XML; repeatable")
    parser.add_argument("--url-list", action="append", default=[], help="Text or CSV URL list; repeatable")
    parser.add_argument("--snapshot-dir", action="append", default=[], help="Directory containing static .html snapshots; repeatable")
    parser.add_argument("--base-url", help="Canonical site origin used to restrict public inspection and map snapshots")
    parser.add_argument("--include-regex", action="append", default=[], help="Inspect only discovered URLs matching at least one regex; repeatable")
    parser.add_argument("--exclude-regex", action="append", default=[], help="Do not inspect discovered URLs matching a regex; repeatable")
    parser.add_argument("--out", type=Path, help="Write JSON output to this path; stdout if omitted")
    parser.add_argument("--max-urls", type=int, default=5000, help="Maximum URLs discovered from Sitemaps and URL lists")
    parser.add_argument("--max-pages", type=int, default=200, help="Maximum public or snapshot pages inspected")
    parser.add_argument("--max-sitemaps", type=int, default=100, help="Maximum nested Sitemap files read")
    parser.add_argument("--samples-per-pattern", type=int, default=5, help="Maximum public pages sampled from each normalized path pattern")
    parser.add_argument("--similarity-threshold", type=float, default=0.72, help="Jaccard threshold from 0 to 1 for similarity candidates")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds")
    parser.add_argument("--delay-ms", type=int, default=150, help="Delay between public page requests")
    parser.add_argument("--max-html-bytes", type=int, default=2_000_000, help="Maximum bytes read from one HTML response")
    parser.add_argument("--include-discovered-urls", action="store_true", help="Include every discovered URL in output")
    args = parser.parse_args(argv)
    if not (args.sitemap or args.url_list or args.snapshot_dir):
        parser.error("provide at least one --sitemap, --url-list, or --snapshot-dir")
    if args.max_urls < 1 or args.max_pages < 1 or args.max_sitemaps < 1 or args.samples_per_pattern < 1:
        parser.error("limits must be positive")
    if not 0 <= args.similarity_threshold <= 1:
        parser.error("--similarity-threshold must be between 0 and 1")
    for pattern in [*args.include_regex, *args.exclude_regex]:
        try:
            re.compile(pattern)
        except re.error as error:
            parser.error(f"invalid URL regex {pattern!r}: {error}")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    base_url = normalize_url(args.base_url) if args.base_url else ""
    base_origin = origin(base_url)
    if not base_origin:
        for source in [*args.sitemap, *args.url_list]:
            candidate = source if urllib.parse.urlsplit(source).scheme in {"http", "https"} else ""
            if candidate:
                base_origin = origin(candidate)
                base_url = base_origin + "/"
                break
    warnings: list[str] = []
    discovered: list[str] = []
    lastmod: dict[str, str] = {}
    if args.sitemap:
        sitemap_urls, sitemap_lastmod, sitemap_warnings = read_sitemaps(
            args.sitemap, args.timeout, args.max_sitemaps, args.max_urls, base_origin
        )
        discovered.extend(sitemap_urls)
        lastmod.update(sitemap_lastmod)
        warnings.extend(sitemap_warnings)
    if args.url_list:
        for value in read_url_lists(args.url_list):
            if base_origin and origin(value) != base_origin:
                warnings.append(f"Skipped off-origin URL: {value}")
                continue
            discovered.append(value)
    discovered = list(dict.fromkeys(discovered))[: args.max_urls]
    if not base_origin and discovered:
        base_origin = origin(discovered[0])
        base_url = base_origin + "/" if base_origin else ""
        if base_origin:
            filtered: list[str] = []
            for value in discovered:
                if origin(value) == base_origin:
                    filtered.append(value)
                else:
                    warnings.append(f"Skipped off-origin URL: {value}")
            discovered = filtered
    pages: list[dict[str, Any]] = []
    include_patterns = [re.compile(pattern) for pattern in args.include_regex]
    exclude_patterns = [re.compile(pattern) for pattern in args.exclude_regex]
    inspection_candidates = [
        value
        for value in discovered
        if (not include_patterns or any(pattern.search(value) for pattern in include_patterns))
        and not any(pattern.search(value) for pattern in exclude_patterns)
    ]
    if discovered:
        robot_parser = build_robot_parser(base_origin, args.timeout, warnings)
        selected = select_pattern_samples(inspection_candidates, args.max_pages, args.samples_per_pattern)
        for index, page_url in enumerate(selected):
            page = inspect_http_page(page_url, args.timeout, args.max_html_bytes, base_origin, robot_parser)
            if page_url in lastmod:
                page["sitemap_lastmod"] = lastmod[page_url]
            pages.append(page)
            if args.delay_ms and index + 1 < len(selected):
                time.sleep(args.delay_ms / 1000)
    remaining = max(args.max_pages - len(pages), 0)
    for directory_value in args.snapshot_dir:
        if remaining <= 0:
            warnings.append("Snapshot inspection stopped at configured page limit")
            break
        directory = Path(directory_value).resolve()
        snapshots = sorted(directory.rglob("*.html"))[:remaining]
        pages.extend(inspect_snapshot(path, directory, base_url) for path in snapshots)
        remaining = max(args.max_pages - len(pages), 0)
    analysis = analyze_pages(pages, base_url, args.similarity_threshold)
    inventory_urls = list(dict.fromkeys([*discovered, *(page["url"] for page in pages)]))
    limitations = [
        "Signals are observations, not automatic create, merge, redirect, delete, canonical, or noindex decisions.",
        "Public pages are parsed from static HTML; client-rendered content and links may be missing.",
        "Internal-link and orphan signals cover only inspected pages and sampled HTML.",
        "Similarity uses titles, descriptions, and headings; confirm user intent and full content before acting.",
    ]
    if len(discovered) > len([page for page in pages if page.get("source") == "http"]):
        limitations.append("Public page inspection was sampled by normalized path pattern rather than fetched exhaustively.")
    result: dict[str, Any] = {
        "generated_at": utc_now(),
        "inputs": {
            "sitemaps": args.sitemap,
            "url_lists": args.url_list,
            "snapshot_dirs": args.snapshot_dir,
            "base_url": base_url or None,
            "include_regex": args.include_regex,
            "exclude_regex": args.exclude_regex,
        },
        "scope": {
            "discovered_url_count": len(discovered),
            "inventory_url_count": len(inventory_urls),
            "inspection_candidate_count": len(inspection_candidates),
            "inspected_page_count": len(pages),
            "max_urls": args.max_urls,
            "max_pages": args.max_pages,
            "samples_per_pattern": args.samples_per_pattern,
        },
        "path_patterns": pattern_summary(inventory_urls),
        "pages": pages,
        "signals": analysis,
        "warnings": warnings,
        "limitations": limitations,
    }
    if args.include_discovered_urls:
        result["discovered_urls"] = discovered
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
