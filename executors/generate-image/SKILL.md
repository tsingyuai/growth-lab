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

Prefer real product screenshots when the image explains product behavior. Use generated visuals for concepts, scenes, covers, illustrations, diagrams, and supporting examples.

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

Before the first provider call, run `python models/onboard-growth-lab/scripts/check_configuration.py`. If image generation is `optional-missing`, tell the user that collection, copywriting, review, and deterministic rendering can continue without an image API. When generated assets are requested, point to [`CONFIGURATION.md`](../../CONFIGURATION.md), name the OpenAI and Gemini field options, and wait for the user to configure or skip. Never ask them to paste a key into the conversation. A paid verification call requires separate approval.

## Control text and structure

List every required label verbatim in the prompt. State that all rendered text must match those strings exactly and that the image may contain no other text or watermark.

For a structured diagram, enumerate nodes, arrows, order, grouping, and direction explicitly. For edits, state what must remain unchanged.

## Inspect every result

Use the Runtime's image viewer at full size. Check:

- relevance to the adjacent page content;
- every rendered character;
- subject and factual details;
- arrow direction, order, and grouping;
- visual artifacts and unintended objects;
- crop, aspect ratio, and mobile readability;
- consistency with the product's visual language.

Regenerate with one targeted correction when the result fails. Use a deterministic code-native graphic when repeated attempts cannot render exact dense text or structure.

Store the selected asset in the product's normal public directory with a stable descriptive filename, suitable compression, explicit dimensions, and descriptive alt text.
