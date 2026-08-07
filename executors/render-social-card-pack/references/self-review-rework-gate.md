# Self-review and rework gate

Apply this gate to the rendered pixels of every production card pack. Mechanical validity is only a prerequisite.

## Review procedure

1. Inspect every formal candidate at full size and in a phone-scale contact sheet.
2. Compare the vertical slice with one user-approved benchmark on transferable quality, not copied styling.
3. Write `visual-quality-review.json` using the contract below.
4. Run `scripts/validate_visual_quality_review.py`.
5. Exclude every failed card from `approved` outputs and from all video inputs.

Score each dimension from 1 to 5. Every score must be at least 4; do not average away a failure:

- `content_completeness`: enough concrete explanation, method or evidence to perform the declared card job;
- `hierarchy`: an immediate title-support-proof reading order;
- `composition`: intentional balance without purposeless emptiness or cramped filler;
- `layout_vitality`: a role-specific reading path rather than a rigid repeated template;
- `mobile_readability`: core copy and proof remain legible at phone scale;
- `evidence_strength`: the visible Product state or example directly proves the claim;
- `visual_finish`: clean typography, crop, alignment, color and annotation details;
- `benchmark_parity`: transferable finish is equal to or better than the approved benchmark.

Require all per-card checks: `one_clear_job`, `no_placeholder_content`, `no_purposeless_empty_zone`, `exact_copy`, `evidence_target_visible`, and `phone_scale_checked`. Require all sequence checks: `distinct_compositions`, `no_template_repetition`, `distinct_product_states`, and `coherent_visual_system`.

## Rework decision

- Use `targeted-correction` only for one localized failure such as a crop, label, alignment or exact-copy error.
- Use `full-regeneration` for content incompleteness, purposeless emptiness, weak evidence, flat hierarchy, rigid layout, or two or more failed score dimensions. Select a different composition archetype; changing only color, decoration or wording position is not a regeneration.
- Render at most three total attempts per card. After the third failed attempt, set the card and package to `blocked`; do not return the best failed candidate.
- Re-run the complete gate after every correction. Only `decision=approved` cards in a `status=pass` review may enter video or publishing.

## Review contract

```json
{
  "schema_version": 1,
  "status": "pass",
  "attempt": 1,
  "reviewed_at_phone_scale": true,
  "benchmark": {"source": "path-or-id", "approved_by_user": true},
  "cards": [
    {
      "id": "01-cover",
      "output": "render/01-cover.png",
      "decision": "approved",
      "scores": {
        "content_completeness": 4,
        "hierarchy": 4,
        "composition": 4,
        "layout_vitality": 4,
        "mobile_readability": 4,
        "evidence_strength": 4,
        "visual_finish": 4,
        "benchmark_parity": 4
      },
      "checks": {
        "one_clear_job": true,
        "no_placeholder_content": true,
        "no_purposeless_empty_zone": true,
        "exact_copy": true,
        "evidence_target_visible": true,
        "phone_scale_checked": true
      },
      "failure_modes": [],
      "next_action": "none"
    }
  ],
  "sequence_checks": {
    "distinct_compositions": true,
    "no_template_repetition": true,
    "distinct_product_states": true,
    "coherent_visual_system": true
  },
  "rework_items": []
}
```
