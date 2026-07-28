---
name: screenshot-assets
description: Capture authenticated product screenshots through the repository-owned Playwright CDP script and archive them in the invoking loop's Memory. Use when content needs truthful UI evidence, reusable product screenshots, a selected component, or a full-page browser capture. Requires only user-installed uv and Chrome configured by onboarding; never depends on MCP tools, external Skills, private repositories, or external scripts.
---

# Screenshot assets

Use [`scripts/capture.py`](scripts/capture.py). It connects to the user's already-running Chrome through CDP, so the user completes login in their own browser and retains control of authentication.

## Preconditions

If `uv`, Chrome, CDP, or the target login is unavailable, invoke [onboard-growth-lab](../../models/onboard-growth-lab/SKILL.md). Do not look for credentials in another repository and do not inject copied tokens or cookies.

Ask for the target URL, what UI fact the screenshot must prove, output path under the invoking Model's Memory, viewport, and optional CSS selector. Never infer a staging URL or test account.

## Capture

Start Chrome with remote debugging as directed by onboarding, let the user log in, then run:

```bash
uv run --with playwright python executors/screenshot-assets/scripts/capture.py \
  --cdp http://127.0.0.1:9222 \
  --url "https://product.example/workspace/..." \
  --out memory/<loop>/assets/screenshots/<descriptive-name>.png \
  --width 1440 --height 900
```

For one stable component, add `--selector '<css-selector>'`. Add `--wait-selector` for a loading boundary and `--delay-ms` only when the application needs a short settling interval.

## Quality and privacy

- Capture only the minimum region needed to support the claim.
- Inspect the output at full size. Reject loading, error, stale, clipped, blurred, or wrong-account states.
- Redact personal data before distribution; do not capture secrets, cookies, tokens, admin panels, or unrelated user content.
- Record source URL, capture time, viewport, selector, product version/environment, and what the screenshot demonstrates in a neighboring metadata file.
- Do not use AI-generated UI as product evidence.
- Store reusable screenshots once in the loop's Memory; outputs may reference them without duplicating the source asset.
