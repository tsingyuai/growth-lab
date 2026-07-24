---
name: create-seo-page
description: Design, write, and implement a high-value SEO page from demand research and live SERP evidence. Use when creating or redesigning an SEO landing page, matching page shape to search intent, writing metadata and page copy, improving information gain and content effort, adding structured data and internal links, or implementing the page in an existing product repository.
---

# Create an SEO page

Turn validated demand and SERP evidence into a complete page in the product's existing framework and design system.

Read [content-quality.md](references/content-quality.md) before drafting.

## Require useful inputs

Recover or obtain:

- target user and search situation;
- primary query family and intent;
- leading pages and their top-to-bottom block descriptions;
- information-gain gaps;
- product capability and desired user action;
- brand, legal, technical, and source constraints.

If research is missing, report the missing evidence to the calling Model before designing the page.

## Match the page shape to intent

Infer the expected shape from current winning results:

- tool intent → a working tool or direct product action;
- template/resource intent → a browsable collection with meaningful previews;
- how-to intent → a complete guide with concrete steps and examples;
- comparison intent → explicit criteria, evidence, and tradeoffs;
- solution intent → a problem-specific landing page with proof and a real path to action.

Use a hybrid when the product can fulfill the task directly: satisfy the informational expectation, then expose the product action at the moment it becomes useful.

## Design before implementation

Write a concise page design document containing final metadata, the page blocks in display order, and the facts and sources the page will use.

For the page structure, write one sentence per block describing exactly what appears. Derive the sequence from the observed winner pages and the product's useful difference. Keep research rationale outside the block list.

Use final title, description, and canonical copy in the design document. Associate every non-obvious number or factual claim with its source before writing the page.

## Create information gain

Give the visitor material that supports action or judgment:

- concrete procedures and examples;
- quality criteria, rubrics, and thresholds;
- real product behavior or firsthand evidence;
- original analysis of relevant data;
- copyable tables, checklists, or artifacts;
- authoritative primary sources;
- constraints, edge cases, and failure modes.

Aggregate resource links with classification and commentary when resource discovery is the task. Preserve original attribution and source links.

## Write the page

- Lead with the answer, product action, or useful choice implied by the intent.
- Use short direct sentences and one stable term for each concept.
- Make each section independently understandable and extractable.
- Put useful detail on the page before asking for conversion.
- Use evidence where it adds information. Keep common knowledge concise.
- Give the page a visible owner or author and update date when the product supports them.
- Connect conversion to the task the visitor came to complete.

Write a meta description around one information-rich point, method, limitation, or result. Use a natural complete sentence.

## Add page images

Define what each image must explain or demonstrate. Invoke `$generate-image` for generated assets. Prefer real screenshots for product behavior. Add descriptive alt text, explicit dimensions, stable filenames, and appropriate compression.

## Implement in the product

Follow the repository's framework, components, visual system, route conventions, and development workflow. Add the elements appropriate to the page:

- title and meta description;
- canonical URL;
- Open Graph and social metadata;
- relevant schema.org structured data;
- one descriptive heading hierarchy;
- contextual internal links;
- sitemap participation;
- source links and update signals;
- responsive and accessible content.

Run the product's own formatting, type, build, route, SEO, and accessibility checks. Use Runtime-native browser testing for the rendered page.

Return the implemented and locally verified page to the calling Model for adversarial review and release coordination.
