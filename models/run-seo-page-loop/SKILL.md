---
name: run-seo-page-loop
description: Run an SEO page observation-action-review loop with persistent Memory by coordinating demand research, page creation, adversarial review, image generation, IndexNow submission, and performance review. Use when taking an SEO page from opportunity discovery through publication, measurement, iteration, or continuing a previous SEO loop from Memory.
---

# Run the SEO page loop

Coordinate the loop inside the product workspace. Let the current Codex or Claude Code session control the work. Use `memory/run-seo-page-loop/` as this Model's persistent Memory.

```text
Read Memory → Observe → Decide → Act → Review → Write Memory → Next observation
```

Read [memory.md](references/memory.md) before starting. Recover relevant observations, actions, outcomes, conclusions, and next-action recommendations.

## Boundaries

- Keep this Model focused on when and why the loop moves between observation, decision, action, and review.
- Delegate data-collection methods and source-specific interpretation to Collectors.
- Delegate creation, implementation, publishing, inspection, and performance-review techniques to Executors.
- Use Runtime-native browser, search, page inspection, screenshot, and local web-testing capabilities directly.
- Add a Client only for an external API action the Runtime cannot perform natively.
- Create no fixed schema, database, dashboard, workflow state, or task queue.
- Store dated operational evidence, analysis, outcomes, and next-action recommendations in Memory.
- Apply improvements to the loop itself directly to this Model. Keep methodology-change suggestions out of Memory.

## 1. Read Memory

Read recent Memory entries and older entries relevant to the product, page, query family, or pending action. Establish what is already known, what was attempted, what happened, and which recommendation should now be tested.

## 2. Observe

Invoke `$research-seo-demand` to collect and interpret current search demand and live SERP evidence. Combine it with product context and relevant Memory.

When the loop begins from an existing page, invoke `$review-seo-performance` first to observe its current outcome.

Persist useful raw evidence and a dated observation in `memory/run-seo-page-loop/`.

## 3. Decide

Before choosing a page action, confirm that the current observation contains a competitor-page breakdown for every candidate query being considered. The breakdown must cover three to five relevant leading pages and include:

- each page's search presentation and winning page shape;
- a top-to-bottom description of its visible blocks;
- reading and conversion hooks, information density, user value, and tone;
- evidence, unique information, authorship, and negative quality signals;
- an information-gain gap synthesized across the leading pages.

Do not invoke `$create-seo-page` from keyword volume, result snippets, or a list of ranking URLs alone. When this evidence is absent, return to Observe and complete it with `$research-seo-demand`.

Choose one action supported by current evidence and historical Memory. State the expected observable result and the evidence that would confirm or challenge the decision.

Possible actions include creating a page, improving an existing page, changing its snippet, strengthening evidence, adjusting conversion, resolving discovery problems, creating a supporting page, or waiting for a defined observation window.

## 4. Act

Coordinate the relevant Executors:

1. Invoke `$create-seo-page` to design and implement the page.
2. Invoke `$generate-image` when the page needs a generated or edited asset.
3. Invoke `$review-seo-page` before release and apply accepted fixes.
4. Use the product's own checks and Runtime-native browser testing.
5. Deploy through the product's existing release process.
6. After the live URL is publicly accessible, submit it with `executors/indexnow/submit-indexnow.mjs`.

Record the action, live URL, launch time, target intent, and baseline evidence in Memory.

## 5. Review

At the appropriate observation time, invoke `$review-seo-performance`. Compare current evidence with the baseline and previous Memory. Determine whether the action improved discovery, ranking, click-through, intent fit, content usefulness, product outcomes, or AI visibility.

Invoke `$review-seo-page` again when performance evidence points to a page-quality or intent problem.

## 6. Write Memory and continue

Write the dated operational evidence, analysis, summary, outcome, and recommended next action to `memory/run-seo-page-loop/`. Link the entry to the earlier observation or action it evaluates.

When the run reveals a better loop, edit this Model's `SKILL.md` or `references/memory.md` directly. Record the real operational outcome in Memory and the improved method in the Model.

Return the selected next action to the beginning of the loop.
