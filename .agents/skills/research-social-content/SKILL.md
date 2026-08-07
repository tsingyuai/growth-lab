---
name: research-social-content
description: Research public social content demand, competitor messaging, high-performing notes/articles, platform norms, content hooks, visual patterns, comments, and reusable non-copying lessons for Xiaohongshu, WeChat official account, or similar social channels. Use before creating platform-specific social content packages.
---

# Research social content

Discover platform-native content patterns and return an evidence handoff. Do not create final content, upload, log in, or publish.

## Establish scope

Confirm:

- Product workspace and calling Model Memory;
- platform: Xiaohongshu, WeChat official account, or another named channel;
- market, language, audience, product scenario, and topic;
- authorized sources: public pages, normal browser session, user-provided screenshots/exports, official analytics exports, or platform search;
- access limits and platform terms.

When public platform search is blocked, degraded, login-gated, or unstable, record the limitation. Use user-provided URLs, screenshots, exports, or official public pages as recovery paths.

## Xiaohongshu collection path

Read [`xiaohongshu-mcp`](../xiaohongshu-mcp/SKILL.md) before configuring or starting the local service. Its runtime and cover-screening references are the canonical Xiaohongshu instructions; this Collector does not maintain a second browser implementation.

For Xiaohongshu platform search, prefer the repository's read-only local Client over legacy MediaCrawler or ad hoc browser wrappers:

```bash
powershell -ExecutionPolicy Bypass -File collectors/xiaohongshu-mcp/scripts/start_xiaohongshu_service.ps1
python collectors/xiaohongshu-mcp/scripts/collect_xiaohongshu.py "<topic>" \
  --cover-pool 25 \
  --review-selection-file "<run>/cover-selection.json" \
  --out "<current-product-workspace>/memory/run-social-content-loop/<run>/xiaohongshu-search.json"
```

- Read the local service from `XHS_MCP_ENDPOINT`; default to `http://127.0.0.1:18063`.
- Before collection, check the endpoint. If it is unavailable, use `start_xiaohongshu_service.ps1`; it reads `XHS_MCP_BINARY` and the optional external `XHS_MCP_COOKIES_PATH` without persisting or printing credentials.
- If the service is not logged in, stop and ask the user before opening the visible login window. After approval, run `login_xiaohongshu.ps1`, verify login once, and resume from collection. Login authorizes read-only research only.
- When the user does not specify a count, tell them the first-run default is 25 items; more can be requested, but 25 is recommended.
- Keep one batch between 20 and 30 items. Persist each successful batch before another batch. Never silently retry an empty result, login failure, timeout, or 460/461/471 signal.
- Treat `xiaohongshu-search.json` as search-card evidence. When visuals are requested, use `--cover-pool 25`, inspect every generated contact sheet, and record a promotional-layout score before fetching details. Engagement is supporting evidence only.
- Keep the same process alive with `--review-selection-file`: after reviewing covers, write only `{"note_ids":[...]}` to that file. Login parameters remain in process memory and are never persisted. An empty list means every cover failed and requests no details.
- Fetch detail images only for 3-8 passing notes. For non-interactive recovery, repeated `--candidate-note-id <id>` is accepted only when those IDs are present in the current search response; it is not the preferred user-choice path.
- Never persist `xsecToken`, cookies, credential-bearing URLs, avatars, or raw upstream responses. The Client stores clean public note URLs and visible card fields only.
- Keep this path specific to Xiaohongshu. Use separate source-appropriate Collectors for WeChat, X, Instagram, and other platforms.

## Research questions

Collect evidence for:

- user pain and search/content language;
- hooks and opening patterns;
- note/article structure and visual density;
- proof, screenshots, examples, and source use;
- saves, comments, shares, and follow triggers when visible;
- CTA and conversion path;
- tone, persona, and brand posture;
- compliance, copyright, exaggeration, and AI-like risk signals.

## Source handling

For each relevant public item, record:

- source URL or user-provided filename;
- collection time;
- platform and account/page type when visible;
- visible title/hook and topic;
- top-to-bottom structure;
- media format and visual pattern;
- user value and likely reason to save/comment/share;
- Product-relevant lesson;
- what must not be copied.

Do not quote long passages. Summarize and transform. Never copy competitor wording, visual identity, proprietary screenshots, unique examples, exact title formulas, or full block sequence.

## Compare by platform

For Xiaohongshu, pay attention to:

- title click tension without false promises;
- first card readability and save value;
- card sequence, screenshots, checklists, before/after, and comment prompts;
- tags and topic language;
- whether claims could be interpreted as academic misconduct, medical/legal advice, or exaggerated outcomes.

### Xiaohongshu visual-reference pass

Run this pass before writing image scripts when the requested output includes covers, cards, screenshots, or other visual assets.

1. Search the topic language and relevant product/competitor accounts. Prefer product promotion, product workflow, and tool-use notes that match the requested audience and scenario.
2. Download all available covers from the 25-item batch and inspect the numbered contact sheets. Apply the hard rejection gate and weighted promotional-layout score in [`cover-screening.md`](../xiaohongshu-mcp/references/cover-screening.md); do not rank by engagement alone.
3. Fetch details only for 3-8 covers scoring at least 75/100, then inspect all their images at full size. If none pass, persist the rejection reasons, state the Agent's own batch-level judgment, and ask whether the user wants to provide a Xiaohongshu note they consider suitable. Offer a new product/workflow-oriented query as the alternative.
4. Under an explicitly approved autonomous policy, choose exactly one primary internally and do not display the selected reference image by default. When user choice or explicit source inspection is required, provide titles, scores, risks, and clean public URLs; never provide local paths or signed URLs. Record why every other candidate was rejected.
5. Write `visual-reference-selection.json` with one `primary`, one `reference_image`, required reasons, and all rejected candidate IDs. Validate it with:

```bash
python collectors/xiaohongshu-mcp/scripts/validate_visual_reference_selection.py \
  --selection <run>/visual-reference-selection.json \
  --candidates <run>/visual-candidates.json
```

6. Derive transferable guidance only from the selected primary sample. Do not blend layouts, palettes, illustration systems, card rhythms, or brand cues from multiple public samples.
7. Treat the selected image as analysis-only. Do not reuse its wording, logo, screenshot, proprietary UI, exact composition, distinctive illustration, or visual identity.
8. Hand off concrete guidance: what the cover should establish, which cards need real Product screenshots, what can be generated, what must be rendered deterministically, and what must not be copied.

An authorized signed-in browser session may be used for read-only research when the user permits it. Authorization to view does not authorize liking, saving, commenting, following, uploading, publishing, or extracting credentials.

For WeChat, pay attention to:

- title and opening;
- article logic, section rhythm, source attribution, and durable reference value;
- cover image and excerpt;
- how the article earns trust before conversion;
- whether it can be repurposed from or to Xiaohongshu without becoming platform-inappropriate.

## Evidence handoff

Persist or return:

- observation time, platform, market, language, query/topic tags, and access limits;
- source list and item-level observations;
- synthesized reusable patterns;
- Product-specific information gain;
- risk list and prohibited copying boundaries;
- candidate angles with value, difficulty, and evidence confidence;
- smallest next action for content creation or additional research.

The handoff must be detailed enough for `$create-social-content-pack` to create without relying on conversation memory.

When visuals are in scope, also include:

- the validated `visual-reference-selection.json` path and its internal-only usage boundary;
- the internal-only primary reference path, selection reasons, disclosure boundary, and rejection reason for every other candidate; do not expose the reference image in the default user-facing handoff;
- transferable rules from the primary sample only, plus Product-specific differences and non-copying boundaries;
- a proposed three-card vertical slice covering hook, independent method value, and real Product evidence;
- data conflicts, missing detail-page evidence, and samples excluded from any requested threshold.
