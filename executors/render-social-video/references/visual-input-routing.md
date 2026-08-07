# Visual input routing

Resolve visual inputs without making the user repeat work or turning video generation into an implicit Xiaohongshu publishing run.

## Route selection

### Capture a real interaction sequence

Use [`capture-screen-video`](../../capture-screen-video/SKILL.md) when motion itself proves the Product behavior and a static screenshot would omit a material step. Prefer an exact visible window, otherwise a bounded region. Require explicit full-desktop confirmation before capturing the desktop.

Import the unchanged MP4 and capture manifest into `video/raw/captures/`. Set the scene to `type=video`, `asset_role=screen-recording`, `motion=none`, and bind `capture_manifest` plus its SHA-256. Reject clips with missing or mismatched manifests, enabled source audio, incomplete duration, wrong account state, private data, notifications, loading/error states or an unreviewed full-desktop boundary.

### Reuse an existing card pack

Reuse a pack when it belongs to the current Product run, its `visual-manifest.json` passes validation, every selected card is approved or marked ready by `visual-review.md`, and its copy and Product facts still match the current video script. For Product promotion, also require scene-level visual evidence: a reusable abstract background does not count, and a four-or-more-scene pack needs at least three distinct Product screenshots, output examples, or independently composed primary effects. Prefer the only clearly current eligible pack without asking a redundant question.

Tell the user naturally:

> 已找到一组经过确认的卡片，我会沿用它的视觉风格和产品素材，再根据视频节奏调整镜头顺序，不重复生图。

Import only selected final PNG files into `video/assets/cards/`. Copy the source `visual-manifest.json` beside them, record its SHA-256 in `video-plan.json`, and preserve card IDs and original paths in the run review. Never modify the source pack.

If several materially different current packs remain eligible, recommend the closest match and ask the user to choose. Do not force a choice when one pack is clearly the current approved version.

### Generate visual cards for a direct video request

When no eligible pack exists, derive scene-card copy from the approved video script and call [`render-social-card-pack`](../../render-social-card-pack/SKILL.md). Store the result under `video/visual/visual-vN/` with platform `social-video`; do not create a Xiaohongshu publishing package unless the user also requested Xiaohongshu cards.

Tell the user before work begins:

> 我会先把视频脚本做成一组可检查的镜头卡片，再加入节奏、字幕和配音形成视频。

Use the same visual quality gates as a social card pack. If provider-backed image generation is needed, run the existing configuration and authorization gate before the first call. If the user declines or no provider is configured, continue with deterministic rendering when possible; otherwise stop with a clear missing-capability message.

### Derive instead of overwrite

If an eligible card needs a different crop, shorter text or a video-safe title area, create a derived copy inside the video package. Preserve the original, record the transformation, and require review of the derived frame. A card package approval does not automatically approve altered copy.

Treat a pack as unavailable when its manifest fails, selected files are missing, review is blocked, Product facts changed, its copy no longer matches the script, or its visual variation consists only of new text over one generic background. Explain the mismatch briefly and generate a new version only when generation is authorized. When screenshots exist, prefer a `mixed-product-evidence` video package over paying for decorative backgrounds.

## Plan contract

Set each image scene's `asset_role`:

- `product-screenshot`: unmodified or deterministically annotated Product-owned evidence;
- `rendered-card`: a reviewed visual card imported from a validated card pack.

Set a real recorded video scene's `asset_role` to `screen-recording`. It is Product evidence only after the full clip passes privacy and state review; the capture manifest proves provenance but does not replace human review.

When any scene uses `rendered-card`, set its `asset_source_id` to the original card ID, set `visual_source.mode`, and include the imported manifest path and SHA-256. The renderer rejects IDs absent from that manifest. Use `generated-for-video` for an internal scene-card pack, `reused-card-pack` for a pre-existing approved pack, and `mixed-product-evidence` when reviewed cards and additional Product screenshots are intentionally combined.

Use `style.layout=card-sequence` when approved 3:4 cards should become full-frame video scenes without another decorative wrapper. This layout accepts only `rendered-card` scenes with manifest provenance.

## User-visible review

Show representative scene cards before or with the video preview. Do not interrupt an otherwise clear run with repeated approvals, but always surface provider configuration, stale or ambiguous packs, changed claims, privacy findings, and the final audio/visual review. Rendering never authorizes publication.
