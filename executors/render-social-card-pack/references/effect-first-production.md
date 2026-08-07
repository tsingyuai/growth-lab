# Effect-first production

Use this contract for Product-promotion card packs. The acceptance target is a visually strong, immediately understandable card, not merely a valid PNG.

## 1. Lock the communication job

For every card, write before layout:

- `user_takeaway`: what the reader can understand, do, or obtain after seeing this card;
- `card_job`: one of hook, pain, method, step, proof, comparison, or checklist;
- `evidence_target`: the exact Product action, UI object, result, file, or before/after state that proves the message;
- exact copy and the one primary visual focus.

Reject Product-operation labels that do not communicate reader value. A screenshot source is not an evidence target. For example, `official website screenshot` is insufficient; `the generated page list proving that the SEO task produced ten routes` is specific enough.

## 2. Prefer API-led complete effects

Check the configured image provider before choosing a production mode.

- When an image API is configured and the user has approved the disclosed provider, model, output count, scope, and paid boundary, use it first for complete-effect exploration.
- Generate two or three materially different vertical-slice directions with the real title length, content density, screenshot count, screenshot aspect ratios, and card roles.
- Select the direction with the strongest hook, hierarchy, screenshot integration, visual character, and reconstruction feasibility. Color-only variants do not count.
- Preserve the selected effect's composition. Replace exact text, Product UI, logos, evidence, citations, and sensitive claims deterministically.
- When the provider is unavailable or the user declines it, use a proven deterministic layout preset and record the reason. Do not improvise a generic document-like layout and call it production-ready.

Image generation improves composition; it does not choose evidence or authorize fake UI. Never send a final card containing real UI or exact evidence through broad image-to-image beautification.

## 3. Require real Product screenshots

A Product-promotion pack must contain real Product-owned screenshots. Every capability claim card must show the corresponding real UI, output, repository artifact, or before/after result. A logo, repository identity, or homepage hero proves identity only; it does not prove how a workflow works.

Capture screenshots around the evidence target. Prefer a smaller meaningful crop over an entire page with unreadable text. Preserve an uncropped source and record the crop.

Choose one screenshot composition per screenshot-led card:

- `single-hero`: one dominant crop for one clear proof;
- `step-flow`: two or three screenshots arranged in task order;
- `hero-plus-detail`: one main screenshot plus one or two magnified details;
- `before-after`: matched states with an explicit changed area;
- `editorial-collage`: unequal screenshots with one dominant proof;
- `workspace-triptych`: three related views only when equal comparison is the point.

Do not place several equal screenshot tiles merely to fill space. In multi-screenshot compositions, create a clear primary image through size, overlap, crop, or reading order.

## 4. Crop and annotate precisely

Crop before composition. The meaningful Product region should dominate the crop; the existing density script only rejects obvious blank-space failures and is not proof of readability.

When the evidence target is not immediately visible, annotate before placing the screenshot into the card:

1. bind the marker to the screenshot coordinate system;
2. place the target point on a concrete control, query, result row, source summary, saved file, changed value, or other evidence object;
3. place the label where it does not cover the target;
4. connect label and target with an unambiguous line or outline;
5. render the annotated screenshot, then compose that complete image into the card.

Never target a tab bar, title bar, empty region, whole window, or decorative frame. Crop and inspect a magnified annotation detail before approval.

## 5. Build a varied but coherent series

When the user explicitly chooses replication, borrow the structure of exactly one validated primary reference. The transferable structure may include card order, hierarchy, relative geometry, whitespace rhythm, screenshot-zone map, and annotation pattern. Replace every source word, screenshot, logo, Product fact, person, proprietary UI, distinctive illustration, and brand asset. Record the source-to-output card map and every replacement zone before rendering. Do not blend several references or preserve the source's visual identity.

Write and validate `layout-ledger.json` before formal rendering. Across a pack, vary card archetype, title anchor, visual mass, reading path, screenshot geometry, and one structural move. Do not disguise a repeated `title + horizontal screenshot` template with new colors or labels.

Variation must serve the card job. Keep a common type system, color roles, annotation language, and footer treatment so the series still feels intentional.

Prefer:

- one dominant visual focus;
- concise copy with visible hierarchy;
- screenshots large enough to read at phone scale;
- breathing room around meaningful content;
- asymmetric, editorial composition when it improves the reading path.

Reject:

- document-like pages dominated by headers, boxes, and footers;
- large decorative frames around a tiny screenshot;
- dense equal grids;
- empty space without compositional purpose;
- visual polish that weakens evidence accuracy.

## 6. Review the final pixels

Mechanical checks are lower bounds. Inspect the actual rendered cards at full size and in a phone-scale contact sheet.

For each card, answer with visible evidence:

- Is the intended takeaway understood in a few seconds?
- Does the screenshot directly prove this card's claim?
- Is the evidence target readable without opening the source image?
- Does every annotation land on the intended UI object?
- Is there one dominant visual focus without crowding?
- Does this card have a distinct role and composition within the pack?

Mark `revise` when any answer is no, even if every script passes. Allow one targeted correction. Stop after repeated failure instead of labeling a weak output ready.

Use a full regeneration rather than a local correction when the card is visibly empty, its content job is incomplete, the reading path is flat, the screenshot is an undersized decoration, or its composition repeats another card's template. A full regeneration must select a different approved archetype and preserve the locked copy and evidence target. Follow `self-review-rework-gate.md`; allow at most three total candidates for one card.
