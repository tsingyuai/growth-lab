#!/usr/bin/env node
// 抓取 cn.bing.com SERP(playwright 真浏览器内核),输出 关键词 x 排名 x URL 矩阵。
// 用法: node scrape-bing-serp.mjs 词1 词2 ...   (在本仓库内运行,依赖根 node_modules 的 playwright)
// 输出: 控制台表格 + 当前目录 serp-results.json(可用 SERP_OUT 环境变量改名,避免多轮互相覆盖)
//
// JSON 结构: { "<词>": [{rank,domain,title,url}, ...], "__meta__": { degraded: [被降级的词] } }
// 遍历结果时跳过 "__meta__" 键。
//
// 已处理的坑:
//   - Bing 对低信任会话(curl/无 JS)可能把完整查询静默降级成首词或首字结果,
//     所以必须用真浏览器内核;抓回后还做词素相关性自检,不相干的词标记 degraded 并告警
//   - 被标记 degraded 的黑话或缩写连真浏览器冷会话也可能降级,
//     其真实 SERP 需人工登录态复核,勿据此下竞争结论
//   - Bing 结果链接是 /ck/a?...&u=a1<base64url> 跳转格式,需解码取真实 URL
//   - 请求间隔 1.5s 温和限速;BING_MARKET 可指定市场,默认 zh-CN

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  console.error('playwright 未找到:请在仓库根目录 pnpm install 后,于仓库内运行本脚本');
  process.exit(1);
}

function decodeBingUrl(href) {
  try {
    if (!href.includes('/ck/a')) return href;
    const u = new URL(href, 'https://cn.bing.com').searchParams.get('u');
    if (!u || !u.startsWith('a1')) return href;
    let b64 = u.slice(2).replace(/-/g, '+').replace(/_/g, '/');
    while (b64.length % 4) b64 += '=';
    return Buffer.from(b64, 'base64').toString('utf8');
  } catch {
    return href;
  }
}

// 词素相关性自检:中文按 2 字滑窗;拉丁语言按实词分词,要求每条结果命中至少两个词。
// 相关结果占比过低 = Bing 把查询降级成了别的东西,该词 SERP 不可信。
function relevanceRatio(keyword, results) {
  const hasCjk = /[\u3400-\u9fff]/.test(keyword);
  const terms = new Set();
  if (hasCjk) {
    const q = keyword.replace(/\s+/g, '');
    for (let i = 0; i + 2 <= q.length; i++) terms.add(q.slice(i, i + 2));
    if (!terms.size) terms.add(q);
  } else {
    for (const term of keyword.toLowerCase().match(/[a-z0-9]{3,}/g) ?? []) terms.add(term);
  }
  const requiredHits = hasCjk ? 1 : Math.min(2, terms.size);
  let hit = 0;
  for (const r of results) {
    const text = `${r.title} ${decodeURIComponent(r.url)}`.toLowerCase();
    const matches = [...terms].filter((term) => text.includes(term)).length;
    if (matches >= requiredHits) hit++;
  }
  return results.length ? hit / results.length : 0;
}

async function fetchSerp(page, keyword) {
  const market = process.env.BING_MARKET || 'zh-CN';
  const host = market.toLowerCase() === 'zh-cn' ? 'cn.bing.com' : 'www.bing.com';
  const url = `https://${host}/search?q=${encodeURIComponent(keyword)}&setmkt=${encodeURIComponent(market)}&count=20`;
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForSelector('li.b_algo', { timeout: 8000 }).catch(() => {});
  const raw = await page.$$eval('li.b_algo', (els) =>
    els.map((el) => ({
      title: el.querySelector('h2')?.innerText ?? '',
      href: el.querySelector('h2 a')?.href ?? '',
    }))
  );
  const results = [];
  for (const it of raw) {
    if (!it.href) continue;
    const realUrl = decodeBingUrl(it.href);
    let domain = '';
    try {
      domain = new URL(realUrl).hostname.replace(/^www\./, '');
    } catch {}
    results.push({ rank: results.length + 1, domain, title: it.title.trim(), url: realUrl });
  }
  return results;
}

const keywords = process.argv.slice(2);
if (!keywords.length) {
  console.error('usage: node scrape-bing-serp.mjs kw1 kw2 ...');
  process.exit(1);
}

const browser = await chromium.launch();
const page = await browser.newPage({ locale: process.env.BING_MARKET || 'zh-CN' });

const out = {};
const degraded = [];
for (const kw of keywords) {
  try {
    out[kw] = await fetchSerp(page, kw);
    const ratio = relevanceRatio(kw, out[kw]);
    const flag = ratio < 0.3 && out[kw].length > 0;
    if (flag) degraded.push(kw);
    console.log(
      `\n=== ${kw} (${out[kw].length} results${flag ? ', DEGRADED 结果与查询词不相干' : ''}) ===`
    );
    if (flag) console.log(`  !! 相关性 ${(ratio * 100).toFixed(0)}%:Bing 降级了该查询,需人工登录态复核,勿据此下结论`);
    for (const r of out[kw]) {
      console.log(`  #${String(r.rank).padStart(2)} [${r.domain}] ${r.title.slice(0, 50)}`);
      console.log(`      ${r.url.slice(0, 100)}`);
    }
  } catch (e) {
    console.error(`FAIL ${kw}: ${e.message}`);
    out[kw] = null;
  }
  await sleep(1500);
}
await browser.close();

out.__meta__ = { degraded };
const fs = await import('node:fs');
const outPath = `${process.cwd()}/${process.env.SERP_OUT || 'serp-results.json'}`;
fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
if (degraded.length) console.log(`\nDEGRADED(需人工复核): ${degraded.join(', ')}`);
console.log(`saved: ${outPath}`);
