---
name: wechat-mp-publish
description: 通过微信公众号官方 API 把公众号文章生产单元渲染为微信排版 HTML、生成阅读页预览、上传封面与正文图片并创建草稿；在三重确认下提交发布并查询状态。支持本机直连与固定 IP 远程发布服务两种模式。用户要求预览公众号、同步微信草稿、发布公众号或查询发布状态时使用。
---

# 微信公众号草稿与受控发布

`scripts/` 是仓库自带的零依赖 Python Client（仅用标准库），只调用微信官方接口，见 [api.md](references/api.md)。输入是 [wechat-article-compose](../wechat-article-compose/SKILL.md) 产出的生产单元：

```text
<post-dir>/
├── article.md        # 必需
├── wechat.yml        # 必需
├── cover.png         # 创建草稿时必需（cover 字段可改名）
└── assets/           # 正文图片，可选
```

渲染器支持 `wechat.yml` 的 `theme`（主题名，或 `base` 加 `accent` / `text` / `background` / `link` / `ink` / `tint` / `muted` / `line` / `generic` 颜色覆盖，值可写 `#RRGGBB`）以及正文排版块 `::: card / steps / stats / bars / figure`，语法见 [wechat-article-compose](../wechat-article-compose/SKILL.md)。内置主题：`default`、`white-accent`（白底、中性灰，只用强调色点缀）。品牌色写成覆盖项：

```yaml
theme:
  base: white-accent
  accent: "#2C3E8C"
  link: "#2C3E8C"
```

运行后在同一目录写入 `preview.html`、`article.html`、`payload.json`、`publish-state.json`。

## 前置

依赖缺失时触发统一的 [onboard-growth-lab](../../models/onboard-growth-lab/SKILL.md)，本 Skill 不自行维护配置流程。

- 本机直连：`WECHAT_MP_APP_ID` / `WECHAT_MP_APP_SECRET`，且本机公网出口 IP 已加入公众号后台 API IP 白名单。
- 远程服务（推荐团队使用）：本机只配 `WECHAT_PUBLISH_SERVICE_URL` / `WECHAT_PUBLISH_SERVICE_TOKEN`；AppSecret 只放在固定 IP 服务器上，部署见 [remote-service.md](references/remote-service.md)。
- 账号主体必须具备草稿与发布接口权限：个人主体、未认证企业主体等账号的发布接口可能已被回收，报 `api unauthorized` 时说明无法自动化，改为人类协作发布。

凭据只从进程环境或根目录 `.env.local` / `.env` 读取；不得回显、写入产物或 Memory。

## 1. 预览（每次都做）

```bash
make wechat-preview POST=<post-dir>     # 生成并打开 preview.html
make wechat-render POST=<post-dir>      # article.html + dry-run payload.json
```

用真实浏览器检查 `preview.html`：标题、作者、摘要、首屏卡片、小标题节奏、图片居中与清晰度、CTA 链接。发现问题回到 `article.md` 修改后重新渲染。`article.html` 是草稿与预览共用的唯一正文，修改 `article.md` 后必须重新 render。

## 2. 创建草稿（默认终点）

```bash
make wechat-draft POST=<post-dir>          # 本机直连
make wechat-remote-draft POST=<post-dir>   # 远程服务
```

两者都先跑 `check-wechat-compliance.py`，未通过即阻断。流程：上传封面为永久素材 → 上传正文本地图片并替换为微信图片 URL → 新建草稿 → 写 `publish-state.json` 的 `draft_media_id`。正文外链图片会被拒绝，改用 `assets/` 本地图片；正文仍含 `::: figure` 配图位时同样拒绝，先换成真实图片再 render。

创建成功后请用户在公众号后台预览草稿；这是人工把关点，不跳过。

## 3. 受控发布（仅在用户明确要求时）

必须同时满足三重确认，缺任一项就停下说明原因：

1. 环境变量 `WECHAT_ENABLE_AUTO_PUBLISH=true`（远程模式在服务器 `.env`）
2. 该篇 `wechat.yml` 中 `publish.approved: true`
3. 命令显式带 `--confirm-publish`（Make 目标已内置）

```bash
make wechat-publish POST=<post-dir>
make wechat-remote-publish POST=<post-dir>   # 会把本地 wechat.yml 审批状态同步到远端
```

发布是异步的。用 status 查询并落盘 `publish_id`、`article_id`、`article_url`：

```bash
make wechat-status POST=<post-dir>
make wechat-remote-status POST=<post-dir>
```

不满足自动发布条件时，走人类协作发布：交付草稿 `media_id`、预览路径与操作说明，请用户在后台发布后回传文章 URL。

## 失败处理

| 信号 | 处理 |
|---|---|
| `invalid credential` / `40001` | 检查 AppSecret、IP 白名单；token 缓存在 `~/.growth-lab/wechat/`，可删除后重试 |
| `invalid ip` / `40164` | 把调用机器公网出口 IP 加入白名单，或改用远程服务 |
| `api unauthorized` / `48001` | 账号主体无接口权限，改人类协作发布 |
| 图片上传失败 | 检查格式（jpg/png）、大小（正文图 ≤1MB，封面 ≤10MB）与路径 |
| 草稿成功、发布失败 | 保留 `draft_media_id`，请用户到后台检查后人工发布 |

## 红线

- 不删除已发布文章，不批量发布，不跳过草稿预览。
- 不修改 `wechat.yml` 的 `publish.approved` 替用户审批。
- 不把 `.env`、AppSecret、access_token 或服务 token 写入产物、日志或 Memory。
