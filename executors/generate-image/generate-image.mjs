#!/usr/bin/env node

// Zero-dependency image generation client for Node.js 18+.
// Credentials are read exclusively from process environment variables.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const GEMINI_MODEL = 'gemini-3.1-flash-image-2k';
const OPENAI_MODEL = 'gpt-image-2';
const MODELS = new Set([GEMINI_MODEL, OPENAI_MODEL]);
const GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com';
const OPENAI_BASE_URL = 'https://api.openai.com';
const TIMEOUT_MS = 300_000;

function loadRepoEnv() {
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  const root = path.resolve(currentDir, '..', '..');
  const allowed = new Set([
    'OPENAI_API_KEY',
    'OPENAI_BASE_URL',
    'OPENAI_IMAGE_MODEL',
    'GEMINI_API_KEY',
    'GOOGLE_GEMINI_BASE_URL',
  ]);
  for (const filename of ['.env.local', '.env']) {
    const envPath = path.join(root, filename);
    if (!fs.existsSync(envPath)) continue;
    for (const rawLine of fs.readFileSync(envPath, 'utf8').split(/\r?\n/)) {
      const line = rawLine.trim();
      if (!line || line.startsWith('#') || !line.includes('=')) continue;
      const splitAt = line.indexOf('=');
      const key = line.slice(0, splitAt).trim();
      if (!allowed.has(key) || process.env[key]) continue;
      let value = line.slice(splitAt + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      process.env[key] = value;
    }
  }
}

loadRepoEnv();

function parseArgs(argv) {
  const configuredModel = process.env.OPENAI_IMAGE_MODEL;
  const defaultModel =
    configuredModel && MODELS.has(configuredModel)
      ? configuredModel
      : process.env.OPENAI_API_KEY && !process.env.GEMINI_API_KEY
        ? OPENAI_MODEL
        : GEMINI_MODEL;
  const options = {
    model: defaultModel,
    references: [],
    output: null,
    prompt: null,
    batch: null,
    outputDir: null,
    concurrency: 1,
    size: null,
    quality: null,
    force: false,
  };
  const promptParts = [];

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--out') options.output = argv[++index];
    else if (value === '--model') options.model = argv[++index];
    else if (value === '--ref') options.references.push(argv[++index]);
    else if (value === '--prompt') options.prompt = argv[++index];
    else if (value === '--batch') options.batch = argv[++index];
    else if (value === '--out-dir') options.outputDir = argv[++index];
    else if (value === '--concurrency') options.concurrency = Number(argv[++index]);
    else if (value === '--size') options.size = argv[++index];
    else if (value === '--quality') options.quality = argv[++index];
    else if (value === '--force') options.force = true;
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

function openAIEndpoint(baseUrl, route) {
  return baseUrl.endsWith('/v1') ? `${baseUrl}${route}` : `${baseUrl}/v1${route}`;
}

function referenceMimeType(filename) {
  const extension = path.extname(filename).toLowerCase();
  if (extension === '.jpg' || extension === '.jpeg') return 'image/jpeg';
  if (extension === '.webp') return 'image/webp';
  return 'image/png';
}

function saveImage(buffer, output) {
  const destination = path.resolve(output);
  if (fs.existsSync(destination)) throw new Error(`Output exists: ${destination}; pass --force to replace it`);
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
    if (options.size) form.set('size', options.size);
    if (options.quality) form.set('quality', options.quality);
    for (const filename of options.references) {
      form.append(
        'image[]',
        new Blob([fs.readFileSync(filename)], { type: referenceMimeType(filename) }),
        path.basename(filename)
      );
    }
    response = await fetch(openAIEndpoint(baseUrl, '/images/edits'), {
      method: 'POST',
      headers,
      body: form,
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } else {
    response = await fetch(openAIEndpoint(baseUrl, '/images/generations'), {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: options.model,
        prompt: options.prompt,
        n: 1,
        ...(options.size ? { size: options.size } : {}),
        ...(options.quality ? { quality: options.quality } : {}),
      }),
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

async function generate(options) {
  if (!options.output || !options.prompt) throw new Error('Each job requires prompt and output');
  if (!MODELS.has(options.model)) throw new Error(`Unsupported model. Choose one of: ${[...MODELS].join(', ')}`);
  if (options.force && fs.existsSync(path.resolve(options.output))) fs.unlinkSync(path.resolve(options.output));
  if (options.model === OPENAI_MODEL) await generateWithOpenAI(options);
  else await generateWithGemini(options);
}

function readBatch(options) {
  if (!options.outputDir) throw new Error('--batch requires --out-dir');
  if (!Number.isInteger(options.concurrency) || options.concurrency < 1 || options.concurrency > 8) {
    throw new Error('--concurrency must be an integer from 1 to 8');
  }
  return fs.readFileSync(options.batch, 'utf8').split(/\r?\n/).filter(Boolean).map((line, index) => {
    let job;
    try { job = JSON.parse(line); } catch { throw new Error(`Invalid JSON on batch line ${index + 1}`); }
    const prompt = job.prompt ?? (job.prompt_file ? fs.readFileSync(job.prompt_file, 'utf8') : null);
    const filename = job.out ?? job.output;
    if (!prompt || !filename) throw new Error(`Batch line ${index + 1} requires prompt/prompt_file and out`);
    return {
      ...options,
      batch: null,
      prompt,
      output: path.join(options.outputDir, filename),
      model: job.model ?? options.model,
      references: job.refs ?? job.references ?? [],
      size: job.size ?? options.size,
      quality: job.quality ?? options.quality,
      force: job.force ?? options.force,
    };
  });
}

async function runBatch(options) {
  const jobs = readBatch(options);
  let cursor = 0;
  const workers = Array.from({ length: Math.min(options.concurrency, jobs.length) }, async () => {
    while (cursor < jobs.length) {
      const index = cursor++;
      await generate(jobs[index]);
    }
  });
  await Promise.all(workers);
}

const options = parseArgs(process.argv.slice(2));

if (!options.batch && (!options.output || !options.prompt)) {
  console.error(
    'Usage: generate-image.mjs --out <file> [--model <model>] [--ref <image>]... [--size <size>] [--quality <quality>] [--force] ("prompt" | --prompt-file <file>)\n       generate-image.mjs --batch <jobs.jsonl> --out-dir <dir> [--concurrency 1-8] [--model <model>]'
  );
  process.exit(1);
}

try {
  if (options.batch) await runBatch(options);
  else await generate(options);
} catch (error) {
  console.error(error instanceof Error ? error.message : 'Image generation failed');
  process.exit(1);
}
