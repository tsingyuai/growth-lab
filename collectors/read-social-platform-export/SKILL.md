---
name: read-social-platform-export
description: Normalize authorized Xiaohongshu, WeChat official account, or other social-platform CSV/JSON exports into privacy-preserving aggregate campaign metrics. Use when reading exposure, reads, views, likes, comments, saves, shares, follows, link clicks, post IDs, dates, or platform result exports for social content review.
---

# Read social platform exports

Treat exports as time-scoped platform evidence, not complete product truth.

## Boundaries

- Use authorized exports and the team's approved private-data location.
- Never write credentials, cookies, private account tokens, private comments, direct messages, raw user identifiers, or complete row-level exports into conversation or shared Memory.
- Preserve platform, export time, filters, timezone, account scope, date range, and whether metrics are organic, boosted, or mixed.
- Do not infer product registration or activation from platform metrics alone.

## Normalize

For common CSV or JSON exports, run:

```text
python collectors/read-social-platform-export/scripts/normalize_social_platform_export.py <export> --platform <platform> --out <aggregate-output>.json
```

Use `--date-field`, `--post-field`, `--title-field`, and metric field options when auto-detection is ambiguous. Read `--help` for exact options.

The script outputs field mapping, row-quality counts, post-level aggregates, totals, and simple derived rates. Treat its aggregate output as the calculation source of truth for reported platform metrics.

## Validate

Check:

- required date, post, title, and metric fields for the current question;
- whether dates parse and the window is complete;
- whether boosted and organic rows are mixed;
- whether totals can be summed safely;
- whether a post appears multiple times by day, by source, or by metric row;
- whether hidden thresholds or export caps may suppress values.

Do not compare incompatible windows, platform definitions, account scopes, or boosted/organic mixes.

## Return evidence

Return:

- provenance and quality limits;
- normalized field map;
- platform-level totals;
- post-level aggregate table;
- derived rates only when denominators are valid;
- missing evidence;
- whether the evidence is usable for a decision, diagnosis only, or blocked.

Persist only necessary aggregates and interpretation in the current Product workspace's `memory/run-social-content-loop/`.
