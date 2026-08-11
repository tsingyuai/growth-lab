---
name: capture-screen-video
description: Execute locked shot requirements to record a user-approved web Product viewport, Windows desktop region, or exact visible window as validated MP4 clips with selector-level or per-action evidence, bounded retries, a privacy gate, and hash-bound capture manifests. Use when a scripted product demo needs truthful motion evidence before deterministic social-video rendering.
---

# Capture screen video

Capture only after the user explicitly requests recording and confirms the target scope. For a web Product, prefer the browser-native path because it fixes the viewport and removes Windows position, border and DPI drift. Use an exact window or bounded region for desktop software and cross-window actions; use the full desktop only when the user specifically accepts the wider privacy boundary.

Do not capture before the owning `render-social-video` package has a complete locked or user-approved `video-script.json`. In `human-reviewed` mode, the user must have had an opportunity to revise the complete script before capture begins.

## Preconditions

- Use the repository-external `social-video-venv`; its `imageio-ffmpeg` binary must provide `libx264`, and must also provide `gdigrab` for desktop capture.
- Close or hide password managers, notifications, private chats, API keys, admin panels and unrelated user content.
- Use a finite duration from 1 to 300 seconds. Recording never authorizes publication.
- The current first version records video and cursor only. System audio and microphone capture are intentionally disabled; narration remains a separate reviewed layer.
- Select the exact script shot and execute its requirements in declared order. Each Product action must declare the expected visible state and minimum readable hold before recording starts.
- Record one complete user-goal workflow as a continuous adaptive master shot by default, normally 15-90 seconds and never above the 180-second browser safety ceiling. Include input, strategy selection, submission, asynchronous result wait, and meaningful result inspection when the Product supports them. Keep per-action requirements and evidence inside that shot; do not stop after configuration merely because a fixed duration was reached.
- Read [`browser-capture-contract.md`](references/browser-capture-contract.md) before recording a web Product. Use a fixed viewport, stable selectors, one browser process for the batch, independent shot contexts and a maximum of two attempts by default.
- For desktop capture, determine valid Product content bounds before preflight. Use the same fixed region for preflight, recording and evidence extraction; never accept browser chrome or unrelated screen areas as Product content.

Check readiness:

```powershell
& $VIDEO_RENDERER_PYTHON executors\capture-screen-video\scripts\record_screen.py check
```

List exact visible window titles:

```powershell
& $VIDEO_RENDERER_PYTHON executors\capture-screen-video\scripts\record_screen.py `
  list-windows --contains "Growth Lab"
```

## Record a web Product

Create a Schema-valid [`browser-capture-plan.json`](schemas/browser-capture-plan.schema.json), then run:

```powershell
node executors\capture-screen-video\scripts\record_browser_shots.mjs `
  --plan <video>\browser-capture-plan.json `
  --out <video>\raw\captures `
  --playwright-module <product>\node_modules\playwright\index.mjs `
  --browser-executable "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --ffmpeg $VIDEO_FFMPEG_PATH --confirm-capture
```

The runner keeps one browser process for up to 12 shots, records each shot in a fixed viewport, injects a synchronized visible cursor, executes declared CSS-selector actions, verifies every requirement before and after its hold, writes evidence screenshots, retries only the failed shot, transcodes to H.264 MP4, and emits a capture manifest only after semantic validation passes. A continuous master may contain many ordered actions and requirement groups. Include layout requirements such as collapsed navigation and closed transient menus. Do not replace stable Product selectors with screen coordinates.

## Record desktop software

Record one exact visible window:

```powershell
& $VIDEO_RENDERER_PYTHON executors\capture-screen-video\scripts\record_screen.py record `
  --window-title "Exact visible title" --duration 12 `
  --out <video>\raw\captures\product-demo.mp4 --confirm-capture
```

Record a bounded desktop region:

```powershell
& $VIDEO_RENDERER_PYTHON executors\capture-screen-video\scripts\record_screen.py record `
  --region 100,100,1280,720 --duration 12 `
  --out <video>\raw\captures\product-demo.mp4 --confirm-capture
```

For scripted desktop actions, pass `--countdown 0 --ready-file <shot>.ready.json`. Start the action runner only after that JSON reports `capture-started`; never synchronize recording and actions with matching fixed sleeps. Full desktop recording additionally requires `--confirm-full-desktop`. The script writes through a partial file, decodes the completed MP4, checks its duration and dimensions, computes SHA-256, and emits `<name>.capture-manifest.json`.

## Script execution evidence

After recording, inspect every requirement rather than accepting generic motion. Browser-native capture performs this gate during recording; desktop capture must create equivalent evidence before handoff:

1. Extract an evidence frame at the observed timestamp for each script requirement.
2. Verify the expected Product state is visible and readable for at least the declared hold duration.
3. Record the requirement ID, evidence frame, timestamp, observed hold and observed state in the owning `asset-evidence-ledger.json`.
4. Reject the whole shot when an action is missing, too brief, cropped, obscured or out of order. Retry only that shot, at most twice by default, and retain the attempt error log.
5. Never rewrite the script to match a deficient recording.

Run the owning video package's `validate_script_coverage.py --for-production` gate before handoff.

## Handoff to video rendering

Copy the MP4 and its capture manifest into the owning video package without modifying either. A `render-social-video` scene may use them only with:

- `type=video`;
- `asset_role=screen-recording`;
- `motion=none`;
- matching `capture_manifest` and `capture_manifest_sha256`.

The final human review must inspect the complete clip for privacy, stale data, wrong account state, loading/errors, unintended notifications and requirement-by-requirement action visibility. Treat decode, duration, dimensions and nonblank pixels as mechanical checks only; they never prove the correct Product state. Stop instead of cropping away evidence of a privacy failure after capture.
