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
