#!/usr/bin/env node
// 拆解页面"给搜索引擎看的一层": title/meta/H层级/内链体量/钩子词频。
// 用法: node analyze-page.mjs <url> [url2 ...]
// 自动探测编码(header -> meta charset),GBK/gb2312 站点可直接抓。

const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15';

function strip(s) {
  return s
    .replace(/<[^>]+>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ')
    .replace(/&#\d+;/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

async function analyze(url) {
  console.log(`\n========== ${url} ==========`);
  let res;
  try {
    res = await fetch(url, {
      headers: {
        'User-Agent': UA,
        'Accept-Language': 'zh-CN,zh;q=0.9',
        Accept: 'text/html,application/xhtml+xml',
      },
      redirect: 'follow',
      signal: AbortSignal.timeout(20000),
    });
  } catch (e) {
    console.log(`FETCH FAIL: ${e.message}`);
    return;
  }
  console.log(`HTTP ${res.status}`);
  if (!res.ok) return;

  const buf = Buffer.from(await res.arrayBuffer());
  let charset = (res.headers.get('content-type')?.match(/charset=([\w-]+)/i) || [])[1];
  if (!charset) {
    const head = buf.slice(0, 2048).toString('latin1');
    charset = (head.match(/charset=["']?([\w-]+)/i) || [])[1] || 'utf-8';
  }
  let html;
  try {
    html = new TextDecoder(charset.toLowerCase()).decode(buf);
  } catch {
    html = buf.toString('utf8');
  }

  const grab = (pat) => {
    const m = html.match(pat);
    return m ? strip(m[1]).slice(0, 200) : '(none)';
  };
  console.log(`charset: ${charset}, size: ${(buf.length / 1024).toFixed(0)}KB`);
  console.log(`title  : ${grab(/<title[^>]*>([\s\S]*?)<\/title>/i)}`);
  console.log(`desc   : ${grab(/<meta[^>]*name=["']description["'][^>]*content=["']([\s\S]*?)["']/i)}`);
  console.log(`keywords: ${grab(/<meta[^>]*name=["']keywords["'][^>]*content=["']([\s\S]*?)["']/i)}`);

  for (const level of [1, 2, 3]) {
    const hs = [...html.matchAll(new RegExp(`<h${level}[^>]*>([\\s\\S]*?)</h${level}>`, 'gi'))]
      .map((m) => strip(m[1]))
      .filter(Boolean);
    if (hs.length) {
      console.log(`h${level} x${hs.length}:`);
      for (const h of hs.slice(0, 12)) console.log(`   - ${h.slice(0, 70)}`);
      if (hs.length > 12) console.log(`   ... +${hs.length - 12} more`);
    }
  }

  const text = strip(html.replace(/<(script|style)[\s\S]*?<\/\1>/gi, ''));
  const links = (html.match(/<a\s/gi) || []).length;
  const imgs = (html.match(/<img\s/gi) || []).length;
  console.log(`正文文本: ~${text.length} 字符, 链接: ${links}, 图片: ${imgs}`);
  const hooks = ['免费', '下载', '模板', '攻略', '合集', '精选', '2025', '2026'];
  console.log(
    `钩子词频: ${hooks.map((h) => `${h}x${(html.match(new RegExp(h, 'g')) || []).length}`).join(' ')}`
  );
}

const urls = process.argv.slice(2);
if (!urls.length) {
  console.error('usage: node analyze-page.mjs <url> [url2 ...]');
  process.exit(1);
}
for (const url of urls) {
  await analyze(url);
  await new Promise((r) => setTimeout(r, 1200));
}
