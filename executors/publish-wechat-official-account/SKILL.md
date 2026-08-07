---
name: publish-wechat-official-account
description: Prepare or execute authorized WeChat official account API publishing steps such as media upload, draft creation, preview, or live publication with strict approval boundaries. Use only when a reviewed WeChat article package exists and the user has explicitly authorized the exact API action and account scope.
---

# Publish WeChat official account content

Default to preparation and draft creation. Live publish or mass-send only after separate explicit approval.

## Boundaries

- Do not request, print, or write credentials.
- The Client reads credentials from environment variables or the ignored root `.env.local` only.
- Treat media upload, draft creation/update, preview, live publish, mass-send, delete, and metric collection as separate scopes.
- Do not upload or publish from a package that has not passed `$review-social-content`.
- Do not retry a publish action without checking idempotency state, draft ID, or platform response.

## Required inputs

Require:

- reviewed WeChat article package;
- explicit approved API action;
- account scope;
- media list and rights status;
- publication or draft idempotency key;
- link and attribution plan;
- rollback or correction boundary.

If any item is missing, prepare a human/API readiness checklist instead of calling a Client.

## Official Client

The implemented Client is `scripts/wechat_official_api.py`. It uses only `https://api.weixin.qq.com` and separates these actions:

```powershell
python executors\publish-wechat-official-account\scripts\wechat_official_api.py --check
python executors\publish-wechat-official-account\scripts\wechat_official_api.py --upload-thumb <cover.jpg> --confirm-upload
python executors\publish-wechat-official-account\scripts\wechat_official_api.py --manifest <manifest.json> --create-draft --confirm-create-draft
python executors\publish-wechat-official-account\scripts\wechat_official_api.py --manifest <manifest.json> --publish --confirm-publish
python executors\publish-wechat-official-account\scripts\wechat_official_api.py --manifest <manifest.json> --status
```

The reviewed body must be HTML. The uploaded `thumb_media_id`, exact HTML, metadata and comment settings are included in `draft_sha256`; live publication additionally requires the same `publication_sha256`, `publish.approved=true`, `auto_publish=true`, and a separate confirmation. Creating a draft never implies publication.

## Client expectation

Keep the Client thin:

- read app credentials from environment variables;
- call official WeChat API endpoints;
- redact tokens and response secrets;
- write only non-sensitive response metadata such as draft ID, article URL, publish ID, status, and timestamps;
- never make content strategy decisions.

## Record

Write the action, approval scope, package path, idempotency key, draft/publish status, returned non-sensitive IDs, URL when available, and next review window to the current Product workspace's `memory/run-social-content-loop/`.
