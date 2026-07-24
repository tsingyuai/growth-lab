---
name: run-seo-page-loop
description: Run an end-to-end SEO page observation-action-review loop with persistent Memory, from keyword demand research through SERP analysis, page creation, image generation, live-page verification, IndexNow submission, Bing Webmaster measurement, and the next iteration. Use when creating or improving an SEO landing page, researching high-potential search terms, submitting a page for indexing, evaluating a page with Bing data, or reviewing SEO outcomes.
---

# Run the SEO page loop

Operate inside the product workspace. Let the current Codex or Claude Code session control the work. Use `memory/run-seo-page-loop/` as this Model's persistent Memory.

This Model is an observation-action-review loop:

```text
Read Memory → Observe → Decide → Act → Review → Write Memory → Next observation
```

Read [memory.md](references/memory.md) before starting a run. Recover relevant historical observations, previous actions, outcomes, conclusions, and next-action recommendations. At the end of useful work, persist the new operational evidence, analysis, synthesis, and next actions back to this Model's Memory.

## Keep these boundaries

- Use the Runtime's browser, search, page inspection, screenshot, and local web-testing capabilities directly.
- Use existing product commands and tests to inspect routes, metadata, rendering, links, responsive behavior, and accessibility.
- Add a Client only for an external API or action the Runtime cannot perform natively.
- Shape research files and the final HTML analysis around the current question. Create no fixed application schema, database, dashboard, or workflow state.
- Store time-based operational evidence, analysis, reviews, and next-action recommendations in `memory/run-seo-page-loop/`.
- Apply improvements to the loop methodology directly to this Model's `SKILL.md` or references. Keep methodology-change suggestions out of Memory.
- Read every credential from environment variables. Keep secrets out of source, prompts, output files, command output, URLs shown to users, and commits.

## Run the loop

### 1. Understand the product and choose the search opportunity

Read the product code, public pages, documentation, current conversion paths, and available growth evidence. Define the target user, their search situation, and the product action that genuinely resolves their need.

Read [keyword-research.md](references/keyword-research.md), then:

1. Build keyword families from user problems, concepts, scenarios, actions, tools, resources, competitors, and natural-language questions.
2. Use Runtime search and browser capabilities to inspect autocomplete, related searches, communities, competitor language, and live SERPs.
3. When `BING_WEBMASTER_API_KEY` is available, query comparable weekly demand with the Bing collector.
4. Choose a page opportunity from demand, intent fit, competition, seasonality, product fit, and the evidence gap the page can fill.
5. Save research artifacts in a task-appropriate form, then preserve useful dated observations and conclusions in this Model's Memory.

### 2. Learn from the winning pages

Open the live SERP results with the Runtime browser. Inspect the leading pages that match the target intent. Study:

- search presentation: title, description, freshness, rich results;
- page shape: tool, landing page, guide, catalog, comparison, or hybrid;
- page sequence: hero, answer, proof, examples, tools, conversion, related topics;
- information gain: original examples, data, firsthand evidence, useful artifacts, authoritative sources;
- conversion path: what the page lets the visitor accomplish next;
- content and image quality: relevance, clarity, uniqueness, and trust.

Identify the shared intent pattern and the unanswered questions. Use those findings to write a concise page brief. Use Runtime-native browsing and inspection throughout; create no scraper or browser wrapper.

### 3. Create the page in the product

Read [page-creation.md](references/page-creation.md). Implement the page in the product's existing framework and design system. Match the search intent, deliver the useful answer on the page, and connect the page to a real product action.

Include the metadata, canonical URL, social preview, structured data, sitemap entry, internal links, author or owner signal, update date, citations, and accessible content that fit the product and page type. Use the product's own conventions and validation commands.

### 4. Create page images

Read [image-creation.md](references/image-creation.md). Inventory the exact images the page needs. Use the Runtime's native image-generation capability when available. Reuse product screenshots and existing brand assets when they explain the product more accurately.

For each generated image, define its purpose, subject, composition, aspect ratio, palette, exact text, and exclusions. Inspect the result visually, verify every rendered word, place the selected asset in the product's normal public asset directory, and add descriptive alt text and explicit dimensions.

When the product workspace provides an external image Client, read its API key and base URL from its documented environment variables. Never place a key in a script, prompt file, README, generated asset metadata, or committed environment file.

### 5. Verify, deploy, and notify IndexNow

Run the product's relevant build, type, lint, route, and SEO checks. Use Runtime-native browser testing against the local page and then the deployed page. Verify the rendered content, metadata, canonical, structured data, images, internal links, viewport behavior, console, network failures, and public accessibility.

After the live URL returns the intended page:

1. Confirm the IndexNow key file is publicly reachable at the configured key location.
2. Set `INDEXNOW_KEY` and `SITE_URL` in the local environment.
3. Submit the live URL with `executors/indexnow/submit-indexnow.mjs`.
4. Use Bing URL Inspection through the Runtime's signed-in browser session, or `url-info` through the Bing collector, to follow index status.

### 6. Measure the page and decide the next iteration

Read [measurement.md](references/measurement.md). Preserve the page URL, launch date, target intent, and baseline evidence in this Model's Memory in a form useful to the current analysis.

When Bing has accumulated data:

1. Read page and query performance with `page-stats` and `page-query-stats`, or export the equivalent data from Bing Webmaster Tools through the Runtime browser.
2. Compare impressions, clicks, click-through rate, average impression position, average click position, queries, and the page's product outcomes across comparable periods.
3. Inspect Bing AI Performance in the signed-in browser when available: cited pages, citations, and grounding queries.
4. Diagnose discovery, ranking, snippet, intent, content, and conversion separately.
5. Generate a standalone HTML review for this page when a visual comparison helps. Build the HTML directly from the current evidence, open it with the Runtime browser, and keep it in this Model's Memory when it supports future comparison.
6. Choose the next action: strengthen the page, improve the snippet, add missing evidence, adjust conversion, build a supporting page, or leave the page to accumulate more data.
7. Write the dated evidence, summary, review, and next-action recommendation to `memory/run-seo-page-loop/`. Link the entry to the earlier observation or action it evaluates.

Return the next decision to the beginning of the loop.

## Clients

```bash
# Keyword demand
node collectors/bing-webmaster/bing-webmaster.mjs keyword-stats \
  --country cn --language zh-CN --input seo-work/keywords.txt \
  --out seo-work/keyword-stats.json

# Site and page performance
node collectors/bing-webmaster/bing-webmaster.mjs page-stats \
  --site "$SITE_URL" --out seo-work/bing-pages.json

node collectors/bing-webmaster/bing-webmaster.mjs page-query-stats \
  --site "$SITE_URL" --page "$PAGE_URL" \
  --out seo-work/bing-page-queries.json

# IndexNow
node executors/indexnow/submit-indexnow.mjs "$PAGE_URL"
```

Read [security.md](references/security.md) before configuring any external Client.
