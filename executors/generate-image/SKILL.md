---
name: generate-image
description: Generate, edit, or batch-create SEO, marketing, social, and document images with Gemini or OpenAI through the repository-owned Growth Lab image client. Use when a page or content loop needs illustrations, diagrams, covers, reference-image edits, multiple candidates, or verified image text and composition. This is the only AI image-generation Executor in Growth Lab.
---

# Generate images

Use `executors/generate-image/generate-image.mjs` for text-to-image and reference-image editing.
It is a repository-owned, zero-dependency Node.js client. Do not call Codex system Skills, private scripts, or files under `~/.codex`.

## Define the asset

Specify:

- placement and purpose;
- subject and visible action;
- composition and aspect ratio;
- visual style and brand palette;
- exact text when text is essential;
- details that must appear;
- artifacts, logos, watermarks, and unrelated text to exclude.

Prefer real product screenshots when the image explains product behavior. When an image provider is configured and the user approves the paid call, prefer provider-backed generation for covers, visual-direction exploration, illustrations, scenes, diagrams, and supporting examples where visual quality matters. Keep exact text and real Product evidence deterministic when needed.

## Direct the composition

For a cover, poster, social card, campaign visual, or any image where layout materially affects quality, read [`references/editorial-layout.md`](references/editorial-layout.md) completely before writing the provider prompt.

Before generation, lock:

- one communication job and one dominant focal point;
- the reading order from primary message to support and proof;
- a short visual philosophy covering space, form, type, color, and rhythm;
- one memorable signature element, with all supporting elements kept quiet;
- an explicit negative-space plan and a density appropriate to the placement;
- the exact text and factual zones that must remain deterministic.

Explore two or three materially different compositions when the scope and approved output count allow it. Different colors on the same layout do not count. Do not combine several aesthetic references: use at most the one authorized primary learning reference, then derive a Product-specific direction from the subject, audience, and communication job.

Treat whitespace as active structure, not an empty region to fill. Do not add cards, badges, icons, rules, labels, or patterns unless they improve hierarchy, evidence, or reading flow. When the brief is minimal, precision in spacing, type, crop, and alignment carries the result.

## Generate

Use a prompt file for long or multilingual prompts:

```bash
node executors/generate-image/generate-image.mjs \
  --out <output.png> --prompt-file <prompt.txt>
```

Choose OpenAI explicitly when appropriate:

```bash
node executors/generate-image/generate-image.mjs \
  --model gpt-image-2 --out <output.png> \
  --prompt-file <prompt.txt>
```

Add one `--ref <image>` argument for each reference image used in an edit.

For JSONL batch generation, put one job per line with `prompt` or `prompt_file`, `out`, and optional `model`, `refs`, `size`, or `quality`:

```bash
node executors/generate-image/generate-image.mjs \
  --batch <jobs.jsonl> --out-dir <directory> --concurrency 3
```

Read `GEMINI_API_KEY` or `OPENAI_API_KEY` from the process environment, root `.env.local`, or root `.env`, in that precedence order. Use `GOOGLE_GEMINI_BASE_URL` or `OPENAI_BASE_URL` only for a compatible HTTPS endpoint. Keep credentials out of prompts, files, logs, and commits.
Do not read credentials from another application's private authentication files.

At the first image-production decision in each run, run `python models/onboard-growth-lab/scripts/check_configuration.py` before choosing a rendering mode.

- If a provider is configured, present the provider/model, proposed output count and task scope, explain that successful calls may be paid, and recommend API generation for the better visual result. Call it only after explicit confirmation.
- If image generation is `optional-missing`, proactively ask whether the user wants to configure an image API for a better visual result. Briefly compare API-led effect exploration with deterministic rendering. If the user chooses API generation, explain that the next successful call is paid, then run `python models/onboard-growth-lab/scripts/open_local_configuration.py` to create or open the ignored `.env.local`.
- Never ask the user to paste a key into the conversation. Wait for the user to save it, rerun the configuration check, and resume only when one provider reports `configured-not-verified`.
- The user's informed choice to configure and continue authorizes one minimal provider verification plus the already displayed image task; scope, provider, output-count, or cost expansion requires a new confirmation.

If the user declines API configuration or use, continue with deterministic rendering when it can meet the requirements, or return a no-image handoff. Record that choice and do not ask again in the same run. Persist only the decision and provider status in ignored run Memory, never the credential. Do not treat existing configuration as permission for a paid call.

For social visual learning, pass at most one external primary learning reference selected by `$research-social-content`. Rejected candidates must not enter the prompt or `--ref` arguments. Product-owned screenshots or logos may be supplied separately only as factual assets for an authorized edit; they are not additional competitor style references.

## Control text and structure

List every required label verbatim in the prompt. State that all rendered text must match those strings exactly and that the image may contain no other text or watermark.

For a structured diagram, enumerate nodes, arrows, order, grouping, and direction explicitly. For edits, state what must remain unchanged.

## Inspect every result

Use the Runtime's image viewer at full size. Check:

- relevance to the adjacent page content;
- whether one focal point leads the eye and the intended reading order is immediate;
- whether negative space separates hierarchy instead of feeling accidentally empty;
- whether typography, crop, and alignment feel deliberate at full size and thumbnail size;
- every rendered character;
- subject and factual details;
- arrow direction, order, and grouping;
- visual artifacts and unintended objects;
- crop, aspect ratio, and mobile readability;
- consistency with the product's visual language.

Run a subtractive second pass before adding anything: remove, merge, quiet, or resize elements that compete with the focal point. Add a new element only when the image otherwise fails its communication job. Regenerate with one targeted correction when the result fails. Use a deterministic code-native graphic when repeated attempts cannot render exact dense text or structure.

Store the selected asset in the product's normal public directory with a stable descriptive filename, suitable compression, explicit dimensions, and descriptive alt text.
