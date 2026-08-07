---
name: x-draft-stager
description: 把用户已审核并明确批准的 X 文案保存到其专用浏览器的 X 草稿箱，但绝不发布。用于用户要求“写入 X 草稿”“保存为草稿”或验证草稿暂存流程；不用于自动发帖、互动、私信或未经确认的内容。
---

# X 草稿暂存

只处理 `social-content-package` 生成的已审核发布包。每次执行前向用户展示最终文案，并取得“保存到 X 草稿箱”的明确确认。

在任何账号写入前，要求用户明确回复与以下意思一致的声明：

> 我确认对最终文案和素材拥有充分权利或授权；我已完整审阅并知情同意其生成方式和本次代理操作；我授权 Agent 仅按当前展示版本操作，并由我承担内容、账号及发布后果；我理解本 Skill 仅为中立工具，不代表或背书任何立场。

该确认只对当前完整内容有效。文案或素材有任何变化都必须重新确认，并更新发布包中的内容哈希。

此外，发布包必须已有贯穿全部环节的 `content_governance` 确认：任何生成或处理结果在任何阶段、任何情况下都不代表 Skill 的倾向或背书；只有接受由发布者承担内容及使用后果、并确认账号操作权限时，才可使用本辅助工具。该边界在研究、生成、修改、翻译、渲染、预览、草稿、排期、发布和复用阶段始终有效。它不替代安全、合规、权利和平台规则。

执行：

```powershell
& $X_BROWSER_PYTHON executors\x-draft-stager\scripts\stage_x_draft.py `
  --manifest workspaces\<product-slug>\memory\run-social-content-loop\<run>\publish-manifest.json `
  --confirm-save-draft
```

规则：

- 连接 `127.0.0.1:X_BROWSER_CDP_PORT` 上已登录的 X 专用浏览器；不得连接局域网或公网 CDP。
- 发布包必须将 `draft_staging.approved` 设为 `true`，并保持 `publish.approved=false`、`auto_publish=false`。
- `content_authorization` 的八项确认必须全部为 `true`，包括目标账号与分发设置；`confirmed_at` 必须存在，且 `content_sha256` 必须与当前最终文案完全一致。
- 支持最多 4 张发布包内的 JPG、PNG、WebP 或 GIF。带图草稿除正文 `content_sha256` 外必须提供覆盖正文、图片相对路径及图片字节摘要的 `content_authorization.package_sha256`，任何图片变化都要求重新预览和授权。
- `content_governance` 的五项生命周期确认必须全部为 `true`，否则在账号写入前停止。
- 只允许点击文字明确为 Save/保存/保存草稿的确认按钮；按钮不符合白名单立即停止。
- 不点击 `tweetButton`、`tweetButtonInline` 或任何发布、回复、转发按钮。
- 只附加已审核且写入授权哈希的媒体，不修改原文，不保存密码、Cookie 或 token。
- 成功只表示内容进入 X 草稿箱，不代表已发布。

删除草稿是独立外部动作。只有用户针对当前发布包明确批准删除后，才可执行：

```powershell
& $X_BROWSER_PYTHON executors\x-draft-stager\scripts\stage_x_draft.py `
  --manifest <publish-manifest.json> --delete-draft --confirm-delete-draft
```

删除器必须按批准文案唯一定位草稿，仅点击 Edit/编辑和 Delete/删除白名单按钮；定位不唯一或界面变化时停止，不批量清理、不删除其他草稿。

## 已验证的安全经验

- 文案以标签结尾时，标签联想透明层可能截获第一次关闭点击。最多点击同一个、已验证处于最上层的关闭按钮两次：第一次消除联想层，第二次关闭 compose。
- 使用按钮文字白名单寻找“保存”，不要依赖单个旧版 `data-testid`。
- 保存确认层可能异步变化；不要用弹层是否立即隐藏判断成败。必须在真实 `/compose/post/unsent/drafts` 页的可见草稿列表中逐字匹配批准文案，后台 compose 正文不能算草稿。
- “保存”在确认其唯一、可见且处于最上层后只点击一次，并等待最多 12 秒；不得因界面延迟重复点击。
- 保存前先检查草稿列表；已存在完全相同文案时直接报告成功，避免重复草稿。
- 当前环境的 CDP 鼠标/键盘事件未能稳定提交 X 保存动作；真实草稿列表未命中时必须报告失败，不能调用 X 私有接口或扩大到随机 GUI 坐标。
