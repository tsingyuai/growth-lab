# Video visual quality gate

Use this gate before accepting cards or generated images as Product-promotion video input.

## Evidence first

- The reference quality target is driven by concrete Product state, not decoration. Product UI, an output example, a result comparison, a real terminal/repository state, or an owned recording frame must be the primary visual subject in claim scenes.
- A generated abstract background is a secondary brand substrate. It never proves a Product claim and cannot satisfy scene variety by itself.
- Do not ask an image model to redraw exact Product UI, code, citations, statistics, logos, or interface text. Compose those sources deterministically.

## Sequence requirements

- Lock one user problem and one proof point per scene.
- For four or more scenes, require at least three distinct primary visual assets or independently composed complete effects.
- Change crop, evidence state, annotation and composition across the sequence. Changing only headline text, node labels, accent color, or the crop of one shared background is insufficient.
- For direct video generation, review a three-scene vertical slice: hook with Product evidence, one operation/proof scene, and one outcome scene. Do not expand a failed slice.
- For `product-demo`, require validated Product screen recordings to occupy at least 50% of total duration and target 65-80% for multi-step workflows. Default to 5-8 distinct recorded actions when that many meaningful operations exist; do not inflate the count with repeated idle states.
- Reject a recording composition when the useful Product region is small or materially off-center, or when enlarging it clips a required control. Crop peripheral blank space and verify the final vertical frame at phone scale.
- Require phone-readable subtitles: 64 px base at 1080 width (about 85 px at 1440), no rectangular background, no more than two lines, and no overlap with the active Product control. When narration has pauses, require timed short-phrase cues and inspect the subtitle-free pause frame.
- Keep deterministic HTML/card animation at or below 25%; static screenshots and cards may support the remaining time.
- Calculate the mix from scene durations before rendering and again after narration changes final scene durations. Reject either failure.

## Image-generation routing

1. Prefer Product-owned screenshots, recordings split into frames, and real outputs.
2. Use `complete-effect` when the model needs to solve the overall editorial composition. Generate each role separately, then replace any Product/evidence placeholder with deterministic owned assets.
3. Use `separable-layer` only for texture, illustration, or atmosphere that remains visibly secondary.
4. If no concrete Product evidence is available, ask the user for screenshots or permission to capture them. Do not spend a paid call on one generic background and present it as a finished promotional sequence.

## Review decision

Mark the pack `revise` when the main visual could describe any AI tool, the same background dominates every scene, the Product is absent from the first viewport, or motion reveals no new evidence. Only cards with `status=approved` and a passed `visual-quality-review.json` may enter video rendering.
