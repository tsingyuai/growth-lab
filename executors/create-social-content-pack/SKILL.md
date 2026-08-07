---
name: create-social-content-pack
description: Create a complete social content package from a persisted product claim ledger and social content research handoff, including candidate angles, drafts, card copy, article copy, asset plans, links, review notes, and platform-ready deliverables. Use for Xiaohongshu, WeChat official account, or cross-platform content packs before publication.
---

# Create a social content pack

Turn verified product facts and platform research into a ready-to-review content package. Do not publish, upload, or create platform drafts.

## Required inputs

Require:

- current Product workspace and its `memory/run-social-content-loop/` output path;
- product claim ledger from `$extract-product-facts`;
- social research handoff from `$research-social-content`;
- target platform set and audience;
- content goal and desired product action;
- brand, compliance, copyright, and academic-integrity boundaries;
- asset inventory or screenshot needs when visuals are required.

If the claim ledger or platform research is missing, stop and return the missing evidence to the calling Model.

## Plan candidates

Create a compact candidate table before drafting:

| Candidate | Platform fit | User pain | Product fact used | Save/share/comment value | Risk | Measurement path |
|---|---|---|---|---|---|---|

Include at least two candidates unless the user approved a single exact topic. Mark rejected candidates and why they are weaker.

## Draft

For each selected candidate, produce platform-neutral content intent first:

- hook;
- user diagnosis;
- practical method or story;
- Product bridge;
- proof and source needs;
- CTA;
- risk boundary.

Then generate platform variants through `$adapt-social-platform`.

## Assets

Use real product screenshots when the content explains product behavior. Use `$inspect-brand-assets` first when asset rights, privacy, or source are unclear.

Use `$generate-image` only for conceptual covers, diagrams, or illustrative scenes. Generated images must not impersonate real UI, real data, real testimonials, or competitor material.

Every asset entry should include purpose, source, required crop, platform ratio, alt/description, and whether it is real screenshot, official asset, generated image, or code-native graphic.

For card-based platform output, lock exact per-card copy and return the package to `$render-social-card-pack`. Content creation owns the message and card sequence; visual production owns visual specification, effect exploration, rendering, local correction, manifest validation, and visual review. Do not embed Product-specific rendering methods in this Executor.

When external visual research is used, require the validated single `visual-reference-selection.json`. Do not ask the renderer to synthesize a visual style from several public notes.

## Package shape

Store a package folder under the calling Model Memory when possible:

```text
YYYY-MM-DD-topic-social-pack/
├─ brief.md
├─ xiaohongshu.md
├─ wechat.md
├─ visual/
│  └─ visual-vN/
├─ assets/
└─ review.md
```

Use Markdown, HTML previews, images, or CSV according to the task. Do not put package files under SEO Memory.

## Content boundaries

- Ground every non-obvious claim in the claim ledger.
- Use competitors as evidence of user expectation, not templates.
- Avoid copied wording, title formulas, proprietary examples, visual identity, or screenshot assets.
- Avoid guaranteed outcomes, detector bypass, ghostwriting, fake citations, fake research results, and misleading urgency.
- Give useful value before Product conversion.

Return text-only packages to the calling Model for `$review-social-content`. When card visuals are required, return the locked package to `$render-social-card-pack`, then send the combined text and visual package to `$review-social-content`.
