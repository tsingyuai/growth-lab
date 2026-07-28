---
name: media-crawler-douyin
description: Collect Douyin competitive evidence with MediaCrawler using keyword search, exact video detail, comments, media, and creator profiles. Use for trend, hook, format, audience-language, or creator research that needs reproducible raw evidence and a documented selection method.
---

# Douyin collection

Follow [media-crawler](../media-crawler/SKILL.md). Require purpose, keywords/links, sample size, date window, comments/media scope, and destination under the invoking Model's Memory.

Build queries across problem, category, and audience. Run `--platform dy --type search` serially; shortlist on topical relevance, hook/format diversity, recency and engagement. Search cards are discovery evidence only. For exact enrichment, set `DY_SPECIFIED_ID_LIST` in `config/dy_config.py`; it accepts full video URLs, URLs containing `modal_id`, short links, or video IDs. For creators set `DY_CREATOR_ID_LIST` to profile URLs or `sec_user_id`, then use `--type creator`. `PUBLISH_TIME_TYPE` controls the upstream publish-time filter.

Enable comments or `ENABLE_GET_MEIDAS` only for the shortlist, then run `--type detail`. Verify canonical video ID, author, caption, publish time, engagement, media mapping, comment coverage and any truncation. Deduplicate by video ID and retain the discovery query. Stop on login/risk control; never loop retries.

Return raw/copied paths, query and selection rationale, search/detail/creator counts, comment/media coverage, time and upstream commit.
