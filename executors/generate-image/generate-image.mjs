#!/usr/bin/env node

// Zero-dependency image generation client for Node.js 18+.
// Credentials are read exclusively from process environment variables.

import fs from 'node:fs';
import path from 'node:path';

const GEMINI_MODEL = 'gemini-3.1-flash-image-2k';
const OPENAI_MODEL = 'gpt-image-2';
const MODELS = new Set([GEMINI_MODEL, OPENAI_MODEL]);
const GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com';
const OPENAI_BASE_URL = 'https://api.openai.com';
const TIMEOUT_MS = 300_000;

function parseArgs(argv) {
  const options = {
    model: GEMINI_MODEL,
    references: [],
    output: null,
    prompt: null,
  };
  const promptParts = [];

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--out') options.output = argv[++index];
    else if (value === '--model') options.model = argv[++index];
    else if (value === '--ref') options.references.push(argv[++index]);
    else if (value === '--prompt-file') {
      options.prompt = fs.readFileSync(argv[++index], 'utf8');
    } else promptParts.push(value);
  }

  if (!options.prompt && promptParts.length > 0) {
    options.prompt = promptParts.join(' ');
  }
  return options;
}

function requireEnvironment(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing ${name}`);
  return value;
}

function normalizeBaseUrl(value) {
  const url = new URL(value);
  if (url.protocol !== 'https:') throw new Error('Image API base URL must use HTTPS');
  return url.toString().replace(/\/$/, '');
}

function referenceMimeType(filename) {
  const extension = path.extname(filename).toLowerCase();
  if (extension === '.jpg' || extension === '.jpeg') return 'image/jpeg';
  if (extension === '.webp') return 'image/webp';
  return 'image/png';
}

function saveImage(buffer, output) {
  const destination = path.resolve(output);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, buffer, { mode: 0o644 });
  console.log(`Saved image: ${destination} (${buffer.length} bytes)`);
}

function sanitizeMessage(message) {
  let sanitized = message
    .replace(/([?&](?:key|apikey|api_key)=)[^&\s]+/gi, '$1[REDACTED]')
    .replace(/(Bearer\s+)[^\s]+/gi, '$1[REDACTED]');
  for (const name of ['GEMINI_API_KEY', 'OPENAI_API_KEY']) {
    const secret = process.env[name];
    if (secret) sanitized = sanitized.split(secret).join('[REDACTED]');
  }
  return sanitized;
}

async function parseResponse(response, provider) {
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(`${provider} returned invalid JSON with HTTP ${response.status}`);
  }

  if (!response.ok || data.error) {
    const message =
      typeof data.error?.message === 'string'
        ? data.error.message.slice(0, 240)
        : `HTTP ${response.status}`;
    throw new Error(`${provider} request failed: ${sanitizeMessage(message)}`);
  }
  return data;
}

async function generateWithGemini(options) {
  const apiKey = requireEnvironment('GEMINI_API_KEY');
  const baseUrl = normalizeBaseUrl(
    process.env.GOOGLE_GEMINI_BASE_URL || GEMINI_BASE_URL
  );
  const parts = [{ text: options.prompt }];

  for (const filename of options.references) {
    parts.push({
      inlineData: {
        mimeType: referenceMimeType(filename),
        data: fs.readFileSync(filename).toString('base64'),
      },
    });
  }

  const response = await fetch(
    `${baseUrl}/v1beta/models/${encodeURIComponent(options.model)}:generateContent`,
    {
      method: 'POST',
      headers: {
        'x-goog-api-key': apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ contents: [{ parts }] }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    }
  );
  const data = await parseResponse(response, 'Gemini');

  for (const candidate of data.candidates ?? []) {
    for (const part of candidate.content?.parts ?? []) {
      const image = part.inlineData ?? part.inline_data;
      if (image?.data) {
        saveImage(Buffer.from(image.data, 'base64'), options.output);
        return;
      }
    }
  }
  throw new Error('Gemini response did not contain an image');
}

async function generateWithOpenAI(options) {
  const apiKey = requireEnvironment('OPENAI_API_KEY');
  const baseUrl = normalizeBaseUrl(process.env.OPENAI_BASE_URL || OPENAI_BASE_URL);
  const headers = { Authorization: `Bearer ${apiKey}` };
  let response;

  if (options.references.length > 0) {
    const form = new FormData();
    form.set('model', options.model);
    form.set('prompt', options.prompt);
    for (const filename of options.references) {
      form.append(
        'image[]',
        new Blob([fs.readFileSync(filename)], { type: referenceMimeType(filename) }),
        path.basename(filename)
      );
    }
    response = await fetch(`${baseUrl}/v1/images/edits`, {
      method: 'POST',
      headers,
      body: form,
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } else {
    response = await fetch(`${baseUrl}/v1/images/generations`, {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: options.model, prompt: options.prompt, n: 1 }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  }

  const data = await parseResponse(response, 'OpenAI');
  const image = data.data?.[0];
  if (image?.b64_json) {
    saveImage(Buffer.from(image.b64_json, 'base64'), options.output);
    return;
  }
  if (image?.url) {
    const download = await fetch(image.url, { signal: AbortSignal.timeout(TIMEOUT_MS) });
    if (!download.ok) throw new Error(`Image download failed with HTTP ${download.status}`);
    saveImage(Buffer.from(await download.arrayBuffer()), options.output);
    return;
  }
  throw new Error('OpenAI response did not contain an image');
}

const options = parseArgs(process.argv.slice(2));

if (!options.output || !options.prompt) {
  console.error(
    'Usage: generate-image.mjs --out <file> [--model <model>] [--ref <image>]... ("prompt" | --prompt-file <file>)'
  );
  process.exit(1);
}
if (!MODELS.has(options.model)) {
  console.error(`Unsupported model. Choose one of: ${[...MODELS].join(', ')}`);
  process.exit(1);
}

try {
  if (options.model === OPENAI_MODEL) await generateWithOpenAI(options);
  else await generateWithGemini(options);
} catch (error) {
  console.error(error instanceof Error ? error.message : 'Image generation failed');
  process.exit(1);
}
