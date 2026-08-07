---
name: inspect-seo-content-inventory
description: Inspect a product's existing public SEO content from Sitemap XML, URL lists, public HTML, or local HTML snapshots before choosing whether to create, improve, merge, keep, or investigate a page. Use when auditing page inventory, indexability, canonical signals, path-scale patterns, internal links, duplicate titles, similar content, orphan candidates, or possible keyword cannibalization without automatically changing the site.
---

# Inspect SEO content inventory

Collect repeatable facts about what the Product already publishes. Return evidence to the calling Model; do not turn signals into automatic create, merge, delete, redirect, canonical, or `noindex` decisions.

## Establish the question and scope

Confirm:

- current Product workspace and canonical site;
- whether the question concerns a new topic, an existing page, a site-wide audit, or an unexpected URL pattern;
- authorized sources: public Sitemap and pages, user-provided URL list, local snapshots, or Product repository;
- inspection cap and output location in the current Model Memory.

Keep different Products in their own workspaces. Do not crawl authenticated, private, preview, account, or user-specific content merely because a URL is discoverable.

## Run the deterministic inventory

Use `scripts/inspect_seo_content_inventory.py` for Sitemap, URL-list, and static HTML inspection.

Public Sitemap example:

```bash
python collectors/inspect-seo-content-inventory/scripts/inspect_seo_content_inventory.py \
  --sitemap https://example.com/sitemap.xml \
  --base-url https://example.com \
  --max-pages 200 \
  --out <current-product-memory>/seo-content-inventory.json
```

Use repeatable `--include-regex` and `--exclude-regex` filters when the authorized scope covers only part of a public site or when account, preview, user-specific, or irrelevant routes must not be inspected.

Local snapshot example:

```bash
python collectors/inspect-seo-content-inventory/scripts/inspect_seo_content_inventory.py \
  --snapshot-dir <rendered-html-directory> \
  --base-url https://example.com \
  --out <current-product-memory>/seo-content-inventory.json
```

The script:

- reads nested Sitemap indexes and URL sets up to explicit limits;
- groups URL paths after replacing likely identifiers with placeholders;
- samples each path pattern instead of blindly fetching every generated URL;
- respects `robots.txt` for public HTTP inspection;
- records status, final URL, title, description, canonical, robots, headings, visible-text size, structured-data types, and links;
- reports duplicate titles and canonicals, exact-content groups, similar-page candidates, unlinked-page candidates, and page-level quality signals;
- states limitations caused by static HTML, sampling, missing rendered content, or incomplete link coverage.

Use Runtime-native browser inspection when client rendering, consent gates, localization, or login changes the visible page. Use Product repository routes as additional evidence when public HTML is incomplete; do not invent a framework-specific scanner.

## Interpret signals without formulas

Treat the output as leads for investigation:

- a repeated path pattern can be an intentional programmatic asset or an uncontrolled URL explosion;
- similar titles can represent cannibalization or deliberately distinct audience pages;
- a different canonical can be correct consolidation or a configuration error;
- an unlinked page can be orphaned or reachable only through client-rendered navigation;
- thin static HTML can be a weak page or a client-rendered application shell.

Before recommending an action, inspect representative pages, their user tasks, available search performance, Product behavior, publishing intent, privacy boundary, and historical Memory. Never infer `noindex`, deletion, merge, or redirect from one signal alone.

## Return evidence to the Model

Return:

- source, collection time, limits, and Product scope;
- inventory size and major URL-pattern groups;
- indexability, canonical, status, internal-link, duplication, and similarity signals;
- representative URLs requiring human or browser inspection;
- what the signals could mean and what remains unknown;
- the smallest next observation needed for a create, improve, merge, keep, or investigate decision.

Keep the full inventory in the current Product's Model Memory. The default user-facing response should translate it into one understandable constraint or opportunity and offer detailed evidence only when requested.
