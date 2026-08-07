---
name: render-social-card-pack
description: Turn approved platform-specific social card copy, real Product screenshots and brand evidence, and one analysis-only visual reference into an effect-first reviewed image pack. Use after Xiaohongshu or another card-based social draft is locked and before publishing preparation, especially for API-led complete-effect exploration, screenshot step flows, precise UI annotations, reference-structure adaptation, varied series layouts, mobile readability, and reproducible render artifacts.
---

# Render social card packs

Produce a platform-ready card set without embedding any Product's brand, assets, or claims in this Executor. Read [visual-production-contract.md](references/visual-production-contract.md) and [effect-first-production.md](references/effect-first-production.md) before rendering, then read [visual-review-rubric.md](references/visual-review-rubric.md) and [self-review-rework-gate.md](references/self-review-rework-gate.md) before handoff.

## Boundaries

- Read stable Product brand facts from its workspace `SOUL.md` and referenced Product-repository assets or documentation. Keep run-specific logos, crops, screenshots, references, and visual decisions in the owning workspace's `memory/run-social-content-loop/` package.
- Treat the one validated competitor or user-provided primary reference as analysis-only unless explicit rights permit reuse. Never blend several external visual samples. Normal modes extract transferable rules. Explicit `close-replication` may reproduce the primary's full card sequence and relative layout map, while replacing source wording, images, logos, people, proprietary UI, distinctive illustrations, and brand assets.
- Invoke `$generate-image` for model calls. Do not duplicate provider credentials, API clients, or proxy behavior here.
- Do not log in, upload, publish, create a platform draft, or modify account state.
- Treat image generation as a separately authorized external action. A content-pack approval does not authorize paid generation. Check configuration before selecting a production mode; when configured and approved, prefer API-led effect exploration for visually led promotional work.
- Optimize for the final communication effect. Passing dimensions, manifests, density checks, or layout-ledger checks never makes a visually weak or semantically inaccurate card ready.
- Require real Product screenshots for Product-promotion packs. Use generated visuals for the surrounding effect, never as a replacement for Product evidence.

## Required inputs

Require these persisted inputs, not conversation-only summaries:

- current Product workspace and owning social-content package path;
- approved platform-specific card sequence and exact formal copy;
- product claim ledger and social research handoff;
- asset inventory from `$inspect-brand-assets` when real screenshots or brand assets are needed;
- target platform, canvas, card count, audience, content goal, and desired action;
- rights, privacy, compliance, brand, and publication boundaries;
- validated `visual-reference-selection.json` containing exactly one primary external learning reference when external visual research is used;
- optional run-specific visual profile derived from Product-owned evidence.

Return missing inputs to the calling Model. Do not invent Product styling or use another Product's Memory as a fallback.

## 1. Create the visual package

Create a new versioned `visual-vN/` or timestamped folder unless overwrite is explicitly authorized. Use the contract's folder shape and initialize `visual-manifest.json` before generation.

Lock for every card:

- stable ID and role;
- exact title, subtitle, labels, footer, and prohibited extra text;
- claim and evidence boundaries;
- screenshot source, crop, redaction, and annotation needs;
- one `user_takeaway` and one exact `evidence_target` that the screenshot must prove;
- expected output filename and platform dimensions.

## 2. Write the visual specification

Resolve visual evidence in this order:

1. authorized Product visual profile and official assets;
2. the one validated primary analysis-only visual reference;
3. persisted non-visual platform research and the primary reference's extracted rules;
4. a restrained platform baseline marked `default-baseline`.

Write `visual-spec.md` so rendering no longer depends on reopening source references. Record canvas, hierarchy, grid, whitespace, density, color roles, screenshot treatment, reusable components, per-card rhythm, generated-image boundaries, source tier, conflicts, and confidence. Name the single primary reference and explicitly state that rejected candidates contributed no rules. For `close-replication`, include the one-to-one card map, retained geometry, every replacement zone, and the persisted risk confirmation.

## 3. Test a vertical slice

Render three roles before expanding a large pack:

- cover or hook;
- independently useful method, checklist, or comparison card;
- real-product evidence card when the content makes a Product claim.

Review hook clarity, mobile readability, Product evidence, screenshot prominence, annotation accuracy, series consistency, privacy, and copying boundaries. Expand only after the slice passes. Acceptance of a rough prototype does not approve it as a production direction.

## 4. Choose one production mode

Follow `$generate-image` before choosing. If a provider is configured, disclose provider/model, scope, output count, and paid boundary, then recommend API-led generation for better visual quality. If no provider is configured, proactively ask on the first image-production decision whether the user wants to configure one for a better result. Do not silently fall back to deterministic rendering.

- `deterministic`: HTML/CSS, SVG, Canvas, or Pillow owns layout and exact text. Use as the whole production mode only after the user declines API generation, configuration is unavailable, or the task is purely structural. It may still replace exact text and real evidence inside an API-generated effect.
- `complete-effect`: AIGC proposes the complete themed card using locked content semantics; the selected effect becomes the layout authority and receives minimal local correction.
- `separable-layer`: AIGC creates only a background, texture, illustration, or other separable non-product layer beneath deterministic content.

When API use is available and approved, use `complete-effect` first for covers and promotional packs where hierarchy, spacing, and visual character determine quality. Test two or three distinct directions before expansion. Do not default to isolated decorative assets followed by an unrelated second layout.

For a pack that will become a Product-promotion video, one reusable abstract background is only a brand substrate and never counts as the scene's primary evidence. When Product screenshots or output examples exist, use them in the claim scenes. Across a sequence of four or more scenes, require at least three distinct primary visual assets or independently composed complete effects; do not approve a pack whose meaningful variation is only text placed over the same generated background. Generate role-specific visual effects separately and keep all exact Product UI deterministic.

## 5. Explore and select complete effects

When using `complete-effect`, create two or three distinct analysis-only directions for the vertical slice. Store prompts under `prompts/effects/` and outputs under `effects/`.

Score candidates with the review rubric. Record adopt/reject decisions in `effect-review.md`. Generated logos, Product UI, citations, statistics, evidence, and sensitive claims are never authoritative.

## 6. Generate formal candidates and correct zones

Freeze formal prompt files under `prompts/formal/`. Generate each distinct card separately; do not use one batch prompt for different card roles.

For screenshot-led cards, select `single-hero`, `step-flow`, `hero-plus-detail`, `before-after`, `editorial-collage`, or `workspace-triptych` from the effect-first contract. Multi-screenshot layouts must communicate an ordered process or a meaningful comparison, not fill a grid. Add screenshot-bound annotations when the evidence target is not immediately visible.

Classify each visible zone:

- `retain`: exact approved low-risk copy, legible at phone size, no malformed glyphs or claim drift;
- `replace`: logo, real screenshot, evidence, citation, statistic, sensitive claim, privacy mask, or mismatched text;
- `reject`: fake UI presented as real, invented paper/data, copied visual identity, broken hierarchy, or a result requiring broad redesign.

Keep untouched model output under `raw/`. Save corrected formal candidates under `render/`. Preserve the selected effect's composition; use local tools only for targeted text, logo, screenshot, privacy, crop, color-mode, and export corrections.

## 7. Validate mechanically

Compose real Product screenshots deterministically with `compose_screenshot_scene.py`; the image model must not redraw Product UI. Check source crops with `check_screenshot_density.py` before annotation, then inspect the final screenshot region for phone-scale readability. Treat the density result as a blank-space lower bound, not an information-coverage score. For packs of three or more cards, record each card's composition fingerprint and run `check_layout_variety.py`; inspect the final contact sheet as well because declarative fingerprints do not prove pixel-level variation.

Create `visual-manifest.json` according to the contract, then run:

```bash
python executors/render-social-card-pack/scripts/check_screenshot_density.py \
  <screenshot-files>
python executors/render-social-card-pack/scripts/check_layout_variety.py \
  --ledger <visual-package-directory>/layout-ledger.json
python executors/render-social-card-pack/scripts/validate_social_card_pack.py \
  --package <visual-package-directory>
```

Require unique card IDs and output paths, existing PNGs, declared dimensions, supported RGB/RGBA color type, and exact manifest-to-render correspondence. Mechanical validation does not replace visual, factual, copyright, or compliance review.

## 8. Review and hand off

Write `visual-review.md` with:

- selected mode and effect decisions;
- per-zone retain/replace/reject record;
- prompt, model/provider, reference, screenshot, and rights provenance;
- dimensions, color mode, mobile-preview, privacy, and image-loading results;
- factual, copyright, brand, compliance, and AI-artifact findings;
- per-card confirmation that the takeaway is immediate, the screenshot proves the claim, and each annotation hits its intended UI object;
- decision: `block`, `revise`, or `ready for social-content review`.

Return the visual package to `$review-social-content`. Only reviewed files under `render/` may enter `$prepare-human-publishing`.

Before setting any card to `approved`, write `visual-quality-review.json` and run:

```bash
python executors/render-social-card-pack/scripts/validate_visual_quality_review.py \
  --review <visual-package-directory>/visual-quality-review.json
```

Any nonzero result means `rework-required`. Do not hand a failed card to video or publishing. Follow the self-review gate's targeted-correction versus full-regeneration rule, change the failed composition rather than only its colors, and stop as `blocked` after three total attempts instead of returning the least-bad candidate.

## Idempotency and stop rules

- Use a versioned visual package and stable card IDs. Never overwrite a passed render unless the user authorized replacement.
- Record prompt path, reference paths, model, and generation time for each generated candidate.
- Retry a failed card once with one targeted correction. Stop after repeated malformed text, fake evidence, provider failure, rights uncertainty, or corrections that would require a full redesign.
- A retry may replace the same candidate path inside an explicitly authorized work-in-progress version; it must not create duplicate publishable cards or platform actions.
- In scheduled runs, default to inspection and recommendation. Do not generate paid assets unless the automation scope explicitly authorizes generation and defines a budget/stop boundary.

## Resources

- [visual-production-contract.md](references/visual-production-contract.md): input, manifest, folder, and stage contract.
- [visual-review-rubric.md](references/visual-review-rubric.md): effect selection and final review gates.
- `scripts/validate_social_card_pack.py`: zero-dependency PNG and manifest validator.
- `scripts/compose_screenshot_scene.py`: deterministic multi-screenshot composition (Pillow).
- `scripts/check_screenshot_density.py`: rejects screenshot crops dominated by blank space (Pillow).
- `scripts/check_layout_variety.py`: validates per-card composition fingerprints.
- `scripts/validate_visual_quality_review.py`: enforces non-compensating pixel-review and automatic rework decisions.
- `scripts/render_workflow_card_pack.py`: bounded deterministic renderer for exact-copy workflow cards over one approved separable background layer.
