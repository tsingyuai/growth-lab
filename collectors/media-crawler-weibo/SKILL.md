---
name: media-crawler-weibo
description: Collect Weibo posts and creator evidence with MediaCrawler using search, exact post IDs, comments, optional media, and creator IDs. Use for discourse, trend, messaging, audience-language, or account research requiring preserved provenance and risk-aware detail enrichment.
---

# Weibo collection

Follow [media-crawler](../media-crawler/SKILL.md). Define research purpose, keywords/post IDs/creator IDs, sample and time bounds, comments/media scope, and invoking Model Memory destination.

Search with `--platform wb --type search`; set `WEIBO_SEARCH_TYPE` deliberately. Use direct problem, category and audience/event query variants, then shortlist by relevance, time, source/account fit, content form and engagement. Configure exact post IDs in `WEIBO_SPECIFIED_ID_LIST` and user IDs in `WEIBO_CREATOR_ID_LIST`; run detail/creator mode.

`ENABLE_WEIBO_FULL_TEXT` makes extra detail requests and raises risk-control probability. Keep it off during broad discovery and enable it only for a small, explicit shortlist when full text is required. Treat repost text, original text and comments as different evidence. Deduplicate by post ID and preserve query provenance.

Return exact inputs, full-text/comment/media flags, raw/copied paths, coverage, time, commit, selection rationale and risk-control/partial failures.
