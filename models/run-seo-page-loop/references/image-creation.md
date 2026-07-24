# Image creation

## Choose useful images

Create an image when it explains the product, demonstrates an outcome, makes a process easier to understand, or provides a strong social preview. Prefer real product screenshots for product behavior and generated visuals for concepts, scenes, covers, illustrations, and supporting examples.

## Prompt from the page job

Specify:

- placement and purpose;
- subject and visible action;
- composition and aspect ratio;
- visual style and brand palette;
- exact text when text is essential;
- details that must appear;
- artifacts, logos, watermarks, and unrelated text to exclude.

Generate new assets with `executors/generate-image/generate-image.mjs`. Choose Gemini or OpenAI according to the available provider and the needs of the asset. Provide credentials through `GEMINI_API_KEY` or `OPENAI_API_KEY`; use `GOOGLE_GEMINI_BASE_URL` or `OPENAI_BASE_URL` only when the environment requires a compatible endpoint.

For long or multilingual prompts, write the prompt to a local ignored file and pass it with `--prompt-file`. Use `--ref` for each reference image when editing or carrying visual context forward.

## Verify the asset

Open every generated image and inspect it at full size. Check subject relevance, text character by character, factual details, visual artifacts, cropping, and mobile readability. Regenerate when the image misrepresents the adjacent content.

Store the selected asset in the product's standard public directory. Use a stable descriptive filename, suitable compression, explicit dimensions, and alt text that describes the image's contribution to the page.
