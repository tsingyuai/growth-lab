# Instagram local runtime

Use a loopback-only adapter conforming to [`social-browser-service-contract.md`](../../social-browser-service-contract.md). Default endpoint: `http://127.0.0.1:18065` via `INSTAGRAM_MCP_ENDPOINT`.

The repository currently bundles the normalized Collector but not an Instagram browser adapter binary. Treat the runtime as `missing-runtime` until an adapter with a verified public source and license is approved, configured outside the repository, visibly logged in with a dedicated non-critical account, and passes one low-frequency non-empty search. The official Graph API probe may verify an authorized professional account but does not satisfy public-content discovery readiness.

Do not install a candidate Client, launch login, or run browser collection without explaining account restriction/ban risk and obtaining explicit user confirmation. Never use a primary or asset-bearing account.

## Reviewed candidates (2026-08-04)

- `subzeroid/instagrapi` at `632af63`, MIT: broad private mobile API wrapper using password/session authentication and challenge handling; reject as the default browser-first runtime.
- `YoppaV/instagram-mcp` at `f823788`, MIT: read-only visible login, profile/home/saved/Reel reads and media downloads; it does not provide general topic/keyword discovery, so it is a strong partial adapter but not parity-complete.
- `werg543/tldw` at `03dcf4d`, MIT: extracts a user-selected post/Reel through an existing CDP browser into media and frames, but does not discover a 25-item keyword batch.

No reviewed candidate satisfies the complete search-to-candidate contract. Keep `missing-runtime`; do not silently reinterpret a topic query as a username or saved-feed query.
