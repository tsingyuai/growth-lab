#!/usr/bin/env node
// Bing Webmaster GetKeywordStats 批量查询工具。
// 数据源:Bing 官方(真实周展现量,非估算)。用于 SEO 选词、判断需求量与季节性。
//
// 用法:
//   node fetch-keyword-stats.mjs <country> <language> <keywords-file>
//   node fetch-keyword-stats.mjs cn zh-CN keywords.txt
//   node fetch-keyword-stats.mjs us en-US keywords-en.txt
//   printf '自动化营销\n内容创作工具\n' | node fetch-keyword-stats.mjs cn zh-CN -
//
// 关键注意:
//   - language 标签大小写敏感! 必须 zh-CN / en-US(zh-cn 会返回空)。
//   - country 是 ISO 3166 两位小写(cn / us / gb ...)。
//   - keywords-file:每行一个关键词;传 "-" 表示从 stdin 读。
//   - 输出:按周均精确展现量(avgStrict)降序的表格 + 当前工作目录 CSV。
//   - 用 BING_KEYWORD_OUT 指定输出文件名,默认 bing-kw-result.csv。

import { readFileSync, writeFileSync } from 'node:fs';

// Bing Webmaster API key。只从环境变量读取,不得写入仓库。
// key 在 Bing Webmaster Tools → 设置 → API 访问里获取或重置。
const API_KEY = process.env.BING_WEBMASTER_API_KEY;
if (!API_KEY) {
  console.error('Missing Bing Webmaster API key.');
  process.exit(1);
}
const BASE = 'https://ssl.bing.com/webmaster/api.svc/json/GetKeywordStats';

const [, , country, language, file] = process.argv;
if (!country || !language || !file) {
  console.error(
    'Usage: node fetch-keyword-stats.mjs <country> <language> <keywords-file|->\n' +
      '  e.g. node fetch-keyword-stats.mjs cn zh-CN keywords.txt'
  );
  process.exit(1);
}

// 读关键词:文件或 stdin
const raw = file === '-' ? readFileSync(0, 'utf8') : readFileSync(file, 'utf8');
const keywords = raw
  .split('\n')
  .map(s => s.trim())
  .filter(Boolean);

const sleep = ms => new Promise(r => setTimeout(r, ms));

// 单次请求。空响应返回 { rows: [] }(区分"真空"与"有数据")。
async function fetchOnce(q) {
  const url = `${BASE}?q=${encodeURIComponent(q)}&country=${country}&language=${language}&apikey=${API_KEY}`;
  const res = await fetch(url);
  const j = await res.json();
  return j.d || [];
}

async function stat(q) {
  try {
    let rows = await fetchOnce(q);
    // 空响应重试一次:Bing 偶发"瞬时假空"(冷/限流),与"真·低量无数据"区分。
    if (!rows.length) {
      await sleep(500);
      rows = await fetchOnce(q);
    }
    // 仍为空 = Bing 无该词数据(低于报告阈值),记为 N/A —— 注意这不等于"0 人搜",
    // 只表示该词在 <country>/<language> 的 Bing 量太低,不代表百度/整体没需求。
    if (!rows.length)
      return { q, empty: true, avgStrict: null, avgBroad: null, peakStrict: null, latestStrict: null, weeks: 0 };
    const strict = rows.map(r => r.Impressions ?? 0);
    const broad = rows.map(r => r.BroadImpressions ?? 0);
    // Date 形如 /Date(1767427200000)/,取最新一周
    const latest = rows
      .map(r => ({ ts: Number((String(r.Date).match(/\d+/) || [0])[0]), s: r.Impressions ?? 0 }))
      .sort((a, b) => b.ts - a.ts)[0];
    const mean = a => Math.round(a.reduce((x, y) => x + y, 0) / a.length);
    return {
      q,
      empty: false,
      weeks: rows.length,
      avgStrict: mean(strict),
      avgBroad: mean(broad),
      peakStrict: Math.max(...strict),
      latestStrict: latest.s,
    };
  } catch (e) {
    return { q, empty: true, avgStrict: null, avgBroad: null, peakStrict: null, latestStrict: null, weeks: 0, err: String(e) };
  }
}

const out = [];
for (const q of keywords) {
  out.push(await stat(q));
  await sleep(350); // 温和限速,避免触发 Bing 节流
}

// 有数据的按 avgStrict 降序;无数据(N/A)的排在最后。
const cell = v => (v == null ? 'N/A' : v);
out.sort((a, b) => (b.avgStrict ?? -1) - (a.avgStrict ?? -1));
console.log(`\n===== ${country}/${language}(按周均精确展现量降序;N/A = Bing 无数据,非 0 需求)=====`);
console.log('avgStrict\tpeak\tlatest\tavgBroad\tweeks\tkeyword');
for (const r of out) {
  console.log(`${cell(r.avgStrict)}\t${cell(r.peakStrict)}\t${cell(r.latestStrict)}\t${cell(r.avgBroad)}\t${r.weeks}\t${r.q}`);
}
const na = out.filter(r => r.empty).map(r => r.q);
if (na.length) console.log(`\n注:${na.length} 个词 Bing 无数据(N/A),需换百度指数/知乎/小红书验证真实需求:\n  ${na.join('、')}`);

// 写 CSV(当前工作目录,避免污染 skill 目录)
const csvPath = `${process.cwd()}/${process.env.BING_KEYWORD_OUT || 'bing-kw-result.csv'}`;
const csv = ['keyword,avg_strict_impr,peak_strict,latest_strict,avg_broad_impr,weeks']
  .concat(out.map(r => `"${r.q}",${cell(r.avgStrict)},${cell(r.peakStrict)},${cell(r.latestStrict)},${cell(r.avgBroad)},${r.weeks}`))
  .join('\n');
writeFileSync(csvPath, csv);
console.log(`\nCSV -> ${csvPath}`);
