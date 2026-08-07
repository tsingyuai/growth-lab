---
name: run-seo-page-loop
description: Run an SEO page observation-action-review loop with persistent Memory by coordinating demand research, page creation, adversarial review, image generation, IndexNow submission, and performance review. Use when taking an SEO page from opportunity discovery through publication, measurement, iteration, or continuing a previous SEO loop from Memory.
---

# Run the SEO page loop

Coordinate the loop inside the current Product workspace. Let the current Codex or Claude Code session control the work. Use `<current-product-workspace>/memory/run-seo-page-loop/` as this Model's persistent Memory. Determine the Product workspace before reading or writing Memory; never combine different Products in one Memory namespace.

```text
Read Memory → Observe → Decide → Act → Review → Write Memory → Next observation
```

Read [memory.md](references/memory.md) before starting. Recover relevant observations, actions, outcomes, conclusions, and next-action recommendations.

When the user requests recurring or scheduled execution, read root `AUTOMATION.md` and [automation.md](references/automation.md). Test the same scope manually before scheduling it.

## Boundaries

- Keep this Model focused on when and why the loop moves between observation, decision, action, and review.
- Delegate data-collection methods and source-specific interpretation to Collectors.
- Delegate creation, implementation, publishing, inspection, and performance-review techniques to Executors.
- Use Runtime-native browser, search, page inspection, screenshot, and local web-testing capabilities directly.
- Add a Client only for an external API action the Runtime cannot perform natively.
- Create no fixed schema, database, dashboard, workflow state, or task queue.
- Store dated operational evidence, analysis, outcomes, and next-action recommendations in Memory.
- Apply improvements to the loop itself directly to this Model. Keep methodology-change suggestions out of Memory.
- Treat research, product-code implementation, deployment, IndexNow submission, and automation as separate scopes. Approval for one does not authorize the next.
- Keep detailed query research, competitor-page breakdowns, source limitations, and technical checks in Memory. In the default user-facing result, translate them into one opportunity or constraint, a short plain-language reason, the next available action, and one confirmation question. Expand the evidence when the user asks why, requests sources, or challenges the conclusion.

## 1. Read Memory

Read recent Memory entries and older entries relevant to the product, page, query family, or pending action. Establish what is already known, what was attempted, what happened, and which recommendation should now be tested.

## 2. Observe

Invoke `$research-seo-demand` to collect and interpret current search demand and live SERP evidence. Combine it with product context and relevant Memory.

For an existing Product site, invoke `$inspect-seo-content-inventory` before selecting a new content action unless a recent inventory already covers the relevant site state and topic. Re-run it when the Sitemap, route set, publishing system, or candidate topic has materially changed. Use its output as evidence about what exists; do not let it make the action decision.

When the loop begins from an existing page, invoke `$review-seo-performance` first to observe its current outcome.

Persist useful raw evidence and a dated observation in the current Product workspace's `memory/run-seo-page-loop/`.

When the user provides a webmaster CSV or JSON export, invoke `$read-webmaster-export` and preserve its provenance and limitations.

## 3. Decide

Shortlist a small set of distinct SEO directions and compare their value and execution difficulty using the criteria in `$research-seo-demand`. Recommend the high-value, low-difficulty direction first. Return two or three meaningful alternatives when supported, with a short reason why each ranks lower. Do not turn alternatives into approved actions.

For each direction, compare the demand with the current content inventory and decide whether the candidate action is create, improve, merge, keep, investigate, or wait. A duplicate-title, similarity, orphan, canonical, thin-content, or path-scale signal is not sufficient by itself; inspect representative pages, user intent, Product purpose, and available performance evidence before choosing.

Before choosing or creating the primary page action, confirm that the current observation contains a competitor-page breakdown for its selected query family. The breakdown must cover three to five relevant leading pages and include:

- each page's search presentation and winning page shape;
- a top-to-bottom description of its visible blocks;
- reading and conversion hooks, information density, user value, and tone;
- evidence, unique information, authorship, and negative quality signals;
- an information-gain gap synthesized across the leading pages.

Do not invoke `$create-seo-page` from keyword volume, result snippets, or a list of ranking URLs alone. When this evidence is absent, return to Observe and complete it with `$research-seo-demand`.

An alternative can remain at preliminary confidence in the user-facing option list. If the user chooses it, return to Observe and complete the same three-to-five-page analysis before creation.

Choose one primary action supported by current evidence and historical Memory. State the expected observable result and the evidence that would confirm or challenge the decision. Preserve the ranked alternatives in Memory so a later run can reconsider them when evidence or constraints change.

Before invoking `$create-seo-page`, identify the exact current Product Memory report that contains the selected direction's completed competitor-page analysis. Pass that report and any separately stored source evidence into the creation context. A conclusion copied into conversation is not a substitute for the persisted evidence. If the report does not match the selected query family, market, language, Product, or current site state, return to Observe and refresh it.

Before implementation, identify the intended product outcome and the smallest available measurement path from page visit to product action. Prefer page-level events for CTA, registration, activation, or revenue when the product already supports them. Record missing instrumentation rather than inventing attribution.

Possible actions include creating a page, improving an existing page, changing its snippet, strengthening evidence, adjusting conversion, resolving discovery problems, creating a supporting page, or waiting for a defined observation window.

## 4. Act

Act only within the confirmed scope.

### Build a release candidate

1. Invoke `$create-seo-page` with the exact persisted research report and selected action so it can read and trace the underlying competitor evidence before designing.
2. Invoke `$generate-image` when the page needs a generated or edited asset.
3. Invoke `$review-seo-page` before release and apply accepted fixes.
4. Use the product's own checks and Runtime-native browser testing.

Return the locally verified release candidate. Do not deploy merely because implementation was approved.

### Release

Deploy only after explicit release approval and through the product's existing release process. If no product repository or release process is available, return the design, copy, assets, or patch instructions instead of implying deployment.

Record the canonical URL, launch time, target intent, search baseline, CTA, and any available page-to-product events. Do not claim that organic traffic caused registration or activation without an appropriate measurement path.

### Submit for discovery

After the canonical live URL is publicly accessible, submit it with `executors/indexnow/submit-indexnow.mjs` only when live submission is in the approved scope. A successful API response is submission evidence, not proof of indexing or ranking.

Record the action, live URL, launch time, target intent, and baseline evidence in Memory.

## 5. Review

At the appropriate observation time, invoke `$review-seo-performance`. Compare current evidence with the baseline and previous Memory. Determine whether the action improved discovery, ranking, click-through, intent fit, content usefulness, product outcomes, or AI visibility.

Separate search visibility, page engagement, registration, activation, and revenue. State when product outcomes are unavailable or only correlated with the SEO action.

Invoke `$review-seo-page` again when performance evidence points to a page-quality or intent problem.

## 6. Write Memory and continue

Write the dated operational evidence, analysis, summary, outcome, and recommended next action to the current Product workspace's `memory/run-seo-page-loop/`. Link the entry to the earlier observation or action it evaluates.

When the run reveals a better loop, edit this Model's `SKILL.md` or `references/memory.md` directly. Record the real operational outcome in Memory and the improved method in the Model.

Return the selected next action to the beginning of the loop. Do not make the user read the internal evidence report before deciding whether to continue.
