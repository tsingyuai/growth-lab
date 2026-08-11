# Product-demo visual pattern

Use this pattern for screenshot-led or lightweight screen-recording videos where the Product interface is the primary evidence.

## Analyzed reference

- Source: <https://www.xiaohongshu.com/explore/696782ed000000002202f98a>
- Reviewed with user authorization on 2026-08-05.
- Only abstract composition, pacing and information hierarchy were analyzed. The source video, audio, logo, copy and extracted frames are not stored or redistributed.

## Transferable rules

1. Keep a stable brand zone, Product-evidence zone and conclusion zone across scenes.
2. Let real Product UI occupy most of the useful canvas. Decoration must not compete with evidence.
3. Present one claim per scene and immediately show the Product state that proves it.
4. Use a short outlined hook only at major transitions, not on every frame.
5. Use a large cursor, click marker, highlight or restrained crop to make the intended operation obvious.
6. Use a 64 px subtitle base at 1080 width (about 85 px at 1440), one short phrase at a time and no rectangular background. Keep captions clear of the demonstrated control.
7. Static screenshots, short recordings and simple transitions are sufficient when the narrative sequence is strong.
8. A generated abstract background may unify the series but must not be the main visual subject in every scene. Use distinct Product states, outputs, screenshots, or independently composed effects so motion reveals new evidence instead of repeatedly zooming the same substrate.
9. Inventory the Product workflow before writing shots. Define the user goal first, then plan 5-8 or more meaningful actions as sub-beats inside a continuous adaptive master, usually 15-90 seconds. A useful walkthrough normally reaches and inspects the output; configuration alone is not a complete workflow.
10. Make unchanged, privacy-reviewed Product screen recordings at least 50% of total runtime. Target 65-80% when the workflow has several meaningful actions.
11. Validate each Product action independently with its own start state, operation, end state and evidence frames. Preserve dependent actions in one continuous master shot; a failed requirement invalidates that master and triggers a coherent retry.
12. Use one continuous master as one renderer scene. Do not add fades, blank frames or repeated stills between sub-beats from the same workflow. Split only for a real page/state/privacy/crop boundary.
13. Scale each recording so the useful Product region is the primary subject. Remove peripheral blank space, keep all required controls visible, and place the useful region near the vertical center before accepting the composition.
14. Split narration into subtitle cues at measured audio pauses. Verify a phrase-visible frame, a pause frame with no subtitle, and the next phrase-visible frame.
15. Limit deterministic HTML/card animation to 25% of runtime. Reserve it for the hook, chapter divider, one concise concept explanation or conclusion.
16. Use `focused-screen` only when a landscape recording needs stronger focus inside a vertical canvas. Fill the canvas with a synchronized blurred copy, then center a large, sharp, unchanged foreground copy. Never blur the only visible Product evidence.
17. For parallel spoken claims, use one caption group with stable left/center/right lanes. Reveal phrases from measured audio onsets, retain earlier phrases when `accumulate` is declared, and remove the whole group at the spoken ending. Move the whole band when required to avoid the active Product control; never move individual lanes mid-group.

## Originality boundary

Do not copy the reference's brand treatment, exact wording, timing, scene order or distinctive layout measurements. Build from Product-owned screenshots, approved claims and the target Product's own visual identity.

## Current implementation

The `product-demo` layout supports 1440x1920 evidence scenes, up to 12 total scenes, ordinary subtitle cues, accumulating caption groups, focused-screen composition, highlights and cursor overlays. It accepts validated screen recordings as the primary footage and real Product screenshots or reviewed cards as supporting frames. Reviewed 3:4 cards render full-canvas rather than inside a second presentation frame. Use `classic` for text-only scenes. The renderer enforces the recording-majority and animation-limit ratios from the final adjusted scene durations.
