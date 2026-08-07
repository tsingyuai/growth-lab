#!/usr/bin/env python3
"""Offline smoke tests for inspect_seo_content_inventory.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("inspect_seo_content_inventory.py")
SPEC = importlib.util.spec_from_file_location("inspect_seo_content_inventory", MODULE_PATH)
assert SPEC and SPEC.loader
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


def page(title: str, canonical: str, heading: str, body: str, links: str = "", description: str = "Useful page") -> str:
    description_tag = f'<meta name="description" content="{description}">' if description else ""
    return f"""<!doctype html>
<html lang="zh-CN"><head><title>{title}</title>{description_tag}
<link rel="canonical" href="{canonical}">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article"}}</script>
</head><body><h1>{heading}</h1>{links}<p>{body}</p></body></html>"""


class InventoryTests(unittest.TestCase):
    def test_path_patterns_replace_identifiers(self) -> None:
        value = "https://example.com/result/53530b51-3325-4928-8477-abb72e546148?view=full"
        self.assertEqual(inventory.path_pattern(value), "/result/{uuid}?view={value}")

    def test_nested_local_sitemap_keeps_origin_and_lastmod(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "child.xml").write_text(
                """<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://example.com/guide</loc><lastmod>2026-07-27</lastmod></url>
<url><loc>https://other.example/private</loc></url></urlset>""",
                encoding="utf-8",
            )
            (root / "index.xml").write_text(
                """<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<sitemap><loc>child.xml</loc></sitemap></sitemapindex>""",
                encoding="utf-8",
            )
            urls, lastmod, warnings = inventory.read_sitemaps(
                [str(root / "index.xml")], 1, 10, 10, "https://example.com"
            )
            self.assertEqual(urls, ["https://example.com/guide"])
            self.assertEqual(lastmod["https://example.com/guide"], "2026-07-27")
            self.assertTrue(any("off-origin" in warning for warning in warnings))

    def test_snapshot_inventory_reports_signals_without_actions(self) -> None:
        long_body = "这是用于验证页面内容盘点的正文。" * 30
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshots = root / "snapshots"
            snapshots.mkdir()
            (snapshots / "index.html").write_text(
                page(
                    "首页",
                    "https://example.com/",
                    "首页",
                    long_body,
                    '<a href="/guide">指南</a><a href="/guide-copy">指南副本</a>',
                ),
                encoding="utf-8",
            )
            (snapshots / "guide.html").write_text(
                page("写作指南", "https://example.com/guide", "写作指南", long_body),
                encoding="utf-8",
            )
            (snapshots / "guide-copy.html").write_text(
                page("写作指南", "https://example.com/guide-copy", "写作指南", long_body),
                encoding="utf-8",
            )
            (snapshots / "orphan.html").write_text(
                page("孤立页面", "https://example.com/orphan", "孤立页面", long_body, description=""),
                encoding="utf-8",
            )
            output = root / "inventory.json"
            code = inventory.main(
                [
                    "--snapshot-dir",
                    str(snapshots),
                    "--base-url",
                    "https://example.com/",
                    "--similarity-threshold",
                    "0.5",
                    "--out",
                    str(output),
                ]
            )
            self.assertEqual(code, 0)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["scope"]["inspected_page_count"], 4)
            self.assertEqual(result["scope"]["inventory_url_count"], 4)
            self.assertTrue(result["signals"]["duplicate_titles"])
            self.assertTrue(result["signals"]["exact_content_duplicates"])
            self.assertIn("https://example.com/orphan", result["signals"]["orphan_candidates"])
            orphan = next(item for item in result["pages"] if item["url"] == "https://example.com/orphan")
            self.assertIn("missing_meta_description", orphan["flags"])
            self.assertIn("Article", orphan["json_ld_types"])
            self.assertTrue(any("not automatic" in item for item in result["limitations"]))


if __name__ == "__main__":
    unittest.main()
