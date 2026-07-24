#!/usr/bin/env node

import fs from 'node:fs/promises';

const API_BASE = 'https://ssl.bing.com/webmaster/api.svc/json';

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const options = { _: [] };

  for (let index = 0; index < rest.length; index += 1) {
    const value = rest[index];
    if (!value.startsWith('--')) {
      options._.push(value);
      continue;
    }

    const key = value.slice(2);
    const next = rest[index + 1];
    if (!next || next.startsWith('--')) {
      options[key] = true;
      continue;
    }

    options[key] = next;
    index += 1;
  }

  return { command, options };
}

function requireValue(options, name) {
  const value = options[name];
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`Missing --${name}`);
  }
  return value;
}

async function request(method, params, apiKey) {
  const url = new URL(`${API_BASE}/${method}`);
  for (const [name, value] of Object.entries(params)) {
    url.searchParams.set(name, value);
  }
  url.searchParams.set('apikey', apiKey);

  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(30_000),
  });
  const body = await response.text();

  if (!response.ok) {
    throw new Error(`Bing Webmaster request failed with HTTP ${response.status}`);
  }

  let parsed;
  try {
    parsed = JSON.parse(body);
  } catch {
    throw new Error('Bing Webmaster returned invalid JSON');
  }

  return parsed.d ?? parsed;
}

async function readKeywords(options) {
  const keywords = [...options._];
  if (typeof options.input === 'string') {
    const content =
      options.input === '-'
        ? await new Promise((resolve, reject) => {
            let input = '';
            process.stdin.setEncoding('utf8');
            process.stdin.on('data', (chunk) => {
              input += chunk;
            });
            process.stdin.on('end', () => resolve(input));
            process.stdin.on('error', reject);
          })
        : await fs.readFile(options.input, 'utf8');
    keywords.push(...content.split(/\r?\n/));
  }

  return [...new Set(keywords.map((item) => item.trim()).filter(Boolean))];
}

function wait(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function run(command, options, apiKey) {
  const siteUrl = options.site;

  switch (command) {
    case 'keyword-stats': {
      const country = requireValue(options, 'country');
      const language = requireValue(options, 'language');
      const keywords = await readKeywords(options);
      if (keywords.length === 0) throw new Error('Provide keywords or --input');
      if (keywords.length > 20) {
        throw new Error('Query at most 20 keywords per run to respect API limits');
      }

      const results = [];
      for (const keyword of keywords) {
        const data = await request(
          'GetKeywordStats',
          { q: keyword, country, language },
          apiKey
        );
        results.push({ keyword, data });
        if (keyword !== keywords.at(-1)) await wait(1_200);
      }
      return results;
    }
    case 'page-stats':
      return request('GetPageStats', { siteUrl: requireValue(options, 'site') }, apiKey);
    case 'page-query-stats':
      return request(
        'GetPageQueryStats',
        {
          siteUrl: requireValue(options, 'site'),
          page: requireValue(options, 'page'),
        },
        apiKey
      );
    case 'query-stats':
      return request('GetQueryStats', { siteUrl: requireValue(options, 'site') }, apiKey);
    case 'url-info':
      return request(
        'GetUrlInfo',
        {
          siteUrl: requireValue(options, 'site'),
          url: requireValue(options, 'url'),
        },
        apiKey
      );
    default:
      throw new Error(
        'Usage: bing-webmaster.mjs <keyword-stats|page-stats|page-query-stats|query-stats|url-info> [options]'
      );
  }
}

const { command, options } = parseArgs(process.argv.slice(2));
const apiKey = process.env.BING_WEBMASTER_API_KEY;

if (!apiKey) {
  console.error('Missing BING_WEBMASTER_API_KEY');
  process.exit(1);
}

try {
  const data = await run(command, options, apiKey);
  const output = `${JSON.stringify(data, null, 2)}\n`;
  if (typeof options.out === 'string') {
    await fs.writeFile(options.out, output, { mode: 0o600 });
    console.error(`Saved Bing Webmaster data to ${options.out}`);
  } else {
    process.stdout.write(output);
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : 'Bing Webmaster request failed');
  process.exit(1);
}
