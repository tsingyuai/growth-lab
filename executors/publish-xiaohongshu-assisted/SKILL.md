---
name: publish-xiaohongshu-assisted
description: Prepare Xiaohongshu publishing packages and only use official authorized automation when the exact account type, content type, API permission, and user approval are verified. Use for Xiaohongshu notes, card packs, titles, tags, cover order, human publishing instructions, or future official Client boundaries.
---

# Publish Xiaohongshu content assisted by a human

Default mode is human-assisted publishing. Do not assume server-side auto-publishing is available for ordinary notes.

## Human-assisted package

Require a reviewed Xiaohongshu content package. Prepare:

- final title;
- note body;
- card/image upload order;
- cover choice;
- tags and topic suggestions;
- comment prompt;
- visible caveats;
- landing link, QR, bio-link, or comment CTA limitation;
- publish timing suggestion;
- step-by-step instructions for a human using the normal platform UI;
- what the human should return: final URL, screenshots, publish time, and later metrics export.

## Authorized browser automation

The configured `xpzouying/xiaohongshu-mcp` runtime exposes image-note publication through its local `/api/v1/publish` route. This is browser automation using the user's saved Xiaohongshu session, not an official Xiaohongshu open API.

Run `scripts/publish_xiaohongshu.py --manifest <path> --check` first. A real publication additionally requires the exact reviewed package to carry a `publication_sha256`, `publish.approved=true`, `publish.auto_publish=true`, a confirmation timestamp, and a separate `--confirm-publish` flag. Login used for collection is not publication approval. Never retry a failed or ambiguous publish automatically.

## Future official automation

Use an automated Client only when current official documentation and the authorized account explicitly support the exact action.

Keep these scopes separate:

- media upload or staging;
- draft creation;
- live publication;
- metric query;
- modification or deletion;
- comment/message actions;
- paid promotion.

Do not create a Client that relies on private browser automation, session cookies, reverse-engineered endpoints, or credential values stored in files.

## Record

Write the handoff or authorized action record to the current Product workspace's `memory/run-social-content-loop/`, including package path, platform, account scope, publish state, idempotency note, URL when available, and next metric window.
