---
name: xhs-render-cards
description: "把已批准的小红书草稿、单一分析参考和真实产品截图变成效果优先的可审查卡片：有可用且获授权的生图 API 时优先探索完整效果，真实 UI 用单图、多步骤截图流、局部特写或精准圈注确定性合成，并用版式指纹和最终像素审查避免平铺拥挤与重复模板。"
---

# Xiaohongshu card production

Read [visual-production-contract.md](references/visual-production-contract.md), [rendering.md](references/rendering.md), and [visual-review-rubric.md](references/visual-review-rubric.md). Also read the generic [effect-first production contract](../render-social-card-pack/references/effect-first-production.md). Keep DAI and compliance rules from [deai.md](references/deai.md) and [quality-gates.md](references/quality-gates.md).

## Required inputs

Require before rendering:

- lifecycle confirmation that all generated or transformed output remains the user's/publisher's responsibility and never represents this Skill's position or endorsement; this applies before and after rendering even if nothing is published, and does not waive safety or compliance rules;
- approved `draft.md` content script with exact card copy, account role, reader, one-sentence user value, per-card claim, reader takeaway, and evidence source;
- `content-approval.md` recording the user's explicit approval of the current script version; research approval, lifecycle confirmation, image-generation approval, or approval of an older draft is not a substitute;
- verified Product facts and real Product-owned screenshots; a logo or brand asset alone is insufficient for a Product-promotion pack;
- one validated `visual-reference-selection.json` when external visual research is used;
- output directory in the current Product workspace's calling Model run;
- target canvas, card count, rights/privacy boundaries, image-provider configuration status, and whether paid image generation is approved.

The selected public reference is analysis-only. In normal modes, learn hierarchy, proof-zone proportion, density, and reading rhythm. In explicitly confirmed `close-replication`, reproduce its card order, hierarchy, relative geometry, whitespace rhythm, and screenshot-zone map one-to-one. In every mode, replace source wording, images, logos, people, proprietary UI, distinctive illustrations, and brand assets. Rejected candidates contribute no rules.

## 1. Verify the approved script and lock evidence

Do not enter this Executor until the user has reviewed the complete content script without relying on rendered visuals. Confirm that `draft.md` is independently detailed and coherent: every card adds one clear point, names the reader benefit, and traces Product claims to current evidence. Run DAI on title, caption, card copy, CTA, and tags. Delete unsupported claims instead of weakening them with defensive filler.

Verify that `content-approval.md` applies to the current title, card order, exact visible copy, CTA, and card count. Any material script change invalidates approval and returns the workflow to script review. Typographic or punctuation-only corrections may proceed when recorded.

Only after that verification, write `image-plan.md` using [image-plan.md](references/image-plan.md). Lock every visible string before rendering. Do not add cards merely to match the reference.

For `close-replication`, write a complete source-card-to-output-card mapping and preserve the source card count/order unless a missing Product fact forces a documented omission. Record `replication_policy`, replacement zones, retained geometry, and unresolved rights risk before generation.

## 2. Capture real Product evidence

Use [screenshot-assets](../screenshot-assets/SKILL.md) for real Product UI, website, code, output, or data. Keep the original screenshot as evidence. For every capability card, name the exact UI object or result that proves the claim. Choose a single hero crop, two-to-three-step screenshot flow, hero-plus-detail composition, before/after pair, or unequal editorial collage. Bind annotations in screenshot coordinates before composition: use a short dashed underline for text targets and a thin closed circle or rounded outline for controls or regions. Do not use arrows or leader lines; use numbering, alignment, or an arrowless spine for sequence. Remove an annotation when it cannot land on one exact target. Do not ask an image model to recreate Product UI, logos, citations, statistics, or source text and present it as real.

## 3. Check image API and choose one production mode

Before selecting a mode, follow the configuration gate in [`generate-image`](../generate-image/SKILL.md). When a provider is configured, recommend API-led effect exploration and disclose provider/model, output count, scope, and paid-call boundary before asking for confirmation. When no provider is configured, explicitly ask on the first decision whether the user wants to configure one for a better visual result; do not silently default to deterministic rendering.

After API use is approved, use `complete-effect` first for promotional covers and visually led card packs. Generate two or three materially distinct vertical-slice directions using the real copy length, screenshot count, screenshot aspect ratios, and card roles. Select the strongest effect, preserve its composition, then replace exact copy, Product UI, logos, citations, and evidence deterministically. Prefer `separable-layer` only when the model should add visual depth without owning composition, text, or UI.

- `deterministic`: HTML/CSS, Canvas, SVG, or Pillow owns layout and exact text. Use as the full production mode only when the user declines API generation, provider configuration is unavailable, the task is purely structural, or effect exploration adds no meaningful value. Record the reason.
- `separable-layer`: the image model creates only a background, texture, or illustration without text/UI; deterministic rendering places approved copy and Product evidence.
- `complete-effect`: the image model proposes a whole visual direction. Generated text, UI, logos, evidence, and sensitive claims must be replaced or the candidate rejected.

Image generation remains separately authorized. API-first is a production preference, not permission to spend: never call a provider from configuration alone, never silently retry, and never request a key in conversation.

## 4. Test a three-card vertical slice

Before expanding a large pack, render:

1. hook/cover;
2. independently useful method/checklist/comparison;
3. real Product evidence when the content makes a Product claim.

Show the actual images in the conversation. A filesystem path alone is not a visual review. Check phone-size readability, hierarchy, Product truthfulness, privacy, and copying boundaries. Reject the slice when it looks like a document page, places a small screenshot inside a large decorative frame, uses equal screenshot tiles without a reason, leaves purposeless empty space, or cannot show the evidence target at phone size. Visual polish, accurate evidence, and an uncluttered reading path must pass together.

## 5. Validate and review

Create `visual-manifest.json`, then run:

```powershell
python executors/xhs-render-cards/scripts/validate_social_card_pack.py --package <visual-package>
```

The Xiaohongshu wrapper delegates generic screenshot composition, screenshot-density checks, and layout-variety checks to [`render-social-card-pack`](../render-social-card-pack/SKILL.md). Do not maintain a second implementation here.

Run the existing DAI and compliance checks with `make lint-post POST=<post-directory>`. Inspect every final image at full size and as a contact sheet. For every screenshot card, inspect a magnified crop of each annotation and confirm that it lands on a concrete UI object rather than a title bar, tab, empty area, or whole window. Write `visual-review.md` with sources, selected mode, generated assets, replacement decisions, dimensions, privacy, copyright, factual and mobile-readability results. State what the reader learns, what screenshot proves it, and why the composition is neither crowded nor visually empty. Mechanical success is not approval.

Only reviewed files under `render/` may enter the human publishing package. Rendering never authorizes upload or publication.

## Stop rules

Stop on an absent, incomplete, stale, or unapproved content script; missing Product evidence; ambiguous rights; unreviewed reference selection; exposed private data; fake UI; malformed text; provider failure; or repeated candidate failure. Before script approval, do not create image prompts, call image providers, render a vertical slice, or render the full pack. One targeted retry may replace an explicitly authorized work-in-progress candidate; do not loop or create duplicate publishable assets.
