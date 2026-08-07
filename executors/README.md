# Executors / 执行器

Executors turn growth decisions into concrete action. They teach the Coding Agent how to create, adapt, distribute, and review growth work.

执行器把增长决策转化为具体行动，教 Coding Agent 如何创作、适配、分发和复盘增长工作。

## Scope / 范围

- Content concepts, copy, images, video, and landing-page assets / 内容创意、文案、图片、视频与落地页素材
- Channel-specific adaptation / 渠道适配
- Campaign and publishing preparation / Campaign 与发布准备
- Authorized publishing through Clients / 通过 Client 进行已授权发布
- Human-assisted publishing / 人类协作发布
- Result collection and review / 结果采集与复盘

## Human-assisted publishing / 人类协作发布

The Agent prepares a publication package containing the final content, assets, target channel, timing suggestion, settings, links, and clear operating instructions. It then asks a person to publish through the platform's normal interface and uses the returned URL or screenshot for subsequent review.

Agent 准备完整发布包，包括最终内容、素材、目标渠道、时间建议、设置、链接与清晰的操作说明；随后召唤人类通过平台正常界面发布，并获取发布 URL 或截图用于后续复盘。

Human-assisted publishing follows platform rules and preserves human judgment for account-sensitive actions. Automated publishing uses official, authorized interfaces exposed through a Client.

人类协作发布遵守平台规则，并在账号敏感操作中保留人的判断。自动发布通过 Client 暴露的官方授权接口执行。

## Available executors / 已有执行器

- [`create-seo-page`](create-seo-page/SKILL.md)：依据需求与 SERP 证据设计、创作并实现高质量 SEO 页面。
- [`review-seo-page`](review-seo-page/SKILL.md)：用删除、反转、换标题、去品牌和图文测试对抗式审查 SEO 页面。
- [`generate-image`](generate-image/SKILL.md)：通过 Gemini 或 OpenAI 执行生图与参考图编辑，并完成逐图质检。
- [`review-seo-performance`](review-seo-performance/SKILL.md)：读取 Bing 与产品数据，诊断页面效果并现场生成 HTML 复盘。
- [`indexnow/`](indexnow/)：向 IndexNow 提交已经上线、更新或删除的 URL。
- [`xhs-render-cards`](xhs-render-cards/SKILL.md)：以一条总 SOP 完成强制 DAI、image-plan、视觉参考图与真实浏览器截图共同生图和质量检查。
- [`screenshot-assets`](screenshot-assets/SKILL.md)：截取、归档并复用小红书内容所需的真实产品 workspace 截图。
- [`social-content-package`](social-content-package/SKILL.md)：把一个已确认参考与真实产品事实整理为通用社交内容发布包，默认停在人工发布准备状态。
- [`adapt-social-platform`](adapt-social-platform/SKILL.md)：从同一 canonical brief 为 X、小红书、微信公众号、Instagram、TikTok 或邮件生成彼此独立的平台原生版本。
- [`x-draft-stager`](x-draft-stager/SKILL.md)：把用户明确批准的发布包保存到 X 草稿箱并复核，绝不点击发布。
- [`publish-x-official`](publish-x-official/SKILL.md)：通过 X 官方 API 发布已审核的文字/图片内容；发帖与删除分别授权。
- [`publish-xiaohongshu-assisted`](publish-xiaohongshu-assisted/SKILL.md)：准备人工发布包，或在本次明确批准后通过本机 xiaohongshu-mcp 执行浏览器自动发布。
- [`publish-wechat-official-account`](publish-wechat-official-account/SKILL.md)：通过微信公众号官方 API 分步上传素材、创建草稿、提交发布和查询状态。
- [`render-social-video`](render-social-video/SKILL.md)：可选的产品视频生成器；默认用真实截图、字幕、可选配音和白名单动效确定性输出 1080×1920 或 1440×1920 MP4，也可在逐次付费授权后导入经过下载、解码和清单校验的 Seedance B-roll。只在目标明确要求视频时进入主流程。
- [`capture-screen-video`](capture-screen-video/SKILL.md)：在用户确认范围后录制 Windows 指定窗口、屏幕区域或完整桌面，输出经过解码校验和哈希绑定的 MP4/来源清单，供产品演示视频复用。
- [`render-card-animation`](render-card-animation/SKILL.md)：把已审核卡片文案与视觉规范渲染为隔离的 1080×1920 HTML 动画，输出经过解码校验和来源哈希绑定的 MP4，且不冒充真实产品证据。
