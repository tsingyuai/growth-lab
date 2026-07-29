#!/usr/bin/env node
// 拆解页面"给用户看的一层": 真实浏览器渲染,截首屏+第二屏,存可见正文。
// 截图之后用当前环境可用的图片查看工具直接查看页面,从阅读钩子/转化钩子/信息密度/用户价值/调性拆解。
//
// 用法: node render-pages.mjs <输出目录> <url1> [url2 ...]
// 依赖: playwright(从当前工作目录的 node_modules 解析,请在装有 playwright 的仓库根目录运行)
//
// 已知拦截(截图会是验证页): 知乎(40362)、雷池 WAF 站、Cloudflare 站 —— 需带登录态浏览器或人工存档。

import fs from 'node:fs';
import path from 'node:path';

let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  console.error('playwright 不可用:请运行 npm install --prefix collectors/research-seo-demand/scripts');
  process.exit(1);
}

const [outDir, ...urls] = process.argv.slice(2);
if (!outDir || !urls.length) {
  console.error('usage: node render-pages.mjs <outdir> <url1> [url2 ...]');
  process.exit(1);
}
fs.mkdirSync(outDir, { recursive: true });

const slug = (url, i) => {
  try {
    return `${new URL(url).hostname.replace(/^www\./, '').replace(/\W+/g, '-')}-${i + 1}`;
  } catch {
    return `page-${i + 1}`;
  }
};

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1280, height: 900 },
  locale: 'zh-CN',
  userAgent:
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
});

for (let i = 0; i < urls.length; i++) {
  const url = urls[i];
  const name = slug(url, i);
  const page = await ctx.newPage();
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);
    await page.screenshot({ path: path.join(outDir, `${name}-s1.png`) });
    await page.evaluate(() => window.scrollBy(0, 900));
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(outDir, `${name}-s2.png`) });
    const text = await page.evaluate(() => document.body.innerText);
    fs.writeFileSync(path.join(outDir, `${name}-text.txt`), text);
    // 可见正文 < 500 字符大概率是反爬验证页
    const flag = text.length < 500 ? '  <- 疑似被反爬拦截' : '';
    console.log(`OK  ${name}: text ${text.length} chars, title="${await page.title()}"${flag}`);
  } catch (e) {
    console.log(`FAIL ${name}: ${e.message.split('\n')[0]}`);
  }
  await page.close();
}
await browser.close();
console.log(`\n截图与正文已存到: ${path.resolve(outDir)}`);
