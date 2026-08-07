---
name: review-social-content
description: Adversarially review social content packages for factual support, copyright, compliance, platform fit, brand tone, AI-like language, visual quality, attribution, and publication readiness. Use before human-assisted publishing, WeChat draft/API actions, Xiaohongshu publishing packages, or social content reuse.
---

# Review social content

Assume every claim, image, and CTA must earn its place. Block publication when critical evidence or authorization is missing.

## Required evidence

Read the content package, product claim ledger, social research handoff, asset inventory, and platform policy notes. When card visuals are in scope, also read the visual manifest, visual specification, effect/final review, provenance, and mechanical validation result from `$render-social-card-pack`. If required evidence is missing, return to the calling Model instead of reviewing from conversation memory.

## Review layers

Check:

1. Product facts: every non-obvious claim traces to the ledger.
2. Platform fit: title, opening, card/article rhythm, CTA, tags, and expected user action match platform norms.
3. Copyright: no copied competitor wording, image, layout identity, proprietary example, or screenshot.
4. Privacy: no private user data, unpublished account data, credentials, or sensitive screenshots.
5. Compliance: no academic misconduct, fake citation, guaranteed detector bypass, fake research result, medical/legal/financial overclaim, or misleading ad claim.
6. Brand: tone, terminology, visual usage, and caveats fit the Product.
7. AI trace: remove generic filler, repetitive list patterns, unsupported superlatives, and vague productivity promises.
8. Measurement: CTA, link, UTM, code, or review window is defined when outcomes will be claimed later.
9. Visual production: formal card copy matches the approved draft; Product UI and evidence are real; generated effects, raw outputs, corrected renders, and publishable assets are separated; the manifest matches the final card order.

## Tests

- Claim deletion test: remove claims that do not change the useful message or lack evidence.
- Competitor synthesis test: keep reusable platform patterns, remove copied expression.
- Screenshot truth test: a product screenshot must show a real product state and must not expose private data.
- Platform swap test: content that works unchanged across Xiaohongshu and WeChat is probably under-adapted.
- CTA alignment test: the requested action must follow naturally from the user's current task.
- Boundary test: caveats must be visible where the risky claim appears, not hidden at the end.
- Visual-source test: generated logos, fake Product UI, invented citations/statistics, or competitor reference assets cannot appear as Product evidence.
- Single-reference test: visual specifications and generation prompts use only the validated primary external learning sample; rejected candidates contribute no visual rules or reference images.
- Full-effect correction test: local corrections preserve the selected composition and do not introduce overlaps, mismatched spacing, or a second unrelated layout.
- Render-manifest test: every publishable card appears once in the manifest, passes mechanical validation, and remains readable in a phone-scale preview.

## Findings

Classify:

- `P0`: unsupported sensitive claim, copied material, privacy leak, fake Product evidence, missing publication authorization, or platform-policy blocker.
- `P1`: weak value, misleading hook, excessive conversion pressure, ungrounded image, unclear attribution, or serious platform mismatch.
- `P2`: wording, rhythm, AI-like tone, minor visual, tag, or metadata issue.

For each finding, include location, shortest identifying excerpt, impact, fix, and replacement copy when useful.

End with one decision: `block`, `revise`, `ready for human publishing`, `ready for draft API`, or `ready for live API approval`.
