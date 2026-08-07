---
name: instagram-mcp
description: 通过本机 browser-first Instagram adapter 只读搜索 Instagram、下载首批帖子或 Reel 封面、补全用户选择的内容详情并脱敏归档。用于 Instagram 爆款研究、竞品内容采集、视觉参考筛选或需要与小红书采集体验一致的任务。
---

# Instagram browser-first collection

启动前读取 [runtime.md](references/runtime.md) 和
[统一服务契约](../social-browser-service-contract.md)。视觉筛选沿用
[小红书封面门禁](../xiaohongshu-mcp/references/cover-screening.md)。

## 首次说明

先由统一 onboarding 完成网络与代理前置检查。告诉用户首次默认采集 25 条，数量可调整；采集只读，本地保存脱敏研究证据、封面和用户明确选择的候选素材；登录不授权发布、点赞、评论、关注或私信。

## 运行

```powershell
python collectors/instagram-mcp/scripts/collect_instagram.py "<topic>" `
  --limit 25 --cover-pool 25 `
  --out "memory/<model>/<run>/instagram-search.json"
```

本机 adapter 未通过健康、登录和最小非空读取时，调用统一 onboarding 并报告真实状态。不得把 Graph API token 存在、端口可连接或模拟测试通过报告为真实采集就绪。

## 选择与详情

检查首批全部联系表，仅为 3–8 条通过视觉门禁的内容补详情。运行时用 `--review-selection-file "<run>/cover-selection.json"` 保持同一搜索批次；审查后写入 `{"content_ids":["<public-content-id>"]}`。向用户展示代表图、标题、公开指标、评分、风险和干净 Instagram URL。用户选择恰好一个主要视觉学习样本；不得复制原文、品牌、人物肖像、音乐、视频片段或精确构图。

## 数据边界

只写入调用 Model 的 ignored Memory。持久化公开 content ID、公开 URL、指标和本地素材；不得持久化 Cookie、access ref、签名媒体 URL、头像或原始响应。遇到验证码、challenge、限流、登录丢失或重复空结果立即停止，不绕过平台控制。
