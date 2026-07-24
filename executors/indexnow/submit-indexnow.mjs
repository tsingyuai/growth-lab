#!/usr/bin/env node

import fs from 'node:fs/promises';

function parseArgs(argv) {
  const options = { urls: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--input') {
      options.input = argv[index + 1];
      index += 1;
    } else {
      options.urls.push(value);
    }
  }
  return options;
}

async function readUrls(options) {
  const urls = [...options.urls];
  if (options.input) {
    const content = await fs.readFile(options.input, 'utf8');
    urls.push(...content.split(/\r?\n/));
  }
  return [...new Set(urls.map((url) => url.trim()).filter(Boolean))];
}

const options = parseArgs(process.argv.slice(2));
const key = process.env.INDEXNOW_KEY;
const siteUrl = process.env.SITE_URL;

if (!key) {
  console.error('Missing INDEXNOW_KEY');
  process.exit(1);
}
if (!siteUrl) {
  console.error('Missing SITE_URL');
  process.exit(1);
}

try {
  const site = new URL(siteUrl);
  const urls = await readUrls(options);
  if (urls.length === 0) throw new Error('Provide one or more URLs or --input <file>');
  if (urls.length > 10_000) throw new Error('IndexNow accepts at most 10000 URLs per request');

  for (const value of urls) {
    const url = new URL(value);
    if (url.host !== site.host) {
      throw new Error(`URL host does not match SITE_URL: ${url.host}`);
    }
  }

  const keyLocation =
    process.env.INDEXNOW_KEY_LOCATION || `${site.origin}/${encodeURIComponent(key)}.txt`;
  const response = await fetch('https://api.indexnow.org/indexnow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({
      host: site.host,
      key,
      keyLocation,
      urlList: urls,
    }),
    signal: AbortSignal.timeout(60_000),
  });

  if (![200, 202].includes(response.status)) {
    throw new Error(`IndexNow submission failed with HTTP ${response.status}`);
  }

  process.stdout.write(
    `${JSON.stringify({ submitted: urls.length, status: response.status }, null, 2)}\n`
  );
} catch (error) {
  console.error(error instanceof Error ? error.message : 'IndexNow submission failed');
  process.exit(1);
}
