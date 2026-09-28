---
name: xhs-render-cards
description: "把已批准的小红书草稿、单一分析参考和真实产品素材变成可审查卡片：先完成 DAI 与 image plan，再按确定性、完整效果或可分离图层模式制作，机械验证 PNG 与清单并运行合规检查。精确文字和真实 UI 不交给模型猜测；AI 生图需要单独配置和授权。"
---

# Xiaohongshu card production

Read [visual-production-contract.md](references/visual-production-contract.md), [rendering.md](references/rendering.md), and [visual-review-rubric.md](references/visual-review-rubric.md). Keep DAI and compliance rules from [deai.md](references/deai.md) and [quality-gates.md](references/quality-gates.md).

## Required inputs

Require before rendering:

- approved draft, exact card copy, account role, reader, and one-sentence user value;
- verified Product facts and Product-owned screenshots or brand assets;
- one validated `visual-reference-selection.json` when external visual research is used;
- output directory in the calling `memory/xhs-replicate/` run;
- target canvas, card count, rights/privacy boundaries, and whether paid image generation is approved.

The selected public reference is analysis-only. Learn hierarchy, proof-zone proportion, density, and reading rhythm; never copy its wording, logo, proprietary UI, exact composition, distinctive decoration, or full sequence. Rejected candidates contribute no visual rules.

## 1. Lock copy and evidence

Run DAI on title, caption, card copy, CTA, and tags. Every Product claim needs a current evidence source. Delete unsupported claims instead of weakening them with defensive filler.

Write `image-plan.md` using [image-plan.md](references/image-plan.md). Lock every visible string before rendering. Do not add cards merely to match the reference.

## 2. Capture real Product evidence

Use [screenshot-assets](../screenshot-assets/SKILL.md) for real Product UI, website, code, or data. Keep the original screenshot as evidence. Do not ask an image model to recreate Product UI, logos, citations, statistics, or source text and present it as real.

## 3. Choose one production mode

- `deterministic`: HTML/CSS, Canvas, SVG, or Pillow owns layout and exact text. Preferred for Chinese copy, dense diagrams, real screenshots, and repeatable series.
- `separable-layer`: the image model creates only a background, texture, or illustration without text/UI; deterministic rendering places approved copy and Product evidence.
- `complete-effect`: the image model proposes a whole visual direction. Generated text, UI, logos, evidence, and sensitive claims must be replaced or the candidate rejected.

Image generation is optional and separately authorized. If neither `OPENAI_API_KEY` nor `GEMINI_API_KEY` is configured, show the user the exact steps in [`CONFIGURATION.md`](../../CONFIGURATION.md) and offer deterministic rendering or a no-image handoff. Never silently retry or request a key in conversation.

## 4. Test a three-card vertical slice

Before expanding a large pack, render:

1. hook/cover;
2. independently useful method/checklist/comparison;
3. real Product evidence when the content makes a Product claim.

Show the actual images in the conversation. A filesystem path alone is not a visual review. Check phone-size readability, hierarchy, Product truthfulness, privacy, and copying boundaries.

## 5. Validate and review

Create `visual-manifest.json`, then run:

```powershell
python executors/xhs-render-cards/scripts/validate_social_card_pack.py --package <visual-package>
```

Run the existing DAI and compliance checks with `make lint-post POST=<post-directory>`. Inspect every final image at full size and as a contact sheet. Write `visual-review.md` with sources, selected mode, generated assets, replacement decisions, dimensions, privacy, copyright, factual and mobile-readability results.

Only reviewed files under `render/` may enter the human publishing package. Rendering never authorizes upload or publication.

## Stop rules

Stop on missing Product evidence, ambiguous rights, unreviewed reference selection, exposed private data, fake UI, malformed text, provider failure, or repeated candidate failure. One targeted retry may replace an explicitly authorized work-in-progress candidate; do not loop or create duplicate publishable assets.
