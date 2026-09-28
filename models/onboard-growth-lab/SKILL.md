---
name: onboard-growth-lab
description: 通过自然语言完成 Growth Lab 的统一依赖审计与配置。检查所有能力所需的 API key、可直接安装的第三方 CLI/Client、浏览器与登录态；拒绝隐含的外部 Skill 或脚本依赖，告诉用户哪些已配置、哪些缺失、从哪里获取，并允许本轮绕过。需要首次配置、检查环境、修复依赖或询问“还缺什么”时使用。
---

# Growth Lab 统一 onboarding

这是整个系统唯一的 onboarding 入口。不要要求各业务 Skill 各自重复审计，也不要创建页面、注册全局 command 或维护配置状态机。

## 工作方式

1. 完整读取 [依赖清单](references/dependencies.md)。
2. 先运行 `python models/onboard-growth-lab/scripts/check_configuration.py`，再只读检查当前机器、已声明的第三方 Client 和认证 profile。脚本与回复都不得输出 secret、cookie、token 或认证文件内容。
3. 向用户给出一张统一状态表：`已就绪`、`缺失`、`可选`、`本轮绕过`。
4. 用自然语言询问用户要启用哪些缺失能力、哪些本轮绕过。不要替用户安装所有可选项。
5. 对用户选择启用的项目逐项处理：
   - API key：解释用途、官方获取入口、变量名和 [`CONFIGURATION.md`](../../CONFIGURATION.md) 中的本地配置步骤。默认请用户在 `.env.local` 或系统密钥管理器中自行配置；只有用户明确授权写入时才可修改 `.env.local`，且永不回显完整值。
   - 第三方 CLI/Client：必须有用户可直接访问的官方来源和安装方式；说明来源、许可证、安装位置与命令，用户确认后安装并检查版本。
   - 登录认证：启动上游或业务 Skill 已定义的原生交互流程，让用户本人扫码、OAuth 或输入验证码；认证材料不得进入仓库或 Memory。
6. 每完成一项就重新执行对应的只读检查。结束时再次输出统一状态表和本轮绕过项。

## 小红书 browser-first 就绪门禁

小红书不再经过 MediaCrawler。需要小红书采集时，按 [`xiaohongshu-mcp`](../../collectors/xiaohongshu-mcp/SKILL.md) 独立检查：

1. 告诉用户首次默认采集 25 条，数量可调整，但建议 25 条。
2. 检查 `XHS_MCP_ENDPOINT`、`XHS_MCP_BINARY`、`XHS_MCP_LOGIN_BINARY` 和仓库外 `XHS_MCP_COOKIES_PATH`，不读取或输出登录态内容。
3. 缺少配置时显示 [`CONFIGURATION.md`](../../CONFIGURATION.md) 的准确位置、需要填写的字段及用途，然后停下等待用户配置或选择本轮绕过。
4. 服务未运行时先说明将启动本机只读服务；登录缺失时说明授权边界并在用户确认后打开可见二维码登录窗口。
5. 只有本机 health check、登录状态和一次低频最小读取全部成功，才报告 `已就绪，可立即抓取`。遇到风控、验证、超时或空响应立即停止，不自动重试或规避平台控制。

小红书登录只授权读取公开研究证据，不授权点赞、收藏、评论、关注、上传或发布。

## MediaCrawler 风险确认与就绪门禁

MediaCrawler 的安装、登录和实际抓取必须在本统一 onboarding 中完成，不得把“已安装”或“有 profile”报告为可用。

1. 在启动 Chrome、二维码登录或任何真实抓取前，通过 Agent 对话原意告知：
   - 自动化抓取可能触发平台风控，导致限流、验证、登录失效或封号。
   - 不要使用正式账号、主账号或承载重要资产的账号；使用者应准备可损失的专用账号。
   - 账号被封后，部分公开内容在不需要该账号的路径上仍可能采集，但不保证持续可用，也不得尝试绕过平台风控。
2. 请用户明确回复类似“我已了解封号风险，并确认使用非正式、可损失的专用账号”。沉默、模糊回复或仅要求“继续”不构成确认。未取得确认就停在风险门禁，不启动登录和抓取。
3. 确认后，让用户选择需要启用的平台：抖音、快手、B 站、微博、贴吧、知乎。小红书使用独立的 browser-first 就绪门禁。未启用的平台必须由用户明确说“本轮绕过”，不得默认忽略。
4. 只要启用任一 MediaCrawler 平台，必须先完成不可绕过的 Chrome CDP onboarding：Chrome 版本至少 144；为 MediaCrawler 启动一个使用仓库外持久化 profile 的专用 Chrome 实例，同时显式传入 `--remote-debugging-port=<port>` 和 `--user-data-dir=<profile-dir>`；`curl --noproxy '*' http://127.0.0.1:<port>/json/version` 必须返回可解析的 Chrome DevTools JSON；MediaCrawler 配置为 `ENABLE_CDP_MODE = True`、`CDP_CONNECT_EXISTING = True` 且 `CDP_DEBUG_PORT = <port>`。Chrome 144+ 在 `chrome://inspect/#remote-debugging` 中的 GUI auto-connect 服务不提供 MediaCrawler 所需的 `/json/version`，不得把“Server running”字样单独当成通过。任一项失败就报告 `CDP 未就绪`并停止，不得回退到标准 Playwright、临时干净浏览器或 Cookie 注入。CDP 不允许本轮绕过；用户只能绕过整个 MediaCrawler 能力或某个平台。
5. 对每个启用平台依次执行 [MediaCrawler operations](../../collectors/media-crawler/references/operations.md) 的登录就绪检查。必须同时满足：CDP 连接已验证、页面显示已登录、最小真实读取成功、产出非空且无登录/风控信号。
6. 只有上述四项全部通过才报告该平台为 `已就绪，可立即抓取`。其他状态使用 `CDP 未就绪`、`待登录`、`验证失败`、`触发风控` 或 `本轮绕过`；不维护额外状态文件。

## 依赖边界

- Growth Lab 调用的脚本必须位于本仓库。不得调用 `~/.codex/skills`、`~/.claude/skills`、其他项目脚本或某个 Agent 产品的私有认证文件。
- 仓库外只允许用户可从官方渠道直接安装的 CLI/Client，以及用户自己的浏览器登录会话。
- 发现隐含外部 Skill/脚本时，不要尝试安装或读取；报告为仓库缺陷，改用仓库内脚本或声明为可安装的第三方 Client。
- API 服务不等于 Client；调用代码必须随仓库分发，凭据由本 Skill 配置。

## 判断原则

- “配置存在”与“配置有效”分开报告。环境变量非空只能证明存在；只有安全的 health check 或一次真实调用成功才能证明有效。MediaCrawler 的安装、CDP 和登录页各自通过仍不足以证明可用，必须完成最小真实读取。
- 用户可随时说“我不需要 SEO / 不需要生图 / 不需要小红书详情提取”。将相关依赖标成`本轮绕过`，不要继续追问。
- MediaCrawler 的 Chrome CDP 是不可分割的强制依赖，不是可选项。用户可以绕过 MediaCrawler 或某个平台，不得在保留抓取能力的同时绕过 CDP。
- 替代关系必须显式呈现。例如生图只需 Gemini 或 OpenAI 其中一条；小红书使用 `xiaohongshu-mcp`，其余六个已声明媒体平台共用 MediaCrawler。
- 不把“本轮绕过”持久化成全局状态。下一次 onboarding 重新检查并结合当次目标询问。
- 不修改业务 Memory 来保存环境状态。Memory 只保存增长过程与结果。
- 安装、登录或联网验证属于有副作用操作；先说明动作并获得用户确认。只读检查可直接执行。

## 交付格式

先给结论，再给统一状态表：

| 能力 | 状态 | 缺少什么 / 下一步 |
|---|---|---|
| SEO 数据读取 | 缺失 | `BING_WEBMASTER_API_KEY`；从 Bing Webmaster Tools 获取 |
| SEO 批量 SERP 与页面渲染 | 缺失 | Node.js 已安装；需从 npm 安装 Playwright 与 Chromium，或确认使用当前 Runtime 真实浏览器完成同等检查 |
| IndexNow 提交 | 本轮绕过 | 用户不需要主动提交 URL |
| AI 生图 | 已就绪 | OpenAI 凭据存在；尚未做付费调用验证 |
| 小红书只读采集 | 缺失 | 按 `CONFIGURATION.md` 配置本机 xiaohongshu-mcp 二进制并完成可见扫码登录 |
| 媒体平台采集 | CDP 未就绪 | Chrome GUI auto-connect 已开启，但 `/json/version` 为 404；需启动带持久化 profile 和显式 debug port 的专用 Chrome |

最后只问当前确实需要用户决策或提供的信息，不把完整清单再次变成问卷。
