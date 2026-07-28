---
name: media-crawler-kuaishou
description: Collect Kuaishou competitive evidence with MediaCrawler using keyword search, exact video detail, comments, media, and creator profiles. Use for trend, format, audience-language, or creator research requiring reproducible source records and explicit collection limits.
---

# Kuaishou collection

Follow [media-crawler](../media-crawler/SKILL.md). Require purpose, keywords/links, target count, time window, comments/media scope, and a destination in the invoking Model's Memory.

Search with `--platform ks --type search`, starting serially with one intent-distinct keyword. Shortlist for relevance, format diversity, recency and engagement; do not confuse a search excerpt with full detail. Put full `kuaishou.com/short-video/...` URLs or pure video IDs in `KS_SPECIFIED_ID_LIST`; put profile URLs or user IDs in `KS_CREATOR_ID_LIST`. Run `--type detail` or `--type creator` accordingly.

Enable comments/media only for shortlisted items. Verify video ID, creator, caption, publish time, engagement, media association and comment coverage. Deduplicate by video ID, preserve query provenance, and report empty/risk-controlled/partial results honestly. Stop on challenge or expired login.

Return raw/copied paths, exact inputs, selection rationale, counts, coverage, collection time and upstream commit.
