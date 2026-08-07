---
name: capture-screen-video
description: Use Growth Lab's bounded Windows screen-recording Executor to capture a user-approved product window or region as a validated MP4 and provenance manifest.
---

# Capture screen video

1. Read `../../../executors/capture-screen-video/SKILL.md` completely.
2. Invoke it only after explicit recording intent and scope confirmation.
3. Prefer an exact window or bounded region; require the additional full-desktop confirmation for desktop capture.
4. Preserve the generated MP4 and capture manifest together and require full-clip privacy review.
5. Hand validated clips to `render-social-video` only as `asset_role=screen-recording`; recording never authorizes publication.
