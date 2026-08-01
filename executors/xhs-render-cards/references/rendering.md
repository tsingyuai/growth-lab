# Rendering modes

Choose the smallest mode that preserves truthful Product evidence and exact approved copy.

| Need | Mode | Implementation |
|---|---|---|
| Exact Chinese, dense information, repeated series, real UI | `deterministic` | HTML/CSS, Canvas, SVG, or Pillow |
| Visual depth without generated text or UI | `separable-layer` | `generate-image` background/effect + deterministic composition |
| Model-led full composition exploration | `complete-effect` | `generate-image --ref` followed by zone review and correction |

## Deterministic

Use stable canvas dimensions and installed fonts. Keep title, body, labels, logo, screenshots, citations, and statistics under local control. Store the rendering source with the package and render one output per manifest card.

## Separable layer

The prompt must say `background only` and prohibit text, letters, numbers, logos, UI, documents, citations, statistics, and watermarks. Inspect the raw layer before composition. Product screenshots and final copy remain deterministic.

```powershell
node executors/generate-image/generate-image.mjs `
  --model gpt-image-2 `
  --prompt-file <background-prompt.txt> `
  --out <raw-background.png>
```

## Complete effect

Use exactly the validated primary visual reference. Product screenshots may be additional factual inputs but do not become a second visual-learning source. Generated output is not evidence.

```powershell
node executors/generate-image/generate-image.mjs `
  --model gpt-image-2 `
  --prompt-file <prompt.txt> `
  --ref <primary-analysis-reference.png> `
  --out <raw-candidate.png>
```

Classify each zone:

- `retain`: legible, approved, low-risk visual content;
- `replace`: text, logo, real screenshot, citation, statistic, privacy mask, or evidence;
- `reject`: fake UI presented as real, invented evidence, copied identity, broken hierarchy, or broad claim drift.

## API configuration boundary

Do not call a provider when configuration is missing. Tell the user that AI generation is optional, point to `CONFIGURATION.md`, name the required variables, and offer deterministic rendering. Before the first paid verification call, ask for approval and state the timeout and output count.

## Output

Keep raw model output separate from corrected final files. Final PNGs live only in `render/`, use stable ordered names, and must pass the manifest validator. Record prompts, provider/model, reference paths, Product screenshot sources, generation time, and corrections in `PROCESS.md` or `visual-review.md`.
