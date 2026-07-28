---
name: media-crawler-zhihu
description: Collect Zhihu answers, articles, videos, comments, and creator evidence with MediaCrawler through search and exact URLs. Use for expert discourse, problem framing, objections, terminology, topic, or creator research where content type and question context must remain explicit.
---

# Zhihu collection

Follow [media-crawler](../media-crawler/SKILL.md). Require purpose, keyword/content/creator inputs, sample and date bounds, comments/media scope, and invoking Model Memory destination.

Search with `--platform zhihu --type search` using problem wording, concept/category and audience/use-case variants. Shortlist by relevance, argument/content-type diversity, recency, author fit and engagement. Configure `ZHIHU_SPECIFIED_ID_LIST` with full answer, article, or video URLs; configure `ZHIHU_CREATOR_URL_LIST` with full people URLs. Run detail/creator mode.

Preserve content type. For answers retain question context; for articles retain article title; for video identify unavailable transcript rather than inventing one. Separate author text from comments, deduplicate by canonical content ID, and retain discovery-query provenance. Enable comments/media only for a shortlist and stop on challenge/risk control.

Return content-type breakdown, inputs, raw/copied paths, detail/comment/media coverage, time, commit, exclusions and selection rationale.
