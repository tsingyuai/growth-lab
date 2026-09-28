# 结果回收与复盘

这是 `run-wechat-article-loop` 的内部阶段，不是独立 Skill。只在用户要求复盘，或主动提供发布结果时执行；数据回收节奏由人决定。

## 数据来源

- `memory/run-wechat-article-loop/outputs/<slug>/publish-state.json`：`article_url`、`publish_id`、发布状态。
- 公众号后台“内容分析”导出或截图：阅读、分享、在看、点赞、收藏、阅读原文、新增关注；以及打开来源（公众号消息、朋友圈、聊天会话、搜一搜、推荐）。
- 产品侧分析：带 UTM 或专用落地页的入口点击与后续转化。
- 用户在对话中补充的数据。

每次从文件系统重新检查，不维护额外状态：

```bash
ls memory/run-wechat-article-loop/publish-log/$(date +%Y-%m).md
ls -t memory/run-wechat-article-loop/publish-log/*.md | head -3
```

日志不存在就询问用户数据从哪里读取；时间点不完整只分析已观测窗口并标注缺失项。

## 发布日志模板

按月写入 `memory/run-wechat-article-loop/publish-log/YYYY-MM.md`，每篇追加一个 entry：

```markdown
---
date: YYYY-MM-DD
platform: wechat-mp
account: 账号标签（不写凭据）
slug:
article_url:
title:
article_type: 教程 / 案例 / 观点 / 更新
hook_type: 痛点 / 反差 / 结果 / 数字 / 物证
replicate_anchor:
cta:
publish_time: HH:MM
---

## 24h / 7d 数据

| 窗口 | 阅读 | 分享 | 在看 | 点赞 | 收藏 | 阅读原文 | 新增关注 | 产品入口点击 |
|---|---|---|---|---|---|---|---|---|
| 24h | | | | | | | | |
| 7d | | | | | | | | |

## 打开来源（7d）

| 公众号消息 | 聊天会话 | 朋友圈 | 搜一搜 | 推荐 | 其他 |
|---|---|---|---|---|---|
| | | | | | |

## 判定

- 与同号近 5 篇基线相比：高 / 持平 / 低 / 证据不足
- 主要贡献：标题打开 / 转发扩散 / 搜索长尾 / 证据不足
```

## 观察项

- 标题与首屏：打开率（阅读 ÷ 送达）是否高于基线。
- 读完与传播：分享、在看是否高于基线；聊天会话与朋友圈来源占比。
- CTA：阅读原文与产品入口点击是否带来转化。
- 产品露出位置与读完的关系。
- 哪类文章值得复用：教程 / 案例 / 观点 / 更新。

## 输出与方法修订

1. 写一份带日期的复盘，如 `memory/run-wechat-article-loop/YYYY-MM-DD-review.md`：窗口、来源、数据、相对基线的变化、结论与下一篇建议，并链接对应生产单元。
2. 新规律至少需要 3 篇共现证据；单篇数据不泛化。
3. 先给用户方法 diff 草案，确认后才修改本 Model 或 [wechat-article-compose](../../../executors/wechat-article-compose/SKILL.md) 的参考文件。旧规律不删除，只标注退役或修订原因。
4. 稳定的产品认知（例如某类读者对某个能力的反馈）写回 `SOUL.md`。
