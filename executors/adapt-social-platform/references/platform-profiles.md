# Platform profiles

这些档案只规定输出职责，不替代实时平台规则、官方 API 权限或发布 Client 验证。

| 平台 | 原生输出 | 必须独立决定 | 当前执行状态 |
|---|---|---|---|
| `xiaohongshu` | 标题、正文、卡片 copy、图片计划、标签 | 卡片层级、手机可读性、真实产品证据 | 卡片生成已实现；人工发布 |
| `wechat` | 标题、长文、摘要、配图位置、CTA | 论证结构、来源、预览效果 | 官方 API Client 已实现；素材、草稿、发布分别授权并待真实账号验收 |
| `x` | 单帖正文或线程计划、CTA、标签 | 短文本节奏、是否线程化、链接位置 | 只读采集、带图草稿和官方发布 Client 已实现；待真实账号最小验收 |
| `instagram` | caption、visual brief、alt text、标签计划 | 首图职责、视觉连续性、caption 节奏 | 生成契约可用；研究 adapter 和发布 Client 未验收 |
| `tiktok` | hook、脚本、shot list、字幕、caption | 前几秒信息、镜头节奏、口播与字幕配合 | 生成契约可用；研究 adapter 和发布 Client 未验收 |
| `email` | subject、preview text、正文、CTA | 发件角色、受众分段、发送与退订设置 | 生成契约可用；发送 Client 由调用产品提供 |

`platform-native` 是多平台输出的默认适配模式。`close-adaptation` 用于紧密改编。`close-replication` 是用户明确要求的高风险单目标模式：只绑定一条主参考，允许 1:1 映射卡序、信息层级、相对布局、留白节奏与截图区几何；必须保留风险确认并替换来源文字、图片、logo、人物、专有 UI 和品牌资产。不同平台的绝对互动量不得直接横向比较或预测效果。
