---
name: media-crawler-tieba
description: Collect Baidu Tieba thread and user evidence with MediaCrawler using keyword or bar discovery, exact thread detail, replies, and creator pages. Use for community pain-point, vocabulary, objection, topic, or user research with thread-context preservation.
---

# Tieba collection

Follow [media-crawler](../media-crawler/SKILL.md). Require purpose, keyword/bar/thread/user inputs, target size and time bounds, reply depth, and invoking Model Memory destination.

Use `--platform tieba --type search` for discovery. Configure bar names in `TIEBA_NAME_LIST` when the research scope is community-specific; otherwise use intent-distinct keywords. Configure exact thread IDs in `TIEBA_SPECIFIED_ID_LIST` and full user-home URLs in `TIEBA_CREATOR_URL_LIST`; use detail/creator mode.

Preserve bar name, thread title, original post, floor/reply relationships, author, publish time and canonical URL. Do not flatten replies into independent opinions without their parent context. Sample across different threads/authors and deduplicate by thread ID plus post/floor identity. Start without deep replies, enrich only relevant threads, and stop on authentication/risk control.

Return scope/bar list, exact inputs, raw/copied paths, thread/reply/user counts, coverage, time, commit, exclusions and selection rationale.
