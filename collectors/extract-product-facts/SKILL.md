---
name: extract-product-facts
description: Extract a traceable product claim ledger from product code, public pages, docs, screenshots, official materials, SOUL.md, and prior Growth Lab Memory for social content or campaign creation. Use when content must be grounded in real product facts, feature behavior, routes, screenshots, claims, caveats, compliance limits, or reusable product evidence before drafting.
---

# Extract product facts

Return a claim ledger to the calling Model. Do not create content, choose campaign angles, or publish.

## Scope

Use authorized sources:

- current Product workspace `SOUL.md`;
- product repository files, routes, metadata, components, analytics names, and documentation;
- public website pages, Sitemap, robots, rendered pages, screenshots, and official materials;
- prior Model Memory when the calling Model names it as evidence.

Keep stable product knowledge in `SOUL.md` only when it satisfies `DATA.md`. Keep campaign-specific claim ledgers in the calling Model Memory.

## Inspect

Collect only facts needed for the content decision:

- product identity, audience, scenario, value, and positioning;
- implemented features and user-visible workflows;
- public routes, app entry points, screenshots, and official assets;
- claims that appear on current pages or docs;
- analytics events or conversion paths relevant to the campaign;
- compliance, privacy, and brand constraints;
- outdated, ambiguous, or unsupported claims.

Distinguish:

- verified product fact;
- user statement;
- inference from code or page behavior;
- unverified claim;
- rejected or prohibited claim.

## Claim ledger

Return a table or structured section with:

- claim;
- status;
- source path or URL;
- collected time;
- where the claim may be used;
- required caveat or wording boundary;
- screenshot or asset reference when applicable;
- risk level and reason.

For academic products, explicitly evaluate claims about real citations, AI traces, originality, coverage, review quality, writing assistance, assignment completion, and user responsibility.

## Output

Write or return the ledger to the calling Model Memory. Do not copy sensitive source files, raw private analytics, credentials, unpublished customer data, or private user content.
