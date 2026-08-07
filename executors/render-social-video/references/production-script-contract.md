# Production script contract

Write and lock the complete production script before collecting footage, screenshots, animations or voice assets. Do not write the script retrospectively from available material.

## Required artifacts

Create both files in the owning video package:

- `video-script.md`: human-readable timeline with shot purpose, picture, action, narration/subtitle and acceptance criteria.
- `video-script.json`: machine-readable source of truth conforming to `schemas/video-script.schema.json`.

After asset collection, create `asset-evidence-ledger.json` conforming to `schemas/asset-evidence-ledger.schema.json`. Bind it to the locked script SHA-256.

## Workflow modes

Choose exactly one mode in `video-script.json`:

- `fully-automated`: lock the complete script before collection and continue without a user pause only when the user requested an autonomous run.
- `human-reviewed`: finish both script files, present the script path and a concise timeline to the user, then stop. Collect no production assets until the user approves or supplies edits. Mark the script `approved` only after that response.

Default to `human-reviewed` when the user has not explicitly requested an autonomous end-to-end run.

## Shot requirements

Inventory the meaningful Product actions before fixing the shot count. For a multi-step walkthrough, preserve each distinct input, option, action, result or verification state that helps the viewer understand the workflow. Default to 5-8 independently recordable Product-action shots when the workflow supports them; do not replace useful operations with repeated cards or generic HTML motion. The video plan may contain up to 12 scenes.

Define every intended visible beat as a requirement. Each requirement must contain:

- a stable requirement ID;
- an executable instruction;
- the expected visible state;
- a minimum readable hold duration;
- whether it is a Product action, static evidence, animation state, narration or subtitle check.

Narration and subtitle text in the script are locked copy. The later video plan must preserve them exactly unless the user approves a script revision.

After narration audio exists, split the locked subtitle copy into short `subtitle_cues` at measured speech pauses. Preserve the exact words and order. Use a 64 px subtitle base at 1080 width by default, keep each cue to at most two lines, and require evidence for phrase appearance, pause disappearance and the following phrase when checking synchronization.

## Asset collection

Collect only assets requested by the locked script. For each shot:

1. Prepare the exact Product state or approved source asset.
2. Fix the recording/crop region before capture and use the same region for preflight and capture.
3. Execute requirements in script order.
4. Save an evidence frame or deterministic state artifact for every requirement.
5. Record the observed timestamp and visible state in `asset-evidence-ledger.json`.
6. Reject and retry the shot when any required state is missing, unreadable, mistimed or cropped.

Do not accept a clip merely because it is nonblank or contains generic motion. Do not rewrite the script after capture to hide missing actions.

## Pre-render gate

Run:

```powershell
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\validate_script_coverage.py `
  --script <video>\video-script.json `
  --evidence <video>\asset-evidence-ledger.json `
  --plan <video>\video-plan.json `
  --for-production
```

Rendering may start only when the command exits zero. The gate checks script status, contiguous timing, exact shot coverage, exact requirement coverage, script hash binding, evidence-file existence and declared asset hashes.

## Revision rule

When the user changes the script, create the new script content first, compute its new hash, invalidate the old evidence ledger, and recollect every asset whose shot or requirement changed. Unchanged evidence may be reused only when its shot definition and source hash remain identical.
