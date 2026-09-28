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
powershell -ExecutionPolicy Bypass -File collectors/xiaohongshu-mcp/scripts/start_xiaohongshu_service.ps1
python collectors/xiaohongshu-mcp/scripts/collect_xiaohongshu.py "<topic>" `
  --limit 25 --cover-pool 25 `
  --out "memory/xhs-replicate/<run>/xiaohongshu-search.json"
```

The service must be local HTTP only. If it is not logged in, explain the boundary, ask before opening the visible login window, run `login_xiaohongshu.ps1`, verify once, and resume. Stop on timeout, risk-control, login loss, or repeated empty responses; do not loop around platform controls.

## Visual selection

1. Persist the 20-30 item search response immediately as one batch. Do not wait for page-wide stability after the response is complete.
2. Download all covers from the first batch and inspect every contact sheet.
3. Score promotional layout quality before engagement. Fetch full details only for 3-8 passing candidates.
4. Show every passing candidate with its actual representative image, title, score, and risk. If inline image rendering is unavailable or cannot be confirmed, include the clean public note URL in the same response.
5. If the user rejects all candidates, record the reasons and run a new product/workflow-oriented query. Do not force the best item from a weak batch.
6. Select exactly one external visual learning sample. Write and validate `visual-reference-selection.json`:

```powershell
python collectors/xiaohongshu-mcp/scripts/validate_visual_reference_selection.py `
  --selection <run>/visual-reference-selection.json `
  --candidates <run>/visual-candidates.json
```

Use the selected reference for analysis only. Do not copy its wording, logo, proprietary UI, exact composition, or visual identity.

## Data boundary

Write search evidence, candidate images, selection, and detail summaries only under the calling Model's ignored `memory/xhs-replicate/` run directory. Persist clean note IDs and public URLs, never xsec tokens, cookies, signed media URLs, avatars, or raw response fields containing credentials.

## Handoff

Return the query, batch size, collection time, access limits, candidates, visible engagement, selection status, clean public URLs, missing evidence, and one recommended next action. The user must be able to see the candidate image or public source before choosing.
