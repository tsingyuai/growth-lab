---
name: x-browser
description: 使用仓库内 browser-first Client 对 X 做连接预检、人工登录、只读关键词搜索、严格过滤和可选媒体保存。用于 X/Twitter 调研、公开帖子采集、代理诊断和 run-social-content-loop 的来源研究；不执行互动或发布。
---

# X browser-first 只读采集

## 用户可见入口

每次先说明：X 采集默认只读，不点赞、转发、回复、关注、私信或发布。登录只授权读取公开研究证据。

按顺序执行：

1. 先由统一 onboarding 检查 `SOCIAL_PROXY_MODE`；默认 `auto` 先测试直连，失败后只尝试用户已经配置的显式或系统代理路径。
2. 所选路径不可用时明确告知当前网络不能使用 X，不擅自修改 Windows 代理、VPN 或 TUN。
3. 连接可用后检查仓库外 profile。未登录时先获得用户同意，再用 `--login-only` 打开普通 Chrome/Edge 独立窗口，由用户本人登录。脚本启动后立即退出，不控制登录表单，也不会自动关闭窗口。
4. 询问用户是只查看本轮结果，还是保存到当前 Model 的 Memory；不保存时不传 `--out`。
5. 根据用户选择决定是否使用 `--download-media`。默认只保存媒体 URL，不下载。

## 配置与安装

字段见根目录 [`CONFIGURATION.md`](../../CONFIGURATION.md)。依赖安装到仓库外环境：

```powershell
py -3.11 -m venv "$HOME\.growth-lab\clients\x-browser-venv"
& "$HOME\.growth-lab\clients\x-browser-venv\Scripts\pip.exe" install `
  -r collectors\x-browser\requirements.txt
```

默认 `X_BROWSER_PYTHON` 指向上述 venv；使用其他位置时再覆盖。

运行示例：

```powershell
$python="$HOME\.growth-lab\clients\x-browser-venv\Scripts\python.exe"
& $python collectors\x-browser\scripts\collect_x.py --preflight
& $python collectors\x-browser\scripts\collect_x.py --login-only
& $python collectors\x-browser\scripts\collect_x.py --cdp-status
& $python collectors\x-browser\scripts\collect_x.py "AI research" --limit 25 --attach
& $python collectors\x-browser\scripts\collect_x.py "目标短语" --exact --exclude "排除短语" `
  --limit 25 --out "workspaces\<product-slug>\memory\run-social-content-loop\<run>\x-search.json" --download-media --headless
```

## 连接决策

- `SOCIAL_PROXY_MODE=auto`：先测直连，再测试已配置的显式代理和系统代理；这是默认值。
- `direct`：只允许直连。
- `system`：普通浏览器完整继承操作系统代理、PAC 或代理客户端的按域名规则；Chrome 与 Edge 均适用。
- `explicit`：使用全平台共享的 `SOCIAL_PROXY_URL`；当前 X 浏览器支持 HTTP(S)、SOCKS4 和 SOCKS5 地址。
- 同一配置由 X、TikTok、Instagram 等 Growth Lab 海外平台复用；不得再创建 `X_PROXY_SERVER` 等平台专属代理字段。
- 代理地址和凭据只能放在 `.env.local` 或系统密钥管理器，不得写进 Memory、日志或提交记录。
- `SOCIAL_PROXY_BYPASS` 必须包含 `127.0.0.1,localhost,::1`，确保本机 MCP 与 CDP 不走代理。
- `SOCIAL_BROWSER_FAMILY=auto` 优先使用 Chrome，未安装时自动使用 Edge；也可设为 `edge` 或用 `SOCIAL_BROWSER_PATH` 指定浏览器。
- `X_BROWSER_CDP_PORT` 默认 `19222`，仅通过 `127.0.0.1` 连接专用浏览器。CDP 可控制整个专用 profile，只允许非正式测试账号，不能监听局域网地址。
- 专用窗口打开时用 `--cdp-status` 验证连接，用 `--attach` 采集；两者均不得关闭现有窗口。

## 采集与落盘

- 默认期望 25 条，硬上限 50；数量是目标而非保证。页面无更多精确结果时如实返回实际数量，不用算法关联结果凑数。
- `--exact` 在 Python 内部构造完整短语，并在落盘前再次检查正文；`--exclude` 同样在落盘前强制复核。
- 单浏览器、单页面、无并发；默认最多滚动 6 次，连续三轮无新增即停止。
- `--out` 省略时只报告数量，本轮不保存帖子内容。
- 保存时只写入当前产品工作区忽略的 `workspaces/<product-slug>/memory/run-social-content-loop/<run>/`，不得写进 `SOUL.md` 或版本化样本库。
- Collector 始终保存 `original_text`、`original_language` 和语言识别来源。用户要求外文中文翻译时使用 `--translate-zh`，一次批量写入 `zh_translation` 与 `translation_method`；翻译失败不得覆盖原文或落盘半成品。该选项会调用本机配置的文本模型，执行前说明调用边界并取得同意。
- X 专用浏览器启动时禁用浏览器自动翻译。若已连接窗口显示 `translated-ltr`/`translated-rtl` 页面状态，Collector 必须停止，而不是把浏览器翻译误存为原文。

## 停止条件

登录失效、代理不可用、rate limit、challenge、profile 占用、页面结构变化或重复空结果时立即停止，不自动重试或规避控制。profile、Cookie、密码和代理凭据始终留在仓库外。

## 明确不做

本 Collector 没有点赞、转发、回复、关注、私信、上传或发布代码。发布必须交给独立 Executor；当前没有官方授权 X 发布 Client 时，只能准备发布包并由人发布。
