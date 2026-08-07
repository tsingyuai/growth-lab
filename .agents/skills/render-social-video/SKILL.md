---
name: render-social-video
description: Use Growth Lab's optional deterministic video Executor for an explicitly requested video, including turning an approved card pack into video or generating video scene cards when no pack exists.
---

# Render social video

1. Read `../../../executors/render-social-video/SKILL.md` completely.
2. Invoke it only when the user or target formats explicitly request video.
3. Reuse one eligible reviewed card pack or generate a video-only scene-card pack according to the Executor's visual input routing; preserve manifests and asset roles.
4. Require an approved plan and real Product evidence for Product claims; do not invent UI or arbitrary animation code.
5. When motion is evidence, call `capture-screen-video` and accept only its unchanged MP4 plus validated capture manifest as `asset_role=screen-recording`.
6. Show representative scene cards plus the final MP4/cover and require human audio/visual review before any upload or publication.
7. Before local TTS, disclose the selected engine/model/voice and tell the user they may ask the Agent to replace this layer with MeloTTS, Qwen3-TTS, CosyVoice, or owned WAV audio under the Executor's license and provenance rules.
8. Offer Seedance only as optional paid B-roll. Disclose the exact model endpoint, clip count/settings and remote-asset boundary, obtain per-run approval, and use the Executor's resumable adapter; never retry an ambiguous paid create or treat B-roll as Product evidence.
