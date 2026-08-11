# Focused recording and caption pattern

Use this pattern for a sharp centered Product recording over a blurred same-recording backdrop, and for spoken parallel phrases that appear progressively across the frame.

## Script contract

Lock semantic speech groups before synthesis:

```json
{
  "composition": {
    "preset": "focused-screen",
    "foreground_width_ratio": 0.86,
    "backdrop_blur": 24,
    "backdrop_dim": 0.14
  },
  "speech_groups": [{
    "id": "benefits",
    "display_mode": "accumulate",
    "exit_mode": "group",
    "vertical_anchor": "middle",
    "segments": [
      {"id": "automatic", "text": "能自动", "lane": "left", "pause_after_ms": 220},
      {"id": "control", "text": "可控制", "lane": "center", "pause_after_ms": 220},
      {"id": "value", "text": "高性价比", "lane": "right", "pause_after_ms": 0, "emphasis": "accent"}
    ]
  }]
}
```

Do not copy a reference brand's logo, exact typeface, wording, timing or layout measurements. Use a Product-owned type and color system.

## Timed plan

After narration exists, use its measured phrase starts:

```json
{
  "speech_segments": [
    {"id": "automatic", "text": "能自动", "pause_after_ms": 220},
    {"id": "control", "text": "可控制", "pause_after_ms": 220},
    {"id": "value", "text": "高性价比", "pause_after_ms": 0}
  ],
  "caption_groups": [{
    "id": "benefits",
    "display_mode": "accumulate",
    "exit_together": true,
    "vertical_anchor": "middle",
    "entry": "fade",
    "end": 2.75,
    "segments": [
      {"id": "automatic", "text": "能自动", "lane": "left", "start": 0.35},
      {"id": "control", "text": "可控制", "lane": "center", "start": 1.02},
      {"id": "value", "text": "高性价比", "lane": "right", "start": 1.71, "emphasis": "accent"}
    ]
  }]
}
```

## Composition gate

- Use one source recording and one timestamp for both layers.
- Scale and crop the backdrop to fill, then blur and dim it.
- Scale the foreground to contain at 55-96% of canvas width and center it.
- Keep the foreground sharp, readable and large enough for the demonstrated control.
- Use `overlay_mode=none` or `subtitles-only`; never place the legacy heading panel over this composition.
- Move the entire caption band when it intersects the action `focus_box`.

## Caption gate

- Use a local licensed font, bold weight, dark outline and no rectangular backing.
- Keep left, center and right lane centers stable for the whole group.
- Fit every phrase inside its lane before rendering; shrink only that group when needed.
- Start each phrase within 180 ms of its measured audio onset.
- Keep previous phrases visible in `accumulate` mode.
- Exit the complete group within 250 ms of the spoken group end.
- Reject collisions, mid-group position shifts, hidden Product controls or foreground/backdrop time drift.
