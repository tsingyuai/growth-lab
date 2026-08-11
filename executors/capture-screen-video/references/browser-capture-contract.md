# Browser capture contract

Use browser-native capture for a web Product unless the script explicitly needs browser chrome, another desktop application or operating-system interaction.

## Plan

Create `browser-capture-plan.json` against `schemas/browser-capture-plan.schema.json`.

- Fix one viewport for the batch.
- Declare 1-12 shots. Treat one meaningful, state-preserving business workflow as one continuous master shot by default; typical Product masters are 15-90 seconds and the hard browser safety ceiling is 180 seconds.
- Use stable CSS selectors, preferably Product-owned `data-testid` attributes.
- Put state preparation in `setup_actions`; setup is trimmed from the final shot.
- Put visible scripted operations in `actions`.
- Bind every requirement to `start` or one recorded action ID.
- Require an expected selector state, optional `text_contains` or input `value_contains`, and minimum hold.
- Declare stable layout requirements such as a collapsed sidebar, absent loading state and closed transient menu; business-control assertions alone do not guarantee a consistent composition.
- Use two attempts by default and three only for a documented external instability.

## Continuity

- Keep sequential actions in one master shot when they form one user goal, including navigation to the resulting Product page. Prefer input -> strategy selection -> submit -> wait for output -> inspect or scroll output over stopping at configuration.
- Validate each sub-beat with its own action-bound requirement and evidence timestamp; continuity never reduces semantic coverage.
- Split only at a real route/page change, a required state reset, a privacy boundary, an incompatible crop, or an alternate branch that cannot truthfully follow the previous action.
- Do not independently re-record consecutive actions and join them with fades. If shorter excerpts are needed later, derive them from the same validated master without adding internal transitions.
- A failed requirement rejects and retries the master shot. Prefer a coherent retry over accepting boundary flashes, duplicated frames or artificial pauses.

Supported actions are `click`, `click-if-visible`, `fill`, `type`, `type-append`, `hover`, `press`, `wait`, `wait-for-visible`, `wait-for-hidden`, `wait-for-url`, `wait-for-text` and `scroll-to-end`. Use `wait-for-url` immediately after cross-origin navigation when a destination keeps long-lived navigation requests open, then use `wait-for-text` when the destination replaces its document after the URL changes. Verify the rendered Product content again with action requirements. Use semantic waits with a bounded `timeout_ms` for asynchronous loading and route changes instead of guessing with long fixed delays. Use `scroll-to-end` with viewport-relative steps and a readable per-step delay when the workflow must browse a long result or document; do not jump directly to the bottom. Supported requirement states are `visible`, `hidden`, `enabled`, `disabled`, `checked`, `unchecked` and `focused`.

## Readiness

Start from a stable Product build when possible. Avoid HMR-dependent recording sessions. Wait for Product-specific readiness selectors rather than `networkidle`; long-lived development connections make network idleness unreliable. Reject page exceptions before or during the shot.

## Timing

Use the browser recording itself as the source. Set `duration_mode=adaptive` by default: `duration_seconds` is a safety ceiling, not a target to fill. The runner ends after the last validated action plus `tail_hold_ms`; use `exact` only when a locked timeline truly requires a fixed length. It trims setup to the recorded action start and pads the final stable frame only when the browser container ends slightly early. Evidence timestamps refer to the transcoded MP4. Never add idle time merely to reach a round duration.

Do not use equal fixed sleeps to coordinate separate record and action processes. Desktop capture must use the `--ready-file` handshake.

## Semantic gate

For every requirement:

1. Check the selector state.
2. Check `text_contains` when declared.
3. Hold for the required duration.
4. Recheck the same state.
5. Save a viewport evidence screenshot and target bounding box.

Evaluate requirements bound to the same action as one simultaneous state group. Count screenshot and assertion work inside the shared hold interval instead of extending the shot once per requirement. Allow a bounded settle interval inside that hold before saving evidence for exit animations.

Generate `recorded-validated` only when every requirement has passed and the MP4 decodes at the fixed viewport. A nonblank image, correct duration or valid codec is insufficient.

## Handoff

Keep `<shot>.mp4`, `<shot>.capture-manifest.json`, `<shot>.browser-evidence.json`, evidence screenshots and failed-attempt logs together. Copy them unchanged into the owning video package and bind the manifest hash in `video-plan.json`.
