---
name: run-wechat-article-loop
description: 微信公众号长文增长闭环 —— 从读者问题与复刻锚选题、写出可验证的公众号长文、预览与合规检查、同步微信草稿、三重确认下受控发布，到回收阅读与转化数据并复盘。用户要求写公众号、把内容改成公众号、同步或发布微信草稿、查看公众号数据或复盘时使用。
---

# run-wechat-article-loop — 公众号长文闭环

## 这条闭环的目标

- **打开（阅读数）= 标题与首屏钩子**：让目标读者在订阅列表或转发卡片里想点开。
- **读完与转发（完读、分享、在看）= 完整解释 + 用户价值**：一篇只解决一个主问题，每节都给读者可带走的结果。
- **转化（阅读原文、产品入口点击）= 产品能力服务于方法**：产品出现在读者需要它的那一步，并有具体 CTA。

> 诚实边界：公众号打开量主要受订阅基数、推送时段和转发链路影响，单篇内容优化够不到这些结构性上限。没有粉丝基础的新号，先把文章当作可被转发、可被搜一搜收录的长期资产，而不是期望单次推送带量。

依赖缺失时触发统一的 [onboard-growth-lab](../onboard-growth-lab/SKILL.md)。本 Skill 不自行维护 onboarding。

```text
① 观察与选题 → ② 创作 → ③ 预览与检查 → ④ 草稿同步 → ⑤ 受控发布 → ⑥ 结果回收与复盘
```

## ① 观察与选题

1. 读取 `SOUL.md`；产品事实不足以支撑本篇时调用 [research-product](../../collectors/research-product/SKILL.md)，只把已确认的增量写回 `SOUL.md`。
2. 读取 `memory/run-wechat-article-loop/` 中近期文章、发布状态和复盘，避免重复选题，并沿用已被数据支持的标题/结构规律。
3. 选题证据可来自：本产品在其他渠道已验证的内容（如 `memory/xhs-replicate/` 的高表现笔记、`memory/run-seo-page-loop/` 中有展现的查询）、用户反馈、产品更新，或通过 [media-crawler](../../collectors/media-crawler/SKILL.md) 等 Collector 采集的公开需求证据。
4. 产出一句话选题：**读者问题 + 本篇给出的方法 + 产品在哪一步出现 + 1-2 篇复刻锚**。复刻锚由用户确认。

## ② 创作

按 [wechat-article-compose](../../executors/wechat-article-compose/SKILL.md) 执行，生产单元放在 `memory/run-wechat-article-loop/outputs/<YYYYMMDD-slug>/`。`source-review.md` 经用户确认后才写正文。

## ③ 预览与检查

按 [wechat-mp-publish](../../executors/wechat-mp-publish/SKILL.md) 第 1 步运行 `make wechat-preview` 与 `make wechat-render`，用真实浏览器查看 `preview.html`；`make wechat-lint` 未通过时回到 ② 修改。

## ④ 草稿同步（默认终点）

按 wechat-mp-publish 第 2 步创建草稿，本机直连或远程服务二选一。缺少凭据、IP 白名单或接口权限时，交付完整发布包（`preview.html`、`article.html`、`cover.png`、`assets/`、`wechat.yml` 中的标题与摘要）走人类协作发布。

## ⑤ 受控发布

只有用户明确要求自动发布，且三重确认齐备时才执行 wechat-mp-publish 第 3 步。否则停在草稿，请用户在后台发布后回传文章 URL 与发布时间，写入 `publish-state.json`。

## ⑥ 结果回收与复盘

用户说“看看公众号数据”“这批复盘一下”或主动提供数据时，执行 [结果回收与复盘](references/result-intake.md)。不自动触发回收，不自动修改方法。

## 保留的人工反馈点

- 选题与复刻锚确认。
- `source-review.md` 确认。
- 公众号后台草稿预览。
- 是否发布（`publish.approved` 只由用户改）。

## 不做

- 不产出小红书卡片，不复用小红书站外导流规则。
- 不批量发布、不删除已发布文章、不跳过草稿预览。
- 不让 AI 伪造产品 UI，不写 `SOUL.md` 之外无法验证的产品能力。

## Growth Lab Memory 接入

- 每篇文章的生产单元（brief、正文、配置、自检、预览、`publish-state.json`）放在 `memory/run-wechat-article-loop/outputs/<YYYYMMDD-slug>/`。
- 发布后的阅读与转化数据按月写入 `memory/run-wechat-article-loop/publish-log/YYYY-MM.md`。
- 复盘结论、下一步选题建议写入带日期的 Memory 文件，并链接对应生产单元。
- 方法改进直接修改本 Model 或对应 Executor，不写进 Memory。
