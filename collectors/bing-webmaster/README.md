# Bing Webmaster collector

从 Bing Webmaster API 读取关键词热度、页面表现、查询表现与 URL 索引信息。Client 使用 Node.js 原生 `fetch`，只输出 Bing 返回的原始数据，由 Agent 根据当前问题现场分析。

```bash
export BING_WEBMASTER_API_KEY='...'

node collectors/bing-webmaster/bing-webmaster.mjs keyword-stats \
  --country cn --language zh-CN \
  "关键词一" "关键词二" \
  --out seo-work/keyword-stats.json

node collectors/bing-webmaster/bing-webmaster.mjs page-stats \
  --site https://example.com \
  --out seo-work/page-stats.json

node collectors/bing-webmaster/bing-webmaster.mjs page-query-stats \
  --site https://example.com \
  --page https://example.com/example-page \
  --out seo-work/page-query-stats.json

node collectors/bing-webmaster/bing-webmaster.mjs url-info \
  --site https://example.com \
  --url https://example.com/example-page
```

`BING_WEBMASTER_API_KEY` 必须来自当前 shell、系统密钥管理工具或 workspace 外的本地环境文件。Client 不读取仓库中的默认 key，也不打印包含 key 的请求 URL。

关键词接口每次最多查询 20 个词。大词表由 Agent 分批处理，并在批次间留出冷却时间。
