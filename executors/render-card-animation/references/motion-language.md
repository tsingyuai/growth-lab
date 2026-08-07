# Bounded motion language

Use this vocabulary for short deterministic explanation scenes. It is distilled from an analyzed product-demo reference; copy no source branding, wording, audio, exact timing or layout identity.

## Supported expressions

| Expression | Implementation | Use |
| --- | --- | --- |
| Typewriter reveal | reveal grapheme clusters with a fixed cursor and final hold | one short hook or closing sentence |
| Masked title reveal | `overflow:hidden`, clip path or width mask plus restrained translate | chapter title or changed state |
| Keyword highlight | animate a flat rectangular backing behind one approved phrase | direct attention to one promise |
| Color-plane transition | expand one solid block across the stage, then reveal the next theme | major chapter boundary only |
| Crossfade | overlap outgoing and incoming opacity for 0.3-0.8 seconds | related state change |
| State switch | update label, active chip, evidence asset and caption from one timeline state | compare input, loading and output |
| Loading ring | SVG circle rotation with fixed stroke geometry | a real bounded wait state, never fake progress |
| Audio waveform | precompute amplitude samples and render an SVG path or Canvas shape | explain real audio playback |
| Evidence emphasis | one cursor, click marker, crop or outline bound to a real Product object | direct attention without covering UI |

## Timing and restraint

- Drive scenes from an explicit state timeline: `idle -> reference/input -> processing -> result -> hold`.
- Use opacity, translate, scale and masks with ease-out curves. Avoid bounce, spring, decorative particles and continuous camera motion.
- Keep most transitions between 0.3 and 0.8 seconds and leave 1-4 second readable holds.
- Synchronize waveform, labels and state switches to reviewed audio markers. Do not estimate lip or audio sync from CSS duration alone.
- Use at most two simultaneous motion ideas. Motion must reveal new meaning, not keep an otherwise empty card busy.

## Product-video boundary

- Never reconstruct Product interaction in HTML when it can be recorded truthfully.
- Treat a real Product recording as the primary visual evidence. Use these expressions for the hook, chapter boundary, short explanation, annotation or conclusion.
- Do not animate a failed or unapproved static card. Preserve the approved composition and exact copy.
- Keep all Product UI unchanged and sourced; overlays must be removable and must not imply an action that was not recorded.
