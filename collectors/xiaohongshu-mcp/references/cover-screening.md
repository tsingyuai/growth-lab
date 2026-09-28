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

## Detail and user choice

Fetch detail images only for 3-8 covers that passed the gate. Inspect every image in each selected note. Then show the user the qualifying candidates with actual inline images, titles, visible engagement, score, and concise fit/risk notes. A filesystem path or hyperlink alone is not a usable choice interface. Display at least the representative first image for every option directly in the conversation; provide paths only as supplemental access.

Before sending the choice response, verify that the response channel can render each image. If inline rendering is unavailable or cannot be confirmed, include the clean public Xiaohongshu note URL for every candidate in the same response. Never expose signed URLs, `xsecToken`, cookies, or a local filesystem path as the only way to make the choice. A loopback preview may be used as a convenience, but it never replaces the public-source fallback and must never serve the repository root, `.env`, login state, or unrelated Memory.

The user chooses the primary reference when they are present. An autonomous run may recommend one only when the approved run policy allows it. Never force a primary from an inadequate set; use a new product-oriented query instead.
