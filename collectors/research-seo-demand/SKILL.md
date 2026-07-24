---
name: research-seo-demand
description: Research and prioritize SEO demand using product context, keyword-family expansion, live SERPs, autocomplete, competitor discovery, and optional Bing Webmaster keyword statistics. Use when finding hot keywords, validating search demand, identifying user search intent, comparing keyword families, studying leading SERP pages, or selecting an SEO page opportunity.
---

# Research SEO demand

Discover what users search for, verify the demand, and return evidence that another Skill can use to create a page.

Use the Runtime's native browser, search, page inspection, and extraction capabilities. Create no browser wrapper or scraping script.

## Start from the product

Read the product code, documentation, public pages, current conversion paths, customer language, internal search terms, support conversations, and available growth evidence. State:

- the user and situation;
- the job they want to complete;
- the product action that resolves it;
- the market and language being researched.

## Expand keyword families

Explore each relevant family separately so their demand can be compared:

| Family | Expansion method |
|---|---|
| Core concepts | domain nouns, task names, category names |
| Scenarios | scenario × object or document type |
| Actions and outcomes | generate, create, convert, fix, improve, learn |
| Tools | feature, format, integration, and conversion phrases |
| Resources | templates, examples, checklists, downloads, standards |
| Competitors | category leaders and niche products discovered in SERPs |
| Questions | how, which, why, cost, quality, risk, comparison, failure |

Use live autocomplete, related searches, SERP titles, communities, product reviews, and support language to find the expressions users already use. Discover niche competitors from repeated SERP domains, then test their brand terms.

Check ambiguous words by reading their live SERP. Separate mixed intents before interpreting demand.

## Validate demand

When `BING_WEBMASTER_API_KEY` is available, call:

```bash
node collectors/bing-webmaster/bing-webmaster.mjs keyword-stats \
  --country <country> --language <language> \
  --input <keywords-file> --out <output-file>
```

Query at most 20 terms per batch and cool down between batches. For a large study, include one known-volume control term in each batch.

Interpret the response with these rules:

- Compare head terms with head terms and compound terms with compound terms.
- Treat exact impressions as a comparable demand floor.
- Treat an empty response as unavailable evidence. Triangulate with live SERPs and other sources.
- Use peak-to-average differences to identify seasonality and publish before the peak.
- Judge intent fit before volume. A high-volume phrase matters when the product satisfies its task.
- Use low-volume questions as supporting sections or AI-answer material when they reveal a real user concern.

## Read the live SERP

Use the Runtime browser with the target market and language. Verify that the rendered results remain relevant to the full query. Re-run suspicious results in a normal signed-in browser session when the engine appears to degrade or rewrite the query.

For each promising query:

1. Inspect the first three to five relevant pages.
2. Note repeated domains and pages across related terms.
3. Classify the winning shape: tool, catalog, guide, comparison, solution page, community answer, or hybrid.
4. Describe each page from top to bottom in one sentence per visible block.
5. Compare search presentation, user value, conversion path, information density, proof, and unique information.
6. List questions, evidence, tools, examples, or quality criteria the leading pages leave unresolved.

## Select the opportunity

Recommend a page when the evidence supports:

1. observable demand;
2. a clear and stable intent;
3. product ability to fulfill the task;
4. an information, utility, or experience gap;
5. a credible path from search visit to product outcome.

Return the selected query family, intent, seasonality, winning page shape, leading references, information-gain gaps, product fit, risks, and the evidence behind the recommendation. Use a task-appropriate Markdown, CSV, JSON, or HTML file.
