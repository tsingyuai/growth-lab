---
name: media-crawler-bilibili
description: Collect Bilibili video and creator evidence with MediaCrawler through search, exact BV detail, comments, dynamics, contacts, and optional media. Use for topic, format, title, creator, or audience research with explicit time-range and quality controls.
---

# Bilibili collection

Follow [media-crawler](../media-crawler/SKILL.md). Define purpose, query/BV/creator inputs, date window, sample target, desired quality, comments/media scope, and invoking Model Memory destination.

Search with `--platform bili --type search`. Configure `START_DAY`, `END_DAY`, `BILI_SEARCH_MODE`, and conservative `MAX_NOTES_PER_DAY` in `config/bilibili_config.py`. Shortlist by relevance, content format, recency, creator fit and engagement—not raw plays alone. Put full video URLs or BV numbers in `BILI_SPECIFIED_ID_LIST`; put Space URLs or UIDs in `BILI_CREATOR_ID_LIST`. Use detail/creator mode respectively.

If downloading video, explicitly select `BILI_QN` compatible with account/video access and disclose that requested quality may be unavailable. `CREATOR_MODE`, contacts and dynamics limits are separate from content comments; record which were enabled. Deduplicate by BV, preserve query provenance, verify files, and stop on auth/risk control.

Return inputs, config window/mode/quality, raw/copied paths, counts and coverage, time, commit, partial failures, and selection rationale.
