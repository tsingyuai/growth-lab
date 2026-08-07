---
name: xiaohongshu-mcp
description: 使用本机 browser-first xiaohongshu-mcp 只读搜索小红书、下载候选首图、补全用户选择的笔记详情，并把脱敏证据写入调用方 Memory。用于 xhs-replicate 的选题和视觉参考研究，取代小红书 MediaCrawler 路径。
---

# Xiaohongshu browser-first collection

Read [runtime.md](references/runtime.md) before startup and [cover-screening.md](references/cover-screening.md) before visual selection.

## First-run conversation

Before collection, tell the user:

- the recommended first-run batch is 25 notes;
- the count is adjustable, but 25 is recommended;
- collection is read-only and saves sanitized research evidence and requested images locally;
- login does not authorize likes, saves, comments, follows, uploads, or publication.

If required settings are missing, stop and invoke `onboard-growth-lab`. Give the user the exact configuration file and fields from [`CONFIGURATION.md`](../../CONFIGURATION.md); never ask them to paste a key, cookie, or signed URL into the conversation.

## Runtime

```powershell
python collectors/xiaohongshu-mcp/scripts/run_xiaohongshu.py "<topic>" `
  --allow-visible-login `
  --limit 25 --cover-pool 25 `
  --out "workspaces/<product-slug>/memory/<calling-model>/<run>/xiaohongshu-search.json"
```

The coordinator starts the local service, allows up to 45 seconds for a cold browser login check, restarts only a service it owns and only once, and resumes the original collection after authentication. `--allow-visible-login` records the user's permission to open the QR window; omit it until the user agrees. It reports progress every five seconds, stops its own service after collection by default, and never stops an unknown service. Stop on timeout, risk-control, login loss, or repeated empty responses; do not loop around platform controls.

## Visual selection

1. Persist the 20-30 item search response immediately as one batch. Do not wait for page-wide stability after the response is complete.
2. Download all covers from the first batch and inspect every contact sheet.
3. Score promotional layout quality before engagement. Fetch full details only for 3-8 passing candidates.
4. Under an approved autonomous-selection policy, choose the single passing reference internally and do not display the selected reference image by default. If the user must choose or explicitly asks to inspect sources, show the candidate review and clean public note URLs; never expose local reference files, signed URLs, or access parameters.
5. If every candidate fails, first tell the user that no suitable reference was found, give the Agent's own rejection judgment and the main batch-level reasons, then ask whether they want to provide a Xiaohongshu note they consider suitable. Offer a new product/workflow-oriented query as the alternative. Do not force the best item from a weak batch or keep searching without surfacing the decision.
6. Select exactly one external visual learning sample. Write and validate `visual-reference-selection.json`:

```powershell
python collectors/xiaohongshu-mcp/scripts/validate_visual_reference_selection.py `
  --selection <run>/visual-reference-selection.json `
  --candidates <run>/visual-candidates.json
```

Use the selected reference for analysis only. Do not copy its wording, logo, proprietary UI, exact composition, or visual identity.

## Data boundary

Write search evidence, candidate images, selection, and detail summaries only under the current Product workspace and calling Model's ignored `workspaces/<product-slug>/memory/<calling-model>/` run directory. Persist clean note IDs and public URLs, never xsec tokens, cookies, signed media URLs, avatars, or raw response fields containing credentials.

## Handoff

Return the query, batch size, collection time, access limits, selection status, missing evidence, and one recommended next action. Keep an autonomously selected reference internal by default. When user choice or source inspection is required, provide clean public URLs and the review evidence needed for that decision.
