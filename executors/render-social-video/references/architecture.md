# Optional video architecture

## Design target

Produce simple 9:16 or 3:4 product-demo videos from real screenshots, approved copy, narration, subtitles, and a bounded animation preset library. AI plans the script and may synthesize narration; deterministic tools assemble the final video.

## Recommended layers

1. `video-plan`: convert one approved platform draft into timed scenes with narration, on-screen text, asset references, crops, annotations, and preset names.
2. `asset preparation`: reuse Product-owned screenshots and the existing screenshot/privacy rules. Use `capture-screen-video` for user-approved real interaction sequences and bind its MP4 to a validated capture manifest. Never ask a model to redraw Product UI or exact claims.
3. `speech adapter`: default to no speech or user audio; add a separately installed, license-reviewed TTS worker later. Voice cloning requires explicit rights and authorization.
4. `timeline renderer`: use the repository-local Pillow/FFmpeg compiler and a repository-external FFmpeg binary. Static layers are rendered by Pillow; FFmpeg owns timing, bounded motion, audio, fades, concatenation and encoding. Keep FFmpeg build/license information in the manifest.
5. `subtitle alignment`: derive timing from final narration; retain SRT separately and optionally burn a reviewed subtitle layer into the MP4.
6. `quality gate`: use ffprobe plus representative frame extraction to validate duration, dimensions, frame rate, codecs, audio, blank frames, text fit, privacy, and manifest correspondence.
7. `capture adapter`: `capture-screen-video` uses FFmpeg `gdigrab` for a bounded Windows window, region or explicitly approved desktop recording. It disables audio, validates decode/duration/dimensions and records privacy confirmation plus hashes before handoff.
8. `provider adapter`: `seedance_provider.py` implements a bounded Ark async-task route for optional Seedance B-roll. It requires an account-owned model endpoint, per-run paid confirmation, URL-only authorized references, resumable polling, local download and FFmpeg validation. It preserves provider, model endpoint, task, revised prompt, usage, seed, request/input hashes and output hashes without persisting signed URLs. Other providers remain unimplemented.

## Initial bounded output

- 1080x1920 or 1440x1920, 20-45 seconds, four to eight scenes;
- H.264 video, AAC audio, MP4 container, separate SRT and cover PNG;
- fade/slide, restrained pan-and-zoom, screenshot focus, highlight box, arrow, sequence number, subtitle emphasis, and CTA ending presets;
- no arbitrary animation code from generated plans;
- no generative reconstruction of logos, UI, citations, statistics, or Product evidence.

## Dependency boundary

Do not vendor FFmpeg, TTS weights, fonts, browser profiles, or generated clips. Keep optional Python dependencies in a dedicated external venv and pin them only when the renderer milestone begins. The rest of Growth Lab must install and test without these dependencies.
