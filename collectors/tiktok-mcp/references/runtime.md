# TikTok local runtime

Use a loopback-only adapter conforming to [`social-browser-service-contract.md`](../../social-browser-service-contract.md). Default endpoint: `http://127.0.0.1:18064` via `TIKTOK_MCP_ENDPOINT`.

The repository currently bundles the normalized Collector but not a TikTok browser adapter binary. Treat the runtime as `missing-runtime` until an adapter with a verified public source and license is approved, configured outside the repository, visibly logged in with a dedicated non-critical account, and passes one low-frequency non-empty search. The official OAuth probe may verify an authorized account but does not satisfy public-content discovery readiness.

Do not install a candidate Client, launch login, or run browser collection without explaining account restriction/ban risk and obtaining explicit user confirmation. Never use a primary or asset-bearing account.

## Reviewed candidates (2026-08-04)

- `davidteather/TikTok-Api` at `4993fe4`, MIT: supports public/trending retrieval but asks callers to supply an `ms_token` from browser cookies; reject as the default because it conflicts with the no-cookie-injection boundary.
- `skosovsky/tiktok-scraper` at `53db557`, MIT: read-only and bounded, but its own status says keyword discovery, reliable profile video lists and media downloads are not solved; useful for direct-URL metadata only.
- `werg543/tldw` at `03dcf4d`, MIT: extracts a user-selected TikTok URL into video, frames and transcript, but does not discover a 25-item keyword batch.

No reviewed candidate satisfies the complete search-to-candidate contract. Keep `missing-runtime`; do not silently combine partial tools and claim parity.
