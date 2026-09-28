# 微信公众号官方接口与权限

## 使用的接口

| 能力 | 接口 | Client 方法 |
|---|---|---|
| 获取 `access_token` | `GET /cgi-bin/token` | `WechatClient.get_access_token` |
| 上传正文图片 | `POST /cgi-bin/media/uploadimg` | `upload_image_for_content` |
| 上传永久封面素材 | `POST /cgi-bin/material/add_material?type=image` | `upload_cover_material` |
| 新增草稿 | `POST /cgi-bin/draft/add` | `add_draft` |
| 发布草稿 | `POST /cgi-bin/freepublish/submit` | `publish` |
| 查询发布状态 | `POST /cgi-bin/freepublish/get` | `publish_status` |

官方文档：

- 发布能力：<https://developers.weixin.qq.com/doc/service/guide/product/publish.html>
- 草稿箱：<https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html>
- 素材管理：<https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html>
- 获取 access_token：<https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html>

## 权限前置

1. 在公众号/服务号后台“设置与开发 → 基本配置”获取 `AppID`，启用并保存 `AppSecret`。
2. 把调用机器的公网出口 IP 加入 API IP 白名单。家庭宽带、笔记本等出口 IP 易变，长期使用推荐 [远程发布服务](remote-service.md)。
3. 账号主体必须具备发布接口权限。官方发布能力页提示：2025 年 7 月起，个人主体账号、企业主体未认证账号及不支持认证的账号会被回收相关接口调用权限。

## 环境变量

| 变量 | 必需 | 说明 |
|---|---|---|
| `WECHAT_MP_APP_ID` / `WECHAT_MP_APP_SECRET` | 直连模式必需 | 公众号凭据 |
| `WECHAT_MP_ACCOUNT_LABEL` | 可选 | 账号标签，仅用于区分记录 |
| `WECHAT_MP_DEFAULT_AUTHOR` | 可选 | `wechat.yml` 未写 author 时使用 |
| `WECHAT_MP_DEFAULT_SOURCE_URL` | 可选 | “阅读原文”默认链接 |
| `WECHAT_ENABLE_AUTO_PUBLISH` | 可选 | 默认 `false`，只允许建草稿 |
| `WECHAT_TOKEN_CACHE_PATH` | 可选 | 默认 `~/.growth-lab/wechat/access-token.json`，权限 600 |
| `WECHAT_PUBLISH_SERVICE_URL` / `WECHAT_PUBLISH_SERVICE_TOKEN` | 远程模式必需 | 远程发布服务地址与内部 token |

## wechat.yml 字段

`title`（必需）、`digest`、`author`、`content_source_url`、`cover`（默认 `cover.png`）、`theme`（主题名或一层颜色覆盖）、`pic_crop_235_1` / `pic_crop_1_1`（封面裁剪，`X1_Y1_X2_Y2` 相对坐标）、`need_open_comment`、`only_fans_can_comment`、`publish.mode`、`publish.approved`。解析器只支持简单的 `key: value` 与一层嵌套，不支持列表和多行字符串。

## publish-state.json

`status`（`draft_created` / `publish_submitted`）、`draft_media_id`、`publish_id`、`article_id`、`article_url`、`image_mapping`、`publish_status_response`、`updated_at`。远程模式额外记录 `remote_slug`、`remote_status`、`remote_state`。
