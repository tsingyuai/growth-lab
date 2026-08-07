---
name: capture-screen-video
description: Execute locked shot requirements to record a user-approved Windows desktop, bounded Product region, or exact visible window as a validated MP4 with per-action evidence, a privacy gate, and a hash-bound capture manifest. Use when a scripted product demo needs truthful motion evidence before deterministic social-video rendering.
---

# Capture screen video

Capture only after the user explicitly requests recording and confirms the target scope. Prefer an exact window, then a bounded region; use the full desktop only when the user specifically accepts the wider privacy boundary.

Do not capture before the owning `render-social-video` package has a complete locked or user-approved `video-script.json`. In `human-reviewed` mode, the user must have had an opportunity to revise the complete script before capture begins.

## Preconditions

- Use the repository-external `social-video-venv`; its `imageio-ffmpeg` binary must report both `gdigrab` and `libx264`.
- Close or hide password managers, notifications, private chats, API keys, admin panels and unrelated user content.
- Use a finite duration from 1 to 300 seconds. Recording never authorizes publication.
- The current first version records video and cursor only. System audio and microphone capture are intentionally disabled; narration remains a separate reviewed layer.
- Select the exact script shot and execute its requirements in declared order. Each Product action must declare the expected visible state and minimum readable hold before recording starts.
- Determine the valid Product content bounds before preflight. Use the same fixed region for preflight, recording and evidence extraction; never accept browser chrome or unrelated screen areas as Product content.

Check readiness:

```powershell
& $VIDEO_RENDERER_PYTHON executors\capture-screen-video\scripts\record_screen.py check
```

List exact visible window titles:

```powershell
& $VIDEO_RENDERER_PYTHON executors\capture-screen-video\scripts\record_screen.py `
  list-windows --contains "Growth Lab"
```

## Record

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

Full desktop recording additionally requires `--confirm-full-desktop`. The script counts down, writes through a partial file, decodes the completed MP4, checks its duration and dimensions, computes SHA-256, and emits `<name>.capture-manifest.json`.

## Script execution evidence

After recording, inspect every requirement rather than accepting generic motion:

1. Extract an evidence frame at the observed timestamp for each script requirement.
2. Verify the expected Product state is visible and readable for at least the declared hold duration.
3. Record the requirement ID, evidence frame, timestamp, observed hold and observed state in the owning `asset-evidence-ledger.json`.
4. Reject the whole shot when an action is missing, too brief, cropped, obscured or out of order. Retry only within the script's declared retry policy.
5. Never rewrite the script to match a deficient recording.

Run the owning video package's `validate_script_coverage.py --for-production` gate before handoff.

## Handoff to video rendering

Copy the MP4 and its capture manifest into the owning video package without modifying either. A `render-social-video` scene may use them only with:

- `type=video`;
- `asset_role=screen-recording`;
- `motion=none`;
- matching `capture_manifest` and `capture_manifest_sha256`.

The final human review must inspect the complete clip for privacy, stale data, wrong account state, loading/errors, unintended notifications and requirement-by-requirement action visibility. Stop instead of cropping away evidence of a privacy failure after capture.
