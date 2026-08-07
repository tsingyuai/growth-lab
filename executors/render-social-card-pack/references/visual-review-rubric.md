# Visual Review Rubric

## Effect selection

Score each candidate from 1 to 5:

| Dimension | Pass signal |
| --- | --- |
| Hook | first-card promise is understood quickly without exaggeration |
| Hierarchy | title, support, proof, and footer have an obvious reading order |
| Whitespace | density supports scanning and does not feel empty or cramped |
| Content selection | every retained block advances the card's one job |
| Product evidence | real screenshot or official asset proves the relevant claim |
| Evidence targeting | the exact UI object, output, or changed state is visible and directly supports the message |
| Platform fit | ratio, text size, sequence, and save/share value fit the target platform |
| Visual focus | one dominant element leads the eye without flat grids, crowding, or purposeless empty space |
| Series system | cards feel related without repeating one rigid layout |
| Brand fit | Product-owned visual evidence is respected without inventing rules |
| Correction feasibility | factual zones can be fixed locally without redesigning the card |
| Non-copying distance | output does not reproduce a reference's protected expression or identity |
| Content completeness | the card contains enough concrete explanation or proof to perform its declared job |
| Layout vitality | the composition has a deliberate reading path and does not reduce every role to the same rigid grid |

Reject a candidate regardless of score when it contains sensitive data, copied material, fake evidence, unsafe claims, or an inseparable fake Product UI.

Reject the package when prompts or `visual-spec.md` blend visual rules from more than one external learning sample, or when they use a candidate that is not the validated primary reference.

## Formal candidate gates

Require all:

1. Exact copy: every retained generated string matches locked copy; no malformed glyphs or extra text.
2. Evidence: logos, Product UI, citations, statistics, and sensitive claims come from approved deterministic sources.
3. Privacy: screenshots are public-safe or redacted; no account, customer, document, or private analytics leakage.
4. Mobile readability: title and core labels remain readable in a phone-scale contact sheet.
5. Screenshot readability: the evidence target remains legible in the final composed card, not only in the source screenshot.
6. Annotation accuracy: every marker lands on a concrete intended UI object and remains aligned after composition.
7. Composition: corrections preserve the selected layout, one dominant focus, useful breathing room, and no crowding or empty decorative frame.
8. Asset provenance: prompts, models, references, screenshots, rights, and local edits are recorded.
9. Mechanical result: manifest validator passes and preview assets load.
10. Platform boundary: no upload, draft, or publication occurred during rendering.

## AI artifact review

Inspect for malformed Chinese, fake interface chrome, impossible diagrams, invented documents, inconsistent icons, random microtext, decorative clutter, model watermarks, and repeated generic visual motifs. Prefer restrained flat structure when the subject does not require a concrete scene.

## Decisions

- `block`: rights, privacy, evidence, compliance, or structural failure.
- `revise`: correctable copy, visual, crop, hierarchy, or mobile-readability issue.
- `ready for social-content review`: visual production gates pass; publication still requires the downstream review and authorization path.

Never choose `ready` solely from scripts or a self-authored ledger. Inspect the final rendered pixels at full size and phone scale, record the result in `visual-quality-review.json`, and apply the non-compensating gate in `self-review-rework-gate.md`. The final pixels and their communication effect control the decision.
