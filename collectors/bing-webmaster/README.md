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

node collectors/bing-webmaster/bing-webmaster.mjs query-stats \
  --site https://example.com \
  --out seo-work/query-stats.json

node collectors/bing-webmaster/bing-webmaster.mjs page-query-stats \
  --site https://example.com \
  --page https://example.com/example-page \
  --out seo-work/page-query-stats.json

node collectors/bing-webmaster/bing-webmaster.mjs url-info \
  --site https://example.com \
  --url https://example.com/example-page
```

`BING_WEBMASTER_API_KEY` 必须通过当前进程环境变量提供。外部密钥管理工具或本地配置只能用于在运行前把值安全注入环境变量；Client 不直接读取密钥库、配置文件或仓库中的默认 key，也不打印包含 key 的请求 URL。

在 PowerShell 中只为当前进程设置 Key，并验证是否存在而不显示值：

```powershell
$env:BING_WEBMASTER_API_KEY = Read-Host 'Bing Webmaster API Key' -MaskInput

if ([string]::IsNullOrWhiteSpace($env:BING_WEBMASTER_API_KEY)) {
  'BING_WEBMASTER_API_KEY=<未设置>'
} else {
  'BING_WEBMASTER_API_KEY=<已设置，值已隐藏>'
}

node collectors/bing-webmaster/bing-webmaster.mjs query-stats `
  --site https://example.com `
  --out workspaces/example-product/memory/run-seo-page-loop/query-stats.json
```

凭据只通过环境变量传入 Client。不要把 Key 写入仓库、Memory、SOUL、命令参数或普通输出。原始账号数据应放在团队选择的私密 Memory 或数据路径中。

关键词接口每次最多查询 20 个词。大词表由 Agent 分批处理，并在批次间留出冷却时间。
