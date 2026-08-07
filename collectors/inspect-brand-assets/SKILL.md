---
name: inspect-brand-assets
description: Inventory official product screenshots, logos, design assets, approved visual examples, and reusable media for social content packages while preserving privacy, copyright, and brand boundaries. Use before creating Xiaohongshu cards, WeChat article images, covers, demos, or generated-image prompts that must reflect real product behavior.
---

# Inspect brand assets

Return asset evidence to the calling Model or Executor. Do not generate new images, upload files, or publish.

## Sources

Use only authorized assets:

- product repository public assets;
- official screenshots or materials provided by the user;
- public product pages and rendered screenshots;
- previously approved campaign assets in the current Product Memory.

Do not use competitor images, private user content, confidential screenshots, or copyrighted third-party assets as reusable visual material unless rights are explicit.

## Inspect and classify

For each candidate asset, record:

- source path or URL;
- collection time;
- what the image actually shows;
- whether it is a real product screenshot, official brand asset, generated visual, diagram, or reference;
- privacy status: public, internal safe, needs redaction, or blocked;
- copyright/usage status;
- platform fit: Xiaohongshu card, WeChat cover, inline article image, product demo, or not suitable;
- required crop, redaction, annotation, compression, and alt text.

Prefer real product screenshots when the content explains product behavior. Use generated images only for concepts, diagrams, covers, or supporting visuals that do not pretend to show the product UI.

## Return

Return a concise asset inventory and the safest usable set. If a needed screenshot is missing, state the exact screen, state, viewport, and data redaction needed.
