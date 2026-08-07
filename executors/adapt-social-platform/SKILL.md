---
name: adapt-social-platform
description: 把已批准的 canonical content brief 分别转换为小红书、X、Instagram、TikTok、微信公众号或邮件的原生内容包，同时保持事实、版权、品牌和授权边界；不执行发布。
---

# 跨平台内容适配

读取调用 run 中的 `research-plan.json`、`canonical-brief.json` 和 [平台档案](references/platform-profiles.md)。从一个经验证的内容概念为每个目标平台单独创作，不得强化无证据声明，也不得把同一正文复制后只改标签。

运行编排验证器：

```powershell
python models\run-social-content-loop\scripts\validate_orchestration.py `
  --run-dir workspaces\<product-slug>\memory\run-social-content-loop\<run> --stage generation
```

## 输入边界

- `research.sources` 与 `distribution.targets` 独立，来源平台不自动成为发布平台。
- 只迁移用户批准的 `learning_scope` 维度。`platform-native` 与 `close-adaptation` 不拼接原文、视觉或账号身份。用户显式选择 `close-replication` 时，允许对单一主参考做 1:1 卡序、层级、相对布局与节奏映射，但必须按 `replication_policy` 替换来源文字、图片、logo、人物、专有 UI 和品牌资产。
- 每个目标输出最多使用一个主要参考锚点，其他来源只作证据。
- 内容生成前 `content_governance` 必须全部通过；生成内容不代表 Skill 的立场。

## Xiaohongshu

Produce:

- 5 to 10 title candidates;
- selected title and reason;
- note body with line breaks suitable for mobile reading;
- card sequence with cover, card titles, per-card copy, screenshot/asset notes, and optional design direction;
- tags and topic keywords;
- comment prompt;
- save/share trigger;
- CTA and link/landing limitation;
- risk notes.

Prefer concrete student/user pain, checklist, before/after, workflow map, mistake diagnosis, prompt recipe, material-to-output pipeline, scenario story, or mini decision tree. Do not make every card the same listicle.

For academic research products, use compliant framing: lower AI-like traces by improving specificity, evidence, structure, and human revision decisions; organize materials; read, compare, summarize, question, and revise. Avoid detector-bypass promises, ghostwriting, fake citations, and assignment completion.

## WeChat official account

Produce:

- 5 to 8 title candidates;
- selected title and reason;
- article opening;
- article outline and full draft when requested;
- section headings;
- image placement and caption notes;
- excerpt;
- ending and CTA;
- source/claim notes;
- optional preview checklist.

Prefer durable reference value, clear logic, source attribution, and a stronger explanation of why the workflow matters. Do not simply paste Xiaohongshu card text into an article.

## Cross-platform consistency

Keep the same factual claim ledger and campaign code across variants. Let hook, length, visual rhythm, and CTA differ by platform.

Return variants to `$create-social-content-pack` or `$review-social-content`.

## 文风收束

- 个人号内容连续交代一组事实或功能后，检查该段是否只有“说明书信息”。如果是，选择性补一句说话者真实的判断、感受或实际影响，例如这件事为什么难兼顾、它替用户省掉了什么，或作者为什么觉得它与常见方案不同。
- 不要机械地给每段添加总结句。收束句必须带来事实清单中没有的主观位置或生活感；只是换词复述功能、拔高意义或喊口号时应删除。
- 用删除测试判断是否保留：删掉末句后如果整段立刻变成产品说明书，而末句又能自然回答“所以呢”或“这对我有什么感觉”，通常值得保留。
- 保持口语自然，避免固定使用“这就是……的意义”“真正重要的是”“不仅……更……”等模板式收束。

## 其他平台

- X：短正文、可选线程计划和来源边界。默认按标准帖子 280 加权字符的硬限制生成，中文、日文、韩文、Emoji 和链接必须使用 X 官方 `twitter-text` 规则计数，禁止用字符串原始长度代替。只有目标账号的长帖能力已经实际确认时，才能采用更长的软目标；用户想表达更多但账号不支持长帖时，应重写信息层级、把细节交给配图或落地页，不能输出无法发布的正文。官方发布 Client 已实现，但仍需真实账号、精确内容和独立授权。
- Instagram：caption、视觉 brief、alt text 和标签计划；当前研究 adapter 与发布 Client 尚未完成真实验收。
- TikTok：hook、短视频脚本、shot list、caption 和字幕边界；当前研究 adapter 与发布 Client 尚未完成真实验收。
- 邮件：subject、preview text、正文和 CTA；发送 Client 及退订设置必须由调用产品验证。

每个平台写入独立的 `packages/<platform>/`，包含 `copy.md`、`source-boundary.md`、`publish-manifest.json` 和 `assets/`。完成后对同一 run 执行 `--stage packages` 验证。生成发布包不构成草稿写入、排期或发布授权。
