---
name: publish-x-official
description: Publish reviewed X posts through the official X API, including up to four images, and delete a previously recorded post with separate explicit approval. Use only for an authorized account and an exact reviewed package.
---

# Publish X through the official API

Use `scripts/publish_x.py` only after showing the exact text, images, target account, and distribution settings. The package must contain `publish.approved=true`, `publish.auto_publish=true`, a non-empty `confirmed_at`, and a `content_authorization.publication_sha256` that covers the text and image bytes.

Credentials stay in the ignored `.env.local` as `X_USER_ACCESS_TOKEN`; never print or persist the token. The token must be an X user access token with the scopes required by the current official API and the target account.

Check without external mutation:

```powershell
python executors\publish-x-official\scripts\publish_x.py --manifest <publish-manifest.json> --check
```

Publish only after a separate confirmation for this exact package:

```powershell
python executors\publish-x-official\scripts\publish_x.py --manifest <publish-manifest.json> --confirm-publish
```

Deletion is a distinct action and uses the post ID recorded after a successful publish:

```powershell
python executors\publish-x-official\scripts\publish_x.py --manifest <publish-manifest.json> --delete-post --confirm-delete-post
```

Never retry a create or delete call automatically. Check the local state and X result before any manual retry.
