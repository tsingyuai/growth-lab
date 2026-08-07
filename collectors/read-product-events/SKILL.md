---
name: read-product-events
description: Normalize authorized product event exports, validate event semantics and data quality, and calculate privacy-preserving aggregate activation funnels. Use when Growth Lab receives CSV, JSON, or NDJSON product analytics exports, needs to map event fields, measure ordered user steps, compare event coverage, or diagnose whether activation data is trustworthy.
---

# Read product events

Treat an export as time-scoped evidence, not complete product truth. Read [event-contract.md](references/event-contract.md) before interpreting a funnel.

## Boundaries

- Use authorized exports and the team's approved private-data location.
- Never write credentials, raw user identifiers, emails, phone numbers, free-text payloads, complete private rows, or a single entity's journey to conversation, shared Memory, or reports. This applies even when identifiers look synthetic.
- Preserve source name, export time, analytics provider, requested filters, and analysis window.
- Do not infer missing field mappings or event meanings from convenient names when more than one interpretation is plausible.
- Do not claim causation from a funnel, or product value from a page view or click alone.

## Inspect before normalizing

1. Identify CSV, JSON array, JSON object containing `events`, `data`, or `results`, or newline-delimited JSON.
2. Inspect headers and a minimal safe sample locally. Do not echo sensitive values into conversation or logs.
3. Map event name, entity identifier, and timestamp. Record whether identity represents a user, account, device, or session.
4. Confirm the ordered diagnostic steps and the value-based activation event with the calling Model.
5. Confirm timezone, data window, filters, staff/test exclusions, identity stitching, event version, and known delivery delay.

## Use the deterministic normalizer

### Mandatory calculation rule

For every supplied supported export, run the normalizer before producing any funnel count, table, or rate. Treat its aggregate output as the sole calculation source of truth.

- The only allowed funnel counts and rates are the values under `funnel` in the script output.
- Never publish a second raw-row, presence-only, sensitivity, or alternative funnel beside the normalized funnel.
- Never add a row listed as missing, invalid, duplicate, or outside the window back into a funnel denominator, even to illustrate instability.
- Discuss excluded rows only through `quality` counts and explain how they limit the decision.
- If the script did not run successfully, report no funnel counts or conversion rates.
- After field mapping is known, base the user-facing analysis on normalized aggregate stdout, not on raw row inspection. Never name an identifier or narrate one entity's path.

If the script cannot run or the required fields cannot be mapped unambiguously, return a blocked measurement result instead of estimating conversion.

Run:

```text
python collectors/read-product-events/scripts/normalize_product_events.py <export> \
  --step signup_completed \
  --step workspace_created \
  --step first_output_completed \
  --out <private-or-model-memory-path>.json
```

The script supports `.csv`, `.json`, and `.jsonl`/NDJSON. It auto-detects common aliases only when one unambiguous field is present. Otherwise pass `--event-field`, `--user-field`, and `--timestamp-field` explicitly. Use `--start` and `--end` to apply an inclusive UTC analysis window.

The output contains field mapping, row-quality counts, aggregate event totals, ordered unique-entity funnel conversion, and median elapsed time from the first step to the final step. It intentionally omits identifiers and raw rows.

Use `quality.input_rows` to describe the source size and `quality.usable_rows` for normalized event coverage. Use only `funnel.steps[*].entities` and its conversions for the ordered funnel. A raw row with an invalid timestamp may be mentioned as a quality failure but must not be counted as a reached step.

Read script help for exact options:

```text
python collectors/read-product-events/scripts/normalize_product_events.py --help
```

## Validate the result

- Reconcile total rows with usable, excluded, duplicate, and invalid rows.
- Check whether each funnel step exists in the selected window.
- Confirm events are ordered per entity; do not count a later step that occurred before its prerequisite.
- Investigate sudden zeros, impossible order, event-name drift, timestamp errors, duplicate delivery, bot or staff activity, and anonymous-to-authenticated identity breaks.
- Compare only compatible populations, event versions, windows, and entity definitions.

## Return evidence

Provide the calling Model with:

- provenance and analysis window;
- explicit field and identity mapping;
- activation and step definitions;
- aggregate counts and conversion rates;
- elapsed-time evidence when available;
- exclusions, quality failures, and known blind spots;
- whether the evidence is usable for a decision, usable only for diagnosis, or blocked.

Persist only the necessary aggregate output and interpretation in the current Product's owning Model Memory. Keep source exports under the team's private retention policy.

Before returning, verify that every reported funnel count equals the script's `funnel` output, excluded rows appear only under data quality, and the response contains no raw identifier or single-entity path.
