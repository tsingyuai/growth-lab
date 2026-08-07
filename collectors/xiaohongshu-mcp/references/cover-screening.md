# Xiaohongshu promotional cover screening

Use this gate when a social-content run needs a public note as an analysis-only visual learning sample. The goal is not to find the most engaged note; it is to find a note whose cover and card system are already suitable for product communication.

## Retrieval

Use product-oriented query language in addition to the content topic, for example tool recommendations, workflow demonstrations, product tutorials, and before/after product use. A purely informational query often returns raw documents, lecture notes, memes, or dense templates.

Download the full first-run cover pool (recommended 25) and inspect every numbered cover sheet before requesting any note details. Visible engagement is supporting evidence only.

## Hard rejection gate

Reject a cover before scoring when any condition applies:

- raw paper/document screenshot, unstructured app screenshot, ordinary photo, or meme without a designed promotional hierarchy;
- no dominant hook readable at phone size;
- dense paragraph/template content with no clear visual center;
- no substantial proof/content zone that could hold a real Product screenshot, diagram, comparison, or structured example;
- copied-template, academic-misconduct, misleading-outcome, privacy, or rights risk;
- topic or audience mismatch.

Color is not a hard gate. Palette can be adapted later.

## Quality score

Score only covers that pass the hard gate:

| Dimension | Weight | Pass signal |
| --- | ---: | --- |
| Promotional hierarchy | 25 | one dominant hook, supporting line, then proof/content |
| Content visualization | 20 | the picture communicates a method, result, workflow, or comparison |
| Proof zone | 20 | real screenshot or structured evidence is a major visual area, not decoration |
| Layout and whitespace | 15 | grouped annotations, stable alignment, controlled density |
| Mobile readability | 10 | hook and key labels survive thumbnail/phone viewing |
| Product adaptability | 10 | transferable structure without copying visual identity |

Require at least 75/100. Record the dimension scores and one rejection reason for every reviewed cover. It is valid for all 25 covers to fail.

## Detail, autonomous selection, and user recovery

Fetch detail images only for 3-8 covers that passed the gate. Inspect every image in each selected note. Under an explicitly approved autonomous policy, select exactly one qualifying reference internally and do not display its image by default. The internal file remains available to the renderer but must not be copied into the final package, normal response, or publishing handoff.

When the user must choose or explicitly asks to inspect the evidence, present titles, scores, fit/risk notes, and clean public Xiaohongshu URLs. Inline candidate images may be shown only for that source-review decision; never expose signed URLs, `xsecToken`, cookies, or a local filesystem path. A loopback preview may be used as a convenience, but it must never serve the repository root, `.env`, login state, or unrelated Memory.

If every candidate fails, do not silently continue or force a primary. Give the user the Agent's own judgment: state that the batch is unsuitable and summarize concrete rejection reasons such as missing proof zones, weak mobile hierarchy, raw screenshots, dense text, rights risk, or product mismatch. Then ask whether the user wants to provide a Xiaohongshu note they consider suitable. A new product-oriented query is the alternative only after this decision is visible.
