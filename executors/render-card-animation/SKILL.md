---
name: render-card-animation
description: Render approved social-card copy and visual rules as a deterministic local HTML animation, record it in an isolated Playwright browser, and emit a validated MP4 plus a hash-bound animation manifest. Use when static cards need to become motion scenes without being misrepresented as Product evidence.
---

# Render card animation

Use only locked formal copy, approved deterministic HTML and declared local assets. Product UI may appear only as an unchanged declared asset; animation never turns generated or reconstructed UI into Product evidence.

Read [`references/motion-language.md`](references/motion-language.md) before authoring HTML. Use its bounded motion vocabulary only where motion clarifies hierarchy, state or narration. Keep Product-promotion video screen-recording-led; deterministic animation is connective explanation, not the main footage.

Run with an ephemeral Playwright environment and the repository-external FFmpeg binary:

```powershell
uv run --with playwright python executors\render-card-animation\scripts\render_card_animation.py `
  --html <video>\01-animation.html `
  --asset <visual>\render\01-cover.png `
  --out <video>\raw\animations\cards.mp4 `
  --duration 12 --width 1080 --height 1920 --fps 30
```

The HTML must set `window.__ANIMATION_READY__ = true` and expose `window.__startAnimation()`. It must not begin before that function is called.

The Executor records in an isolated browser context, disables background network behavior, normalizes to H.264 MP4, verifies full decode/duration/dimensions and writes an `animation-manifest.json` binding the HTML, declared assets and output hashes.

Hand the MP4 to `render-social-video` only as `asset_role=deterministic-animation`, with `motion=none` and the matching animation manifest. It is a designed communication scene, not a real Product interaction.
