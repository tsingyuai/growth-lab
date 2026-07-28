---
name: media-crawler
description: Install, authenticate, configure, operate, and troubleshoot the external MediaCrawler client shared by Xiaohongshu, Douyin, Kuaishou, Bilibili, Weibo, Tieba, and Zhihu collectors. Use when auditing this client, onboarding a platform account, selecting search/detail/creator modes, enabling comments or media, locating outputs, or diagnosing crawler failures. Do not use it as the platform research methodology; hand that work to the matching media-crawler-* collector skill.
---

# MediaCrawler

This is the shared tool layer. Read [operations.md](references/operations.md) before changing the external checkout. Then invoke exactly one platform Skill:

- [Xiaohongshu](../media-crawler-xhs/SKILL.md)
- [Douyin](../media-crawler-douyin/SKILL.md)
- [Kuaishou](../media-crawler-kuaishou/SKILL.md)
- [Bilibili](../media-crawler-bilibili/SKILL.md)
- [Weibo](../media-crawler-weibo/SKILL.md)
- [Tieba](../media-crawler-tieba/SKILL.md)
- [Zhihu](../media-crawler-zhihu/SKILL.md)

MediaCrawler does not support Twitter/X or Reddit. Do not imply otherwise.

## Contract

1. If install or authentication is missing, invoke [onboard-growth-lab](../../models/onboard-growth-lab/SKILL.md). Do not duplicate the global audit here.
   Onboarding must obtain the user's explicit ban-risk acknowledgement before login or crawling, require existing-Chrome CDP with no browser or Cookie fallback, and verify each enabled platform with a non-empty minimal real read. Installation, a persisted profile, or a visible login alone is not readiness.
2. Treat `${MEDIACRAWLER_DIR:-${GROWTHLAB_CLIENT_ROOT:-$HOME/.growth-lab/clients}/MediaCrawler}` as an external checkout. Never vendor it or commit its browser profile, cookies, databases, or downloaded data.
3. Before a run, record upstream commit, platform, crawl type, keywords/IDs, config changes, login type, comment/media flags, and destination.
4. Modify only the documented platform config and `config/base_config.py`; show the diff before running. Restore unrelated example values.
5. Run serially and conservatively. Never silently retry risk-control or authentication errors.
6. Copy the required output into the invoking Model's `memory/<model>/...`; leave source provenance beside it. A Collector does not invent a new Memory owner.
7. Apply the upstream non-commercial learning license and each target platform's terms.

## Standard invocation

```bash
cd "${MEDIACRAWLER_DIR:-${GROWTHLAB_CLIENT_ROOT:-$HOME/.growth-lab/clients}/MediaCrawler}"
uv run main.py --platform <xhs|dy|ks|bili|wb|tieba|zhihu> --lt qrcode --type <search|detail|creator>
```

Use `--lt qrcode` with CDP and an existing Chrome session. Do not fall back to standard Playwright, a newly launched clean browser, or Cookie injection.

## Completion report

Return: exact source query/URLs, run time, upstream commit, raw and copied paths, record/media/comment counts, filters, partial failures, and any risk-control signal. Never report a search-card excerpt as full detail.
