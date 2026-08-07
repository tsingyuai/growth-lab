---
name: read-product-events
description: Use Growth Lab's implemented product-event Collector to normalize authorized CSV, JSON, or NDJSON exports, validate event data quality, and calculate aggregate ordered activation funnels without exposing raw user identifiers. Use when an activation loop receives a product analytics export or needs to verify whether its events support a decision.
---

# Read product events

1. Read repository `AGENTS.md` and `DATA.md`, determine the current Product workspace, then read its `SOUL.md`.
2. Read `../../../collectors/read-product-events/SKILL.md` and its required reference completely.
3. For a supported export, invoke `python -B ../../../collectors/read-product-events/scripts/normalize_product_events.py <export> --step <step-1> --step <step-2> [...]` from this Skill directory, adding explicit field options when required. Do not formulate a funnel result before the command exits successfully.
4. Use only the script's aggregate stdout for counts and rates. Do not publish a raw-row, presence-only, sensitivity, or alternative funnel. If the command fails, report measurement as blocked and include no conversion values.
5. Never expose a raw identifier or narrate one entity's path in conversation or shared output, even when values look synthetic. Discuss invalid rows only as aggregate quality counts.
6. Keep row-level private data under the team's approved retention policy. Write only necessary aggregates, provenance, limitations, and interpretation to the owning Model Memory.
7. Do not reinterpret event semantics or claim causation beyond the canonical Collector's boundaries.
