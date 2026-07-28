# MediaCrawler operations

## Install and upgrade

Source: `https://github.com/NanmiCoder/MediaCrawler`. The repository is external because its license is for non-commercial learning/research. The unified onboarding Skill must obtain confirmation before clone/install/update.

```bash
git clone https://github.com/NanmiCoder/MediaCrawler.git "$HOME/.growth-lab/clients/MediaCrawler"
cd "$HOME/.growth-lab/clients/MediaCrawler"
uv sync
uv run playwright install chromium
```

For an existing checkout, inspect `git status`, remote, branch and commit first. Do not overwrite local config. Fetch and show the prospective update before merging.

## Authentication

Required: Chrome 144+ launched with an explicit remote-debugging port and a dedicated persistent profile outside the repository, upstream `ENABLE_CDP_MODE = True`, `CDP_CONNECT_EXISTING = True`, and matching `CDP_DEBUG_PORT`, then `--lt qrcode`. Let the user complete each platform's login/QR challenge in this Chrome. Standard Playwright, an ephemeral clean browser, and Cookie injection are prohibited fallbacks. Chrome's GUI auto-connect server is not sufficient unless `/json/version` returns valid DevTools JSON.

### 强制风险确认

在启动 Chrome、展示二维码或执行任何抓取命令前，必须由 `onboard-growth-lab` 通过 Agent 对话警告用户：自动化抓取可能导致限流、验证、会话失效或封号；不要使用正式账号或承载重要资产的账号。账号被封后，部分公开内容路径仍可能可用，但不保证，也不允许绕过风控。

只有用户明确回复已理解封号风险，并确认使用非正式、可损失的专用账号，才能继续。不得从“继续”、沉默或既往抓取行为推断确认。

### 逐平台就绪验证

对用户要启用的每个平台单独完成以下流程，不得用一个平台的登录结果代表其他平台：

1. 检查 Chrome 版本至少 144，为 MediaCrawler 选择一个固定、仓库外的 profile 目录和未占用端口。默认可使用 `$HOME/.growth-lab/browser-profiles/mediacrawler-chrome` 和 `9223`。
2. 使用安装的 Chrome 启动该实例：`<chrome> --remote-debugging-port=<port> --user-data-dir=<profile-dir> --no-first-run --no-default-browser-check`。这是持久化专用 profile，不得每轮创建临时目录。
3. 确认外部 checkout 中 `ENABLE_CDP_MODE = True`、`CDP_CONNECT_EXISTING = True` 且 `CDP_DEBUG_PORT = <port>`。用 `curl --noproxy '*' http://127.0.0.1:<port>/json/version` 确认返回包含 `webSocketDebuggerUrl` 的可解析 JSON；当前 shell 有代理时必须绕过 localhost。
4. 启动 MediaCrawler 后，从日志确认成功连接该浏览器上下文。若 CDP 超时或连接失败，立即停止；不允许继续使用上游的标准模式 fallback。
5. 以 `--platform <platform> --lt qrcode --type search` 启动单平台流程，让用户在可见 Chrome 中完成扫码、验证码或安全挑战。
6. 在可见页面检查已登录标志（例如用户头像或账号入口）。不读取、输出或复制 cookie/token。
7. 执行一次低频最小真实读取：优先使用一条带平台临时访问参数的完整公开 URL 进行 `detail`，最多 1 条、并发 1、关闭评论和媒体下载，保存为 JSONL。若只能从 `search` 开始，先确认当前上游是否会对整个首页 fan-out；`CRAWLER_MAX_NOTES_COUNT=1` 不一定会把单页详情任务严格限制为 1 条。先检查当前版本 CLI 参数与配置项，不假设旧参数仍有效。
8. 定位本次新修改的输出，确认至少有 1 条可解析的内容记录，且日志中没有登录失效、人机验证或风控信号。删除或明确标记这份 onboarding 测试数据，不写入业务 Memory。
9. 只有第 1–8 步全部通过才返回 `已就绪，可立即抓取`。若失败，保留真实失败状态并停止；不自动重试、轮换账号或规避挑战。

Do not use Cookie mode as an onboarding or recovery path. Never ask the user to paste cookies, tokens, or browser authentication material into a file or transcript.

## Shared configuration

Inspect `config/base_config.py` on the installed commit; do not assume old defaults. Important fields currently include `PLATFORM`, `KEYWORDS`, `CRAWLER_TYPE`, `LOGIN_TYPE`, `CRAWLER_MAX_NOTES_COUNT`, `MAX_CONCURRENCY_NUM`, `ENABLE_GET_COMMENTS`, `CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES`, upstream-spelled `ENABLE_GET_MEIDAS`, `SAVE_DATA_OPTION`, and proxy/database options.

Prefer CLI overrides for platform/login/type. Edit only fields without a CLI override. Media download can be large and must be explicitly requested.

## Modes and outputs

- `search`: keyword discovery; configure `KEYWORDS`.
- `detail`: exact content IDs/URLs; configure the platform-specific specified list.
- `creator`: creator/profile crawl; configure the platform-specific creator list.

The installed version controls output schema and path, commonly under `data/<platform>/`. Locate newly modified output files after the run rather than hard-coding a stale filename. Copy—not move—the evidence required by the caller into its Memory and record source paths.

## Failure ladder

1. Stop and capture the exact command, commit, traceback/status, config diff, and last successful action.
2. Validate Chrome/CDP reachability and that the correct platform account is visibly logged in.
3. Validate URL/ID format against the platform Skill and installed config examples.
4. Compare the checkout with the current official repository/issues; update only after user confirmation.
5. Reduce to one keyword/URL, comments off, media off, concurrency one.
6. If authentication/risk control persists, stop. Ask the user to re-authenticate or defer/bypass that platform. Never rotate accounts, evade challenges, or loop retries.

Do not treat empty output as success. Distinguish genuinely empty results, login failure, risk control, parser/schema breakage, and partial media failure.
