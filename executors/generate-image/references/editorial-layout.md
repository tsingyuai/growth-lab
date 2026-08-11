# Editorial layout direction

Use this reference for visually led assets where composition, typography, or information density affects quality. Channel-specific card contracts may add stricter requirements; they do not replace this visual direction.

This independently written Growth Lab workflow adapts general design methods reviewed in Anthropic's Apache-2.0 [`canvas-design`](https://github.com/anthropics/skills/tree/b29e7cf65e5cb78a5ac33d582270551bc74a14eb/skills/canvas-design) and [`frontend-design`](https://github.com/anthropics/skills/tree/b29e7cf65e5cb78a5ac33d582270551bc74a14eb/skills/frontend-design) Skills and the MIT-licensed wshobson/agents [`visual-design-foundations`](https://github.com/wshobson/agents/tree/1ad2f007d5e9ec822a2d79e727ac1dcdf5f66f11/plugins/ui-design/skills/visual-design-foundations) Skill. No upstream Skill text, code, font, template or executable is bundled here; repository-level boundaries are recorded in [`THIRD_PARTY_NOTICES.md`](../../../THIRD_PARTY_NOTICES.md).

## 1. Start from the communication job

Write one sentence for what the viewer should understand in a few seconds. Reduce the content to:

- one primary message;
- one supporting idea or proof;
- one dominant visual focus;
- optional metadata that can remain quiet.

Do not design around every available fact. Move secondary content outside the image when it does not improve the immediate takeaway.

## 2. Define a visual philosophy

Write two to four sentences that explain how the subject becomes a visual system. Cover:

- space and form;
- palette and material;
- scale, rhythm, and balance;
- typography and hierarchy.

Describe a point of view rather than a named template. Ground it in the Product, audience, and placement. Avoid generic AI defaults unless the subject specifically calls for them.

## 3. Plan distinct compositions

Sketch two or three directions with the same real copy and asset constraints. Change the spatial idea, not only the palette. Useful differences include:

- image-led versus type-led;
- centered stillness versus asymmetric tension;
- one dominant crop versus a deliberate sequence;
- broad quiet field versus compact editorial rhythm.

Choose the direction with the clearest hierarchy, strongest subject fit, useful negative space, and feasible factual correction. Keep one signature move. Supporting shapes, labels, lines, and textures must remain subordinate.

## 4. Use restraint as a constraint

- Give every element a communication job.
- Use negative space to group, separate, pause, or direct attention.
- Avoid equal-weight grids unless equality is the meaning.
- Avoid decorative containers around content that already has structure.
- Limit accent color to intentional emphasis rather than distributing it everywhere.
- Keep the type system small and create contrast through role, scale, weight, and placement.
- Preserve safe margins and separation; nothing may clip or overlap accidentally.

Minimal work must be precise, not merely sparse. Dense work must still have an obvious entry point, rhythm, and quiet zones.

## 5. Write the provider prompt

Include these decisions in natural language:

```text
Communication job: [one immediate takeaway]
Visual philosophy: [space, form, palette, rhythm, and type]
Hierarchy: [primary -> support/proof -> metadata]
Composition: [focal point, reading path, crop, balance]
Negative space: [where it is protected and what it accomplishes]
Signature element: [one memorable move]
Exact text and factual zones: [verbatim strings and protected evidence]
Exclusions: [unnecessary decoration, extra text, fake UI, watermark, clutter]
```

Do not turn the prompt into pixel-by-pixel art direction unless deterministic geometry is required. Constrain hierarchy and total visual weight while leaving the model room to compose.

## 6. Review by subtraction

Inspect the full-size result and a thumbnail. Ask:

1. Is the communication job understood quickly?
2. Does one element lead the eye?
3. Is the reading order unambiguous?
4. Does whitespace perform a visible grouping or emphasis function?
5. Does anything exist only to make the canvas feel fuller?
6. Are typography, crop, alignment, and palette specific to the subject?
7. Can exact text and Product evidence be corrected locally without losing the composition?

For the second pass, remove or quiet the weakest element before considering additions. Prefer one targeted correction over a broad restyle. Reject a visually polished result when it is crowded, generic, factually unsafe, or unreadable at its actual placement size.

## 7. Recompose from a reference

When the user supplies one approved reference and asks for layout variation, separate invariants from variables before editing.

Lock as invariants when present:

- exact copy and content order;
- Product identity and color/type roles;
- evidence meaning and screenshot sequence;
- recurring annotation, border, shadow, and background language;
- rights, privacy, and factual boundaries.

Vary only the declared composition axes: focal weight, reading path, panel geometry, overlap, crop, alignment, and whitespace rhythm. Test materially different structures rather than palette variants. A useful three-direction range is:

1. conservative recomposition with familiar hierarchy;
2. structural recomposition with a new reading path;
3. proof-first recomposition that changes visual weight to match the content claim.

Treat a provider edit containing Product UI, citations, logos, statistics, or dense exact text as an analysis-only effect even when it looks faithful. Image models may redraw those pixels. Select the effect for its composition, then classify every zone as `retain`, `replace`, or `reject`. Preserve the selected geometry while replacing identity, exact copy, and evidence from deterministic Product-owned sources before formal use.

Bind every annotation to a concrete target. Create screenshot annotations in the screenshot's own coordinate system before scaling or placing the annotated screenshot.

Do not use arrows or leader lines for screenshot annotations by default. Use a short dashed underline for a text row, citation, or phrase. Use a thin closed circle or rounded outline for a control, region, or non-text object. Keep the mark inside or immediately adjacent to the target bounds. When a mark cannot identify one exact object unambiguously, remove it instead of positioning it approximately. Use numbering, alignment, or a simple spine without arrowheads for sequence when no point target is required.
