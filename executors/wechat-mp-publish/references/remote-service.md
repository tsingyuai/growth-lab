# 远程发布服务

微信接口要求调用方 IP 在白名单内。把 API 调用固定到一台有公网固定 IP 的服务器上：本地只上传文章包，`AppSecret` 只存在服务器。

## 服务器配置

1. 在公众号后台启用 `AppSecret`，把服务器公网出口 IP 加入 API IP 白名单。
2. 生成内部 token：`python3 -c "import secrets; print(secrets.token_urlsafe(48))"`。
3. 在服务器部署目录新建 `.env`，模板见 [`deploy/server.env.example`](../deploy/server.env.example)。这份 `.env` 与本地 Growth Lab 的 `.env.local` 分开维护。

## 构建与启动

在 Growth Lab 仓库根目录构建镜像（镜像同时包含发布 Client 与合规 lint）：

```bash
make wechat-publisher-build
```

把镜像与 [`deploy/docker-compose.yml`](../deploy/docker-compose.yml) 放到服务器部署目录，与 `.env` 同级，然后：

```bash
docker compose -p wechat-publisher up -d
```

compose 默认把 `127.0.0.1:8080` 暴露在本机。对公网提供服务时必须放在 HTTPS 反向代理（Nginx、Caddy、Traefik 等）之后，不以明文 HTTP 暴露 token。

## 本地调用

本地 `.env.local`：

```bash
WECHAT_PUBLISH_SERVICE_URL="https://<your-publisher-domain>"
WECHAT_PUBLISH_SERVICE_TOKEN="<与服务器一致的 token>"
```

```bash
make wechat-remote-draft POST=<post-dir>
make wechat-remote-publish POST=<post-dir>
make wechat-remote-status POST=<post-dir>
```

远端 slug 默认取文章目录名，只允许字母、数字、点、下划线和短横线。

## 接口

- `GET /healthz`：健康检查，无需 token。
- `POST /v1/wechat/draft`：上传文章包（`article.md`、`article.html`、`wechat.yml`、`cover.*`、`assets/`，单文件 ≤8MB），服务端跑合规 lint 后建草稿。
- `POST /v1/wechat/publish`：提交发布，需 `confirm_publish=true`；可只同步 `wechat.yml` 审批状态。
- `GET /v1/wechat/status?slug=...`：查询发布状态。

除 `/healthz` 外都需要 `Authorization: Bearer <WECHAT_PUBLISH_SERVICE_TOKEN>`。

远程模式同样执行三重确认：服务器 `WECHAT_ENABLE_AUTO_PUBLISH=true`、该篇 `publish.approved: true`、请求带 `confirm_publish=true`。
