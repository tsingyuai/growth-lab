# Growth Lab 依赖清单

每次 onboarding 都以仓库当前文件为准，并用 `rg` 补查新增的环境变量和外部命令；本表是已知基线，不是缓存状态。

审计还必须搜索 `~/.codex/skills`、`~/.claude/skills`、其他仓库脚本路径和未声明 MCP。匹配项不是待安装依赖，而是必须移除的架构违规。允许的仓库外执行物只有本表中具有公开安装来源的 CLI/Client。

## 基础 Runtime

| 依赖 | 用途 | 检查 | 配置 / 安装 | 可绕过条件 |
|---|---|---|---|---|
| Git | 拉取外部 Client、读取版本 | `command -v git` | 系统包管理器或 Git 官方安装包 | 不安装任何第三方 Client 时 |
| Python 3 | 媒体采集、归一化、lint、渲染 | `command -v python3` | Python 官方发行版或系统包管理器 | 只使用纯 Node 能力时 |
| jsonschema 4.26.0 | 跨平台编排公开 Schema 的 Draft 2020-12 meta-schema 与 fixture 测试 | 仓库外开发 venv 中运行 `python -c "import jsonschema"` | `pip install -r models/run-social-content-loop/requirements-dev.txt` | 只运行现有编排、不修改公开 Schema 时可绕过；运行时仍有标准库业务验证器 |
| Node.js | Bing、IndexNow、SEO 调研脚本、通用生图 Executor | `command -v node` | Node.js 官方发行版或版本管理器 | 不使用这些能力时 |
| Playwright + Chromium | 批量抓取 Bing SERP、渲染竞品页并截图 | `npm --prefix collectors/research-seo-demand/scripts exec playwright -- --version`，再执行一次最小 Chromium 启动检查 | `npm install --prefix collectors/research-seo-demand/scripts`，然后 `npm --prefix collectors/research-seo-demand/scripts exec playwright install chromium`；也可使用已连接的 Runtime 真实浏览器代替批量脚本 | 不做批量 SERP/竞品页面调研，或当前 Runtime 浏览器已能完成同等检查时 |
| uv | 第三方 Python Client 与临时依赖 | `command -v uv` | <https://docs.astral.sh/uv/> | 不使用媒体 Client、Playwright 渲染时 |
| Make | 小红书文案与合规检查快捷入口 | `command -v make` | Xcode Command Line Tools 或系统包管理器 | 也可直接调用仓库内检查脚本 |
| Chrome 144+ | 其他媒体平台的 MediaCrawler CDP 登录、默认 Playwright 渲染 | 检查 Chrome 版本及 `chrome://inspect/#remote-debugging` | <https://www.google.com/chrome/> | 不用 MediaCrawler 时；小红书使用独立 browser-first Client |
| 海外平台网络路径 | `SOCIAL_PROXY_MODE`;显式代理时另需 `SOCIAL_PROXY_URL`;本机绕过需 `SOCIAL_PROXY_BYPASS` | 只报告模式、URL 是否存在和 loopback 绕过，不输出代理地址或凭据 | 默认 `auto` 先测直连；按域名且跨浏览器路由使用用户已有的 Windows/PAC/代理客户端规则并选 `system` | 不使用任何海外平台时可绕过；不得自动选择、购买或轮换代理 |

## API 凭据

检查进程环境、`.env.local`、`.env`；只判断变量是否非空，不展示值。若用户允许联网验证，再执行最小、低成本 health check。

| 能力 | 满足条件 | 从哪里获取 | 说明 / 绕过 |
|---|---|---|---|
| Bing Webmaster 数据 | `BING_WEBMASTER_API_KEY` | Bing Webmaster Tools 账号的 API access | 不做 SEO 需求/表现研究可绕过 |
| IndexNow | `INDEXNOW_KEY` + 正确的 `SITE_URL`;站点可访问 key 文件 | key 由站点所有者自行生成，不需向第三方申请 | 不主动提交 URL 可绕过；`INDEXNOW_KEY_LOCATION` 可选 |
| AI 生图 | `GEMINI_API_KEY` 或 `OPENAI_API_KEY` 任一条有效 | Google AI Studio / Google Cloud；OpenAI Platform | 不生图可绕过；兼容代理才配置对应 base URL |
| TikTok 已授权账号读取 | `TIKTOK_ACCESS_TOKEN` 有效且最小身份读取成功 | TikTok for Developers 中用户自有 App 的 OAuth 授权 | 仅验证授权账号；不代表搜索或下载任意公开视频 |
| Instagram 已授权账号读取 | `INSTAGRAM_ACCESS_TOKEN` 有效且最小身份读取成功 | Meta for Developers 中用户自有 App 的 Instagram 授权 | 仅验证授权账号；账号类型、字段和权限取决于 App 配置 |

TikTok 与 Instagram 的公开内容研究不由上述 token 探针提供。仓库内 `tiktok-mcp` 与 `instagram-mcp` 已定义统一的 loopback adapter 契约、采集脚本和脱敏输出，但当前没有经过许可证与真实读取验证的 adapter Client。状态必须报告为 `missing-runtime`，不得仅凭默认端口或 OAuth token 标记就绪。选定第三方 Client 后，必须把公开来源、许可证、安装位置、账号风险门禁和最小真实读取步骤补入本清单。

API key 默认由用户自行写入根目录 `.env.local` 或通过系统密钥管理器注入，该文件已被 Git 忽略。Agent 必须先给出 [`CONFIGURATION.md`](../../../CONFIGURATION.md) 的字段和步骤；只有用户明确同意后 Agent 才能写，且不得回显值。

首次 Growth Lab 配置时，如图片 API 缺失，主动说明配置 Gemini 或 OpenAI 后宣传视觉将优先进行 API 效果探索，通常能获得更好的效果，并明确询问是否现在配置。说明后续成功调用可能计费。用户选择需要后，运行 `scripts/open_local_configuration.py` 弹出本机配置文件；保存后重新执行脱敏检查。每轮首次实际付费调用前仍需展示提供商、模型、任务范围和候选数量并再次确认。用户拒绝时使用确定性渲染或无图交付，不在同一轮重复询问。

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

### X browser-first

- 用途：X 连接预检、人工登录、关键词搜索、正文/互动/公开 URL 归一化和可选图片下载。
- Client：仓库内 [`collect_x.py`](../../../collectors/x-browser/scripts/collect_x.py)，不使用 MediaCrawler 或其他项目脚本。
- Runtime：仓库外 Python venv，默认由 `X_BROWSER_PYTHON` 指向；依赖见 `collectors/x-browser/requirements.txt`，并使用本机 Chrome 或 Edge（`auto` 自动回退）。
- 网络：统一使用 `SOCIAL_PROXY_MODE`、`SOCIAL_PROXY_URL` 和 `SOCIAL_PROXY_BYPASS`，不得创建 X 专属代理配置。
- 认证：用户在普通 Chrome/Edge 独立窗口中登录，脚本不控制表单、不自动关闭窗口；仅通过 `127.0.0.1:X_BROWSER_CDP_PORT` 连接，profile 留在仓库外，必须用连接状态、Cookie 检查和最小真实读取验证。
- 保存：用户选择；不传 `--out` 不落盘，媒体下载默认关闭。
- 权限：只读公开研究，不包含互动、私信、上传或发布。当前 X 发布只支持人类协作发布包。
- 绕过：不做 X 调研时可绕过；网络路径失败或没有测试账号时报告不可用并停止。

具体运行和停止规则见 [`collectors/x-browser`](../../../collectors/x-browser/SKILL.md)。

### MediaCrawler

- 用途：抖音、快手、B站、微博、贴吧、知乎的搜索、详情、评论、媒体和创作者采集。
- 状态检查：目标目录存在，含 `main.py` 和 `.git`；依赖环境可解析。
- 来源：<https://github.com/NanmiCoder/MediaCrawler>。
- 安装：用户确认许可证和目录后执行 `git clone`，进入目录运行 `uv sync`；记录 `git rev-parse HEAD`。
- 强制 CDP：使用 Chrome 144+ 与仓库外的专用持久化 profile，通过 `--remote-debugging-port=<port> --user-data-dir=<profile-dir>` 启动实例；必须验证 `http://127.0.0.1:<port>/json/version` 返回 DevTools JSON，并保持 `ENABLE_CDP_MODE = True`、`CDP_CONNECT_EXISTING = True` 与一致的 `CDP_DEBUG_PORT`。Chrome GUI auto-connect 页面显示的 server 不等于传统 CDP discovery endpoint，不能代替该检查。不允许回退到标准 Playwright、临时干净浏览器或 Cookie 注入。
- 认证：通过上述 CDP 连接的专用 Chrome 完成对应平台二维码/页面登录；登录会话由专用 profile 跨运行持久化。该 profile 只用非正式、可损失账号，不进入仓库或 Memory。
- 风险门禁：启动登录或抓取前，Agent 必须警告自动化抓取可能封号，要求使用非正式、可损失的专用账号，并取得用户的明确文字确认。账号被封后部分公开内容路径仍可能可用，但不保证且不得绕过风控。
- 登录状态：按平台分别检查。profile 存在只代表曾经认证；必须同时由可见页面确认已登录，并以一次低频、最小、非空的真实读取确认当前会话可用。不维护额外状态文件。
- 绕过：可逐平台选择“不配置”，也可绕过整个 MediaCrawler；一旦启用任一平台，CDP 不可绕过。Twitter/X、Reddit 不在该 Client 支持范围。
- 安装前提示用户核对上游 LICENSE；不自动升级或覆盖已有目录。

具体操作与平台检查入口见 [`collectors/media-crawler`](../../../collectors/media-crawler/SKILL.md)。小红书已有链接的详情和图片由独立 `xiaohongshu-mcp` Collector 完成。

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
