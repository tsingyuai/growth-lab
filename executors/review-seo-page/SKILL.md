---
name: review-seo-page
description: Adversarially review an SEO page from the target user's real search situation, identify intent mismatch, low-information sections, template-like content, repeated conversion, AI-sounding language, terminology drift, weak metadata, unsupported claims, and irrelevant images, then fix the page. Use when reviewing SEO content quality, reducing generic or AI-like copy, checking image relevance, or deciding whether to keep, merge, rewrite, or remove a page.
---

# Review an SEO page adversarially

Assume each page block must earn its place. Keep content that directly helps the target user understand, decide, or act.

Use Runtime-native browser inspection on the rendered page. Review the implementation and the actual user-visible result.

## Establish the user task

Write down:

- target user;
- search query and intent;
- problem at page entry;
- useful result expected before leaving;
- product action relevant to that result.

Treat intent mismatch as the highest-severity problem.

## Review from top to bottom

For every visible block:

1. State what it contributes to the user's task.
2. Remove material the user is unlikely to need.
3. Check whether it adds a method, criterion, example, fact, tool, or decision.
4. Check whether the same block could survive unchanged under a neighboring page title.
5. Check factual support, terminology, image relevance, and conversion pressure.
6. Check the rendered layout, links, mobile behavior, accessibility, console, and failed requests with Runtime-native tools.

## Apply adversarial tests

- Deletion test: remove the block when the user loses nothing.
- Reversal test: replace advice whose opposite is obviously absurd with a specific statement.
- Title-swap test: rewrite content that fits several neighboring pages unchanged.
- Brand-removal test: remove or specify copy that becomes empty promotion after the brand name disappears.
- Evidence test: remove or source non-obvious facts and numbers.
- Image-text test: replace an image that does not show the task or result claimed beside it.
- Conversion test: consolidate repeated calls to action and keep the action aligned with the search task.

## Review metadata

Make the title accurately identify the page and its intent. Write the meta description around one information-rich point, method, limitation, or result. Use a natural complete sentence. Check canonical URL, social metadata, structured data, and sitemap participation against the rendered page.

## Rewrite plainly

- Use short sentences with one idea each.
- Define concepts directly.
- Use common domain terminology consistently.
- Remove slogans, suspense openings, invented jargon, empty transitions, parallel filler, and duplicated claims.
- Write affirmative definitions directly.
- Give every effect claim an object, condition, and concrete meaning.
- Keep internal implementation names out of user-facing copy.
- Apply corrected terminology directly throughout the page.

## Report and fix

Classify findings:

- `P0`: search-intent or user-task mismatch;
- `P1`: low value, repetition, template-like content, unsupported claims, excessive conversion, or image mismatch;
- `P2`: awkward language, AI-like tone, terminology drift, metadata weakness, or minor presentation issue.

For each finding, include location, shortest identifying excerpt, user impact, action, and replacement copy when applicable. End with a page decision: keep, merge, rewrite, or remove.

When authorized to edit, implement the fixes, rerun relevant product checks, and inspect the rendered page again.
