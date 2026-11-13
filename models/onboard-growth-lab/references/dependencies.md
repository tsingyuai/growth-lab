# Growth Lab 依赖清单

每次 onboarding 都以仓库当前文件为准，并用 `rg` 补查新增的环境变量和外部命令；本表是已知基线，不是缓存状态。

审计还必须搜索 `~/.codex/skills`、`~/.claude/skills`、其他仓库脚本路径和未声明 MCP。匹配项不是待安装依赖，而是必须移除的架构违规。允许的仓库外执行物只有本表中具有公开安装来源的 CLI/Client。

## 基础 Runtime

| 依赖 | 用途 | 检查 | 配置 / 安装 | 可绕过条件 |
|---|---|---|---|---|
| Git | 拉取外部 Client、读取版本 | `command -v git` | 系统包管理器或 Git 官方安装包 | 不安装任何第三方 Client 时 |
| Python 3 | 媒体采集、归一化、lint、渲染 | `command -v python3` | Python 官方发行版或系统包管理器 | 只使用纯 Node 能力时 |
| Node.js | Bing、IndexNow、SEO 调研脚本、通用生图 Executor | `command -v node` | Node.js 官方发行版或版本管理器 | 不使用这些能力时 |
| Playwright + Chromium | 批量抓取 Bing SERP、渲染竞品页并截图 | `npm --prefix collectors/research-seo-demand/scripts exec playwright -- --version`，再执行一次最小 Chromium 启动检查 | `npm install --prefix collectors/research-seo-demand/scripts`，然后 `npm --prefix collectors/research-seo-demand/scripts exec playwright install chromium`；也可使用已连接的 Runtime 真实浏览器代替批量脚本 | 不做批量 SERP/竞品页面调研，或当前 Runtime 浏览器已能完成同等检查时 |
| uv | 第三方 Python Client 与临时依赖 | `command -v uv` | <https://docs.astral.sh/uv/> | 不使用媒体 Client、Playwright 渲染时 |
| Make | 小红书文案与合规检查快捷入口 | `command -v make` | Xcode Command Line Tools 或系统包管理器 | 也可直接调用仓库内检查脚本 |
| Chrome 144+ | 其他媒体平台的 MediaCrawler CDP 登录、默认 Playwright 渲染 | 检查 Chrome 版本及 `chrome://inspect/#remote-debugging` | <https://www.google.com/chrome/> | 不用 MediaCrawler 时；小红书使用独立 browser-first Client |

## API 凭据

检查进程环境、`.env.local`、`.env`；只判断变量是否非空，不展示值。若用户允许联网验证，再执行最小、低成本 health check。

| 能力 | 满足条件 | 从哪里获取 | 说明 / 绕过 |
|---|---|---|---|
| Bing Webmaster 数据 | `BING_WEBMASTER_API_KEY` | Bing Webmaster Tools 账号的 API access | 不做 SEO 需求/表现研究可绕过 |
| IndexNow | `INDEXNOW_KEY` + 正确的 `SITE_URL`;站点可访问 key 文件 | key 由站点所有者自行生成，不需向第三方申请 | 不主动提交 URL 可绕过；`INDEXNOW_KEY_LOCATION` 可选 |
| AI 生图 | `GEMINI_API_KEY` 或 `OPENAI_API_KEY` 任一条有效 | Google AI Studio / Google Cloud；OpenAI Platform | 不生图可绕过；兼容代理才配置对应 base URL |
| 微信公众号草稿与发布 | 本机直连：`WECHAT_MP_APP_ID` + `WECHAT_MP_APP_SECRET`，本机出口 IP 在白名单；或远程服务：`WECHAT_PUBLISH_SERVICE_URL` + `WECHAT_PUBLISH_SERVICE_TOKEN` | 公众号后台“设置与开发 → 基本配置”获取 AppID/AppSecret 并配置 API IP 白名单；远程服务按 `executors/wechat-mp-publish/references/remote-service.md` 自行部署 | 两种模式任一条即可。账号主体须具备草稿/发布接口权限。`WECHAT_ENABLE_AUTO_PUBLISH` 默认 false，onboarding 不替用户打开。不同步草稿、改为人类协作发布时可绕过 |
| 知乎内容采集 | 官方 `zhihu-cli` 已安装且兼容；Access Secret 已配置；一次最小请求成功 | 官方 CLI 文档 <https://developer.zhihu.com/docs?key=zhihu_cli>；Access Secret 从 <https://developer.zhihu.com/profile> 生成 | 不做知乎研究时可绕过。CLI 可从官方 CDN 安装；桌面端凭证存系统密钥链，headless 场景可由 Secret Store 注入 `ZHIHU_ACCESS_SECRET` |

API key 默认由用户自行写入根目录 `.env.local` 或通过系统密钥管理器注入，该文件已被 Git 忽略。Agent 必须先给出 [`CONFIGURATION.md`](../../../CONFIGURATION.md) 的字段和步骤；只有用户明确同意后 Agent 才能写，且不得回显值。知乎 Access Secret 是例外：桌面端通过官方 CLI 写入系统密钥链，headless 端由宿主 Secret Store 注入进程环境，不写入 `.env.local`。

## SEO 调研脚本

所有 SEO 调研脚本都随仓库分发，位于 `collectors/research-seo-demand/scripts/`：

- `fetch-keyword-stats.mjs`：聚合 Bing 周展现量并导出 CSV；只依赖 Node.js 和 `BING_WEBMASTER_API_KEY`。
- `analyze-page.mjs`：提取公开页面的 metadata、标题层级、正文和链接/图片体量；只依赖 Node.js。
- `scrape-bing-serp.mjs`：使用 Playwright 真浏览器批量抓取 SERP，并检查查询降级。
- `render-pages.mjs`：使用 Playwright 渲染竞品页，保存首屏、第二屏和可见正文。

Onboarding SEO 时分别检查“API 数据读取”和“浏览器批量调研”。缺少 Playwright 时先向用户说明它来自 npm 官方 registry、依赖安装在 `collectors/research-seo-demand/scripts/node_modules/`、Chromium 安装在 Playwright 的用户级浏览器缓存，并说明磁盘占用，再在用户确认后安装；不要把其他仓库中的 Playwright 或脚本路径当作已配置。用户选择使用 Runtime 自带的真实浏览器完成同等调研时，可以绕过批量脚本依赖，但不得绕过 SERP 相关性、登录态复核和页面真实渲染检查。

## 媒体平台第三方 Client

默认根目录：`${GROWTHLAB_CLIENT_ROOT:-$HOME/.growth-lab/clients}`。可用 `MEDIACRAWLER_DIR` 指向已有安装。第三方源码不放入 Growth Lab 仓库。

### xiaohongshu-mcp

- 用途：小红书关键词搜索、用户指定笔记详情和候选图片的 browser-first 只读采集。
- 来源：<https://github.com/xpzouying/xiaohongshu-mcp>。二进制、源码 checkout 和登录态均放在仓库外。
- 配置：`XHS_MCP_ENDPOINT`、`XHS_MCP_BINARY`、`XHS_MCP_LOGIN_BINARY`、`XHS_MCP_COOKIES_PATH`；详细字段见 [`CONFIGURATION.md`](../../../CONFIGURATION.md)。
- 状态检查：本机 endpoint health check、可见登录状态和一次低频最小读取；三者缺一不可。
- 默认批次：25 条，可调整但建议 25；单批必须保持 20–30 条并立即落盘。
- 认证：用户本人在可见窗口扫码。Cookie、token、签名媒体 URL 和登录 profile 不进入仓库或 Memory。
- 绕过：不做小红书研究时可绕过；缺少配置时不得自动降级到 MediaCrawler。

具体运行和停止规则见 [`collectors/xiaohongshu-mcp`](../../../collectors/xiaohongshu-mcp/SKILL.md)。

### 知乎官方 CLI

- 用途：通过知乎数据开放平台采集站内搜索、全网搜索、热榜和问题回答摘要；本人 `me` 能力可读取当前 Access Secret 所属账号的内容、关注和收藏。
- 来源：<https://developer.zhihu.com/docs?key=zhihu_cli>；发布清单为 <https://developer-cdn.zhihu.com/zhihu-cli/releases/stable/manifest.json>。
- 仓库入口：统一 onboarding 使用 `models/onboard-growth-lab/scripts/onboard_zhihu.py`；实际采集使用 `collectors/zhihu-open-platform/scripts/zhihu_cli.py`。安装器只从 `developer-cdn.zhihu.com` 下载，校验官方 manifest 中的大小与 SHA-256，再安装到用户应用数据目录；CLI 二进制保持在仓库外。
- 状态检查：`python3 models/onboard-growth-lab/scripts/onboard_zhihu.py status`。需要同时确认 `installed=true`、`compatible=true` 和 `auth.configured=true`，最后用 `verify` 完成一次非空真实读取。
- 配置覆盖：`ZHIHU_CLI_BIN` 可指定官方二进制绝对路径；`ZHIHU_CLI_HOME` 可指定安装根目录。不要把来源不明的 `zhihu-cli` 从 PATH 自动当成官方客户端。
- 认证：用户从官方个人中心生成 Access Secret，通过官方 CLI 的标准输入写入系统密钥链。不得作为命令行参数传入，也不得写入 `.env.local`、Memory 或仓库。仅 headless 场景由宿主 Secret Store 注入进程级 `ZHIHU_ACCESS_SECRET`。
- 验证：统一执行 `onboard_zhihu.py verify --query "<真实查询>" --yes`，它会运行 `auth status --verify` 并读取至少 1 条真实内容。`--yes` 表示用户已同意联网验证和可能发生的额度消耗。
- 数据边界：搜索结果和问题回答是摘要，不是全文；本人全文只能读取 Access Secret 所属账号。不能查询其他用户的私有数据。
- 绕过：不做知乎内容研究时可绕过；不得降级到 MediaCrawler、浏览器 Cookie 抓取或页面爬虫。

### MediaCrawler

- 用途：抖音、快手、B站、微博、贴吧的搜索、详情、评论、媒体和创作者采集。
- 状态检查：目标目录存在，含 `main.py` 和 `.git`；依赖环境可解析。
- 来源：<https://github.com/NanmiCoder/MediaCrawler>。
- 安装：用户确认许可证和目录后执行 `git clone`，进入目录运行 `uv sync`；记录 `git rev-parse HEAD`。
- 强制 CDP：使用 Chrome 144+ 与仓库外的专用持久化 profile，通过 `--remote-debugging-port=<port> --user-data-dir=<profile-dir>` 启动实例；必须验证 `http://127.0.0.1:<port>/json/version` 返回 DevTools JSON，并保持 `ENABLE_CDP_MODE = True`、`CDP_CONNECT_EXISTING = True` 与一致的 `CDP_DEBUG_PORT`。Chrome GUI auto-connect 页面显示的 server 不等于传统 CDP discovery endpoint，不能代替该检查。不允许回退到标准 Playwright、临时干净浏览器或 Cookie 注入。
- 认证：通过上述 CDP 连接的专用 Chrome 完成对应平台二维码/页面登录；登录会话由专用 profile 跨运行持久化。该 profile 只用非正式、可损失账号，不进入仓库或 Memory。
- 风险门禁：启动登录或抓取前，Agent 必须警告自动化抓取可能封号，要求使用非正式、可损失的专用账号，并取得用户的明确文字确认。账号被封后部分公开内容路径仍可能可用，但不保证且不得绕过风控。
- 登录状态：按平台分别检查。profile 存在只代表曾经认证；必须同时由可见页面确认已登录，并以一次低频、最小、非空的真实读取确认当前会话可用。不维护额外状态文件。
- 绕过：可逐平台选择“不配置”，也可绕过整个 MediaCrawler；一旦启用任一平台，CDP 不可绕过。Twitter/X、Reddit 不在该 Client 支持范围。
- 安装前提示用户核对上游 LICENSE；不自动升级或覆盖已有目录。

具体操作与平台检查入口见 [`collectors/media-crawler`](../../../collectors/media-crawler/SKILL.md)。小红书使用独立 `xiaohongshu-mcp`，知乎使用独立官方 CLI Collector。

## 微信公众号验证

- “配置存在”只说明变量非空。直连模式的最小有效性检查是一次 `get_access_token`（不产生内容、不消耗素材额度）：`40164` 表示 IP 不在白名单，`40001`/`40125` 表示凭据错误。执行前取得用户同意，不输出 token。
- 远程模式先请求 `GET <WECHAT_PUBLISH_SERVICE_URL>/healthz`；鉴权是否正确以一次 `status` 查询返回 404“远端文章不存在”而非 401 为准。
- 接口权限（`48001 api unauthorized`）只在创建草稿时暴露，状态表中标注“凭据有效，接口权限待首次草稿验证”。

## 本地工具与用户会话

| 能力 | 依赖 | 检查 | 可绕过条件 |
|---|---|---|---|
| 真实产品截图 | 仓库内 `screenshot-assets/scripts/capture.py` + uv + Chrome CDP + 用户自己的已登录会话 | 检查脚本、`uv`、Chrome、9222 CDP；登录由用户在 Chrome 完成 | 不需要真实产品截图时 |
| 小红书真实界面截图 | Python、uv、Playwright、支持 CDP 的 Chrome | 检查 CDP 端点并用 `screenshot-assets` 做一张最小截图 | 内容不需要产品界面时 |

## 每轮扫描

```bash
rg -n 'API_KEY|TOKEN|COOKIE|process\.env|os\.environ|getenv\(' collectors executors models .env.example
rg -n '\buv run\b|\bnpm exec\b|\bnpx\b|\bplaywright\b|\bchrome\b|subprocess' collectors executors models
rg -n '\.codex/skills|\.claude/skills|\.claude/|/Users/|MCP|mcp__' collectors executors models
```

发现新依赖时先纳入本轮状态表；如果是稳定依赖，再更新本清单。
