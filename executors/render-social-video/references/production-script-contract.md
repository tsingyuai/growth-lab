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

Inventory the complete user goal before fixing shot count or duration. For a multi-step walkthrough, preserve each distinct input, option, submission, loading, output and result-inspection state that helps the viewer understand the workflow. Default to at least 5-8 verifiable Product-action beats when the workflow supports them. Group the dependent beats, including navigation to the result page, into a continuous adaptive master and keep that master as one renderer scene; duration follows the executed workflow and `duration_seconds` is only a safety ceiling. Do not create a scene boundary merely because a new control is used, and do not accept configuration without output as a complete walkthrough. Do not replace useful operations with repeated cards or generic HTML motion. The video plan may contain up to 12 scenes.

Define every intended visible beat as a requirement. Each requirement must contain:

- a stable requirement ID;
- an executable instruction;
- the expected visible state;
- a minimum readable hold duration;
- whether it is a Product action, static evidence, animation state, narration or subtitle check.

Narration and subtitle text in the script are locked copy. The later video plan must preserve them exactly unless the user approves a script revision.

When one spoken sentence contains meaningful pauses or parallel claims, declare `speech_groups` before synthesis. Give every segment locked text, a stable ID, left/center/right lane, emphasis and `pause_after_ms`. Use `display_mode=accumulate` and `exit_mode=group` when earlier phrases must remain while later phrases appear. The ordered segment text must preserve the narration wording.

For a focused Product composition, declare `composition.preset=focused-screen` in the script. The blurred backdrop and centered foreground must use the same unchanged recording and frame time. The sharp foreground remains the evidence; the blurred copy is only spatial fill.

After narration audio exists, split ordinary subtitle copy into short `subtitle_cues` at measured speech pauses, or resolve scripted `speech_groups` into timed `caption_groups`. Never infer final timing from punctuation. Segmented local TTS must synthesize each phrase separately, insert the declared silence, and record actual phrase boundaries. User audio requires measured alignment. Preserve exact words and order.

Use a 64 px ordinary-subtitle base at 1080 width by default. Designed caption groups may use 56-96 px, a locally declared licensed font, bold weight, dark outline and no rectangular background. Keep ordinary cues to at most two lines. For an accumulating group, each phrase appears within 180 ms of its audio onset, stays in its stable lane, and the whole group exits within 250 ms of the spoken group end.

## Asset collection

Collect only assets requested by the locked script. For each shot:

1. Prepare the exact Product state or approved source asset.
2. Fix the recording/crop region before capture and use the same region for preflight and capture.
3. Execute requirements in script order.
4. Save an evidence frame or deterministic state artifact for every requirement.
5. Record the observed timestamp and visible state in `asset-evidence-ledger.json`.
6. Reject and retry the shot when any required state is missing, unreadable, mistimed or cropped.

For `speech_groups`, also record one `caption_check` per segment and one `caption_group_check` per group. Reject lane changes, collisions, audio/caption timing outside tolerance, foreground/background time drift, unreadable sharp Product UI, or captions covering the active control.

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
