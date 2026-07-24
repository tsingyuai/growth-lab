---
name: review-seo-performance
description: Evaluate an SEO page using Bing Webmaster page and query data, index status, product outcomes, and optional Bing AI Performance evidence, then generate a task-specific HTML review and recommend the next action. Use when reviewing SEO results, diagnosing weak impressions, rankings, click-through rate, intent fit, content quality, conversion, AI citations, or deciding how to iterate a published page.
---

# Review SEO performance

Evaluate a published page against its original intent and product outcome. Use comparable periods and account for launch date and seasonality.

## Collect evidence

Use the Bing collector or Runtime browser access to Bing Webmaster Tools:

```bash
node collectors/bing-webmaster/bing-webmaster.mjs page-stats \
  --site "$SITE_URL" --out <page-stats-file>

node collectors/bing-webmaster/bing-webmaster.mjs page-query-stats \
  --site "$SITE_URL" --page "$PAGE_URL" --out <query-stats-file>

node collectors/bing-webmaster/bing-webmaster.mjs url-info \
  --site "$SITE_URL" --url "$PAGE_URL"
```

Read:

- crawl and index status;
- impressions and queries;
- clicks and click-through rate;
- average impression and click positions;
- changes after page or snippet updates;
- page-level product actions, activation, revenue, or another relevant outcome;
- citations, cited pages, and grounding queries from Bing AI Performance when available.

## Diagnose the constraint

- Discovery: the intended canonical URL has not been crawled or indexed.
- Demand: the selected query family produces little observable demand.
- Ranking: impressions exist while positions remain weak.
- Snippet: positions are competitive while click-through remains weak.
- Intent: arriving queries and the page task diverge.
- Content: competing pages provide stronger evidence, utility, freshness, or clarity.
- Conversion: the page satisfies search intent while producing little product movement.
- Visibility without traffic: AI systems cite the page while users rarely click through.

Separate evidence from interpretation. Compare against previous Memory entries before declaring a trend.

## Create the review

Generate a standalone HTML review when visual comparison helps. Shape it around the current evidence. Useful views include period comparison, query table, position distribution, product outcomes, annotated findings, and a recommended action.

Create the HTML directly in `memory/run-seo-page-loop/` or the active Model's Memory, then open it with the Runtime browser. Keep source exports beside it when they support future comparison.

Recommend one primary next action and explain the evidence:

- strengthen the current page;
- improve title and snippet;
- add missing evidence or utility;
- align conversion with intent;
- create a supporting page;
- resolve discovery or canonical issues;
- wait for a defined period to accumulate data.
