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

Generate with the Runtime's native image tool when available. If the product workspace uses an external image Client, provide credentials through environment variables such as `OPENAI_API_KEY` or `GEMINI_API_KEY` and follow that Client's documented interface.

## Verify the asset

Open every generated image and inspect it at full size. Check subject relevance, text character by character, factual details, visual artifacts, cropping, and mobile readability. Regenerate when the image misrepresents the adjacent content.

Store the selected asset in the product's standard public directory. Use a stable descriptive filename, suitable compression, explicit dimensions, and alt text that describes the image's contribution to the page.
