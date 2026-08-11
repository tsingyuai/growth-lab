---
name: render-social-video
description: Write, review and lock a complete shot-by-shot production script before collecting assets, then validate and render short product-demo videos from reviewed cards, real Product screenshots or recordings, narration, subtitles, and bounded deterministic motion. Use when a target explicitly requests video, asks to turn social cards into video, or requests video without preparing images first; this optional generator stays isolated from non-video Growth Lab runs.
---

# Render social video

Keep video production as an optional Executor. It may consume the same verified Product facts and platform brief as other social outputs, but it must not add a runtime dependency to research, copywriting, card rendering, or publishing.

## Current status

Status: `generator-ready`; platform video publication remains separately gated.

- Render only when `distribution.targets[].formats` explicitly contains `video` or the user directly requests a video.
- Read [`production-script-contract.md`](references/production-script-contract.md) first. Write `video-script.md` and Schema-valid `video-script.json` before collecting any footage, screenshots, animations or voice assets. Do not reconstruct the script after production.
- Choose `fully-automated` only when the user explicitly requested an autonomous end-to-end run. Otherwise use `human-reviewed`: finish the complete script, present its path and concise timeline to the user, then stop before asset collection so the user can approve or revise it.
- After the script is locked or approved, collect only its declared assets and create `asset-evidence-ledger.json`. Every intended visible action or state must have a matching requirement result, evidence artifact, observed timestamp and readable hold duration. Run `scripts/validate_script_coverage.py --for-production`; do not render unless it exits zero.
- Read [`visual-input-routing.md`](references/visual-input-routing.md) and [`visual-quality-gate.md`](references/visual-quality-gate.md), then reuse one eligible reviewed card pack or generate an internal scene-card pack before planning the timeline. Do not make the user manually run card generation first. A card is eligible only after its hard self-review gate passes.
- Use reviewed cards, real Product screenshots, reviewed text, the versioned plan Schema and the bounded preset list. Never generate arbitrary animation code.
- Use [`capture-screen-video`](../capture-screen-video/SKILL.md) when a Product claim is best proven by a real interaction sequence. Accept only its validated MP4 and hash-bound capture manifest as `asset_role=screen-recording`; require full-clip privacy review before rendering.
- Use [`render-card-animation`](../render-card-animation/SKILL.md) for approved card copy that needs deterministic motion. Accept only its validated MP4 and hash-bound animation manifest as `asset_role=deterministic-animation`; never describe it as Product interaction evidence.
- Choose `classic` for the existing 1080x1920 treatment, `product-demo` for a screen-recording-led 1440x1920 walkthrough, or `card-sequence` only when the user explicitly asks to animate approved 3:4 cards without a Product walkthrough. Read [`product-demo-pattern.md`](references/product-demo-pattern.md) before planning `product-demo`. Inventory the complete user goal first; for a multi-step workflow, default to at least 5-8 verifiable action beats and target 65-80% recording runtime. Record input, strategy selection, submission, asynchronous result wait and meaningful result inspection as one adaptive master when they form one flow, and use that master as one renderer scene while retaining per-action evidence. Split only at a genuine state, privacy or crop boundary. Keep cards for a necessary hook, proof summary or conclusion instead of repeating them between Product actions. Every reused card must declare its role and provenance. The renderer rejects a `product-demo` plan when real `screen-recording` scenes occupy less than 50% of planned or final duration, or deterministic HTML animation exceeds 25%.
- Read [`focused-caption-pattern.md`](references/focused-caption-pattern.md) when the user wants a centered clear recording over a blurred same-recording backdrop, or wants pause-driven words to appear in left/center/right lanes. Declare `speech_groups` in the locked script, synthesize or measure narration segments, then resolve exact `caption_groups` timing in the video plan. Never infer word timing from punctuation alone.
- Make subtitles phone-readable by default: use a 64 px base at 1080 width (about 85 px at 1440), one short spoken phrase at a time, at most two lines, outlined text without a rectangular background, and a safe position that does not cover the demonstrated control. For recorded narration, measure real audio pauses and provide ordered `subtitle_cues`; do not leave a full sentence visible for the whole scene when the voice contains multiple phrases. Review phrase start, pause disappearance and next-phrase appearance against the final audio.
- Treat caption overlays on a real screen recording as guidance, not deterministic-animation runtime. They do not reduce the recording ratio or count toward the 25% HTML/card-animation limit.
- The repository-local Pillow/FFmpeg compiler remains the default renderer. When a reviewed script genuinely benefits from React-driven motion, designed caption choreography or reusable programmatic scenes, read [`remotion-renderer.md`](references/remotion-renderer.md) and offer Remotion as an optional repository-external renderer. Before its first installation or use, disclose the exact version and separate Remotion License, explain the current free/company eligibility boundary, and obtain explicit confirmation that the user is eligible or licensed. Persist only a minimal acknowledgement outside the repository. Never vendor Remotion, silently install or upgrade it, add it to the Growth Lab core dependency path, or require attribution in the generated video.
- `none`, per-scene `user-audio`, Windows `windows-sapi`, and pinned local `local-tts` voice modes are supported. The current local preset is Apache-2.0 `hexgrad/Kokoro-82M-v1.1-zh` with a separately installed runtime. Voice cloning and paid providers are not part of the generator.
- Before local synthesis, disclose the engine, model and voice. Tell the user naturally that they may ask the Agent to replace the voice layer with MeloTTS, Qwen3-TTS, CosyVoice, or owned WAV audio. A replacement must remain optional and external, pass a license/hardware review, preserve exact model provenance, and produce reviewable WAV files; never silently clone a person or claim a platform's proprietary voice.
- Offer Seedance only as an optional paid `generated-broll` source. Before creating a task, show the configured provider/model endpoint, number of clips, requested duration/resolution/ratio, reference-upload boundary and unknown or estimated cost, then obtain explicit approval for that exact run. `check` and `inspect` are free local checks; `run` requires `--confirm-paid-generation`. Never repeat an ambiguous POST, persist a signed input/output URL, or let generated B-roll redraw exact Product UI or text.
- Rendering does not authorize upload or publication.

Install optional dependencies into the repository-external video venv:

```powershell
uv venv "$HOME\.growth-lab\clients\social-video-venv" --python 3.11
uv pip install --python "$HOME\.growth-lab\clients\social-video-venv\Scripts\python.exe" `
  -r executors\render-social-video\requirements-video.txt

uv venv "$HOME\.growth-lab\clients\social-tts-venv" --python 3.11
uv pip install --python "$HOME\.growth-lab\clients\social-tts-venv\Scripts\python.exe" `
  -r executors\render-social-video\requirements-tts-kokoro.txt
```

Render:

```powershell
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\render_video.py `
  --plan <package>\video\video-plan.json --out <package>\video
```

The plan must pass [`video-plan.schema.json`](schemas/video-plan.schema.json). It supports 2-12 scenes, screen-recording scenes up to 90 seconds, other scenes up to 12 seconds, and an optional 56-72 px `style.subtitle_size` base; omit the setting to use 64 px. The renderer produces an MP4, cover, SRT, extracted review frames, [`video-manifest.schema.json`](schemas/video-manifest.schema.json), and a mechanical review report. Local TTS additionally produces `raw/audio/tts-manifest.json`; segmented requests record actual phrase timing and declared pauses. A human still reviews audio, privacy, text timing and final publication settings. Screen recordings require a validated capture manifest and remain silent so the reviewed narration layer stays authoritative.

The pre-render script gate is mandatory even when all assets already exist:

```powershell
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\validate_script_coverage.py `
  --script <package>\video\video-script.json `
  --evidence <package>\video\asset-evidence-ledger.json `
  --plan <package>\video\video-plan.json `
  --for-production
```

Seedance preflight and generation:

```powershell
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\seedance_provider.py check
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\seedance_provider.py inspect `
  --request <video>\seedance\hero\seedance-request.json
& $VIDEO_RENDERER_PYTHON executors\render-social-video\scripts\seedance_provider.py run `
  --request <video>\seedance\hero\seedance-request.json `
  --out <video>\seedance\hero --confirm-paid-generation
```

Use `resume` with the same request/output after a polling timeout. Use `delete --confirm-delete` only after a separate remote-cleanup confirmation; it never deletes local evidence. A successful `seedance-manifest.json` may enter `video-plan.json` only as `type=video`, `asset_role=generated-broll`, `motion=none`, with the manifest path and SHA-256. Provider audio remains disabled; local subtitles and the selected voice layer stay authoritative.

## Integration contract

Future input ownership:

- the current Product workspace and owning `run-social-content-loop` run;
- an approved canonical brief and one platform-native video draft;
- verified claim ledger and Product-owned screenshot inventory;
- narration, on-screen copy, aspect ratio, duration, rights, privacy, and generation boundaries.

Future output ownership:

```text
workspaces/<product-slug>/memory/run-social-content-loop/<run>/packages/<platform>/video/
  video-script.md
  video-script.json
  asset-evidence-ledger.json
  video-plan.json
  narration.wav
  subtitles.srt
  raw/
  render/
    final.mp4
    cover.png
  video-manifest.json
  video-review.md
```

All runtime output remains in ignored Product Memory. No generated or downloaded media belongs in the Skill directory.

## Active optional route

```text
run-social-content-loop
  -> adapt-social-platform
  -> render-social-video (optional; only when formats includes video)
  -> social-content-package
  -> human-assisted or separately authorized official publishing
```

The canonical brief remains usable when this optional step is skipped or unavailable. `capture-screen-video` may supply truthful Product interaction clips, and Seedance may supply optional short B-roll through the bounded Ark adapter; real Product UI, exact text, subtitles, annotations, encoding, and final assembly remain deterministic. Other generative-video providers are not implemented.

## Stop rules

Stop on a missing/unapproved production script, incomplete requirement evidence, script/evidence hash mismatch, missing renderer, invalid plan, missing requested TTS runtime, absent Product rights, exposed private data, unsupported codec, failed video QA, or missing final publication authorization. Never fall back to fake Product UI, undeclared paid APIs, a placeholder MP4, or retrospective script edits that conceal missing footage.
