<div align="center">

# 🧪 Growth Lab

<p>用自然语言运行产品运营和用户增长闭环：理解产品，发现真实需求，采取行动，再从结果中找到下一步。</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![开源](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[官网](https://growthlab.tsingyuai.com)

[简体中文](./README.md) · [English](./README.en.md) · [繁體中文](./docs/readmes/README.zh-Hant.md) · [Français](./docs/readmes/README.fr.md) · [Español](./docs/readmes/README.es.md) · [Русский](./docs/readmes/README.ru.md) · [Português](./docs/readmes/README.pt.md) · [Deutsch](./docs/readmes/README.de.md) · [日本語](./docs/readmes/README.ja.md) · [한국어](./docs/readmes/README.ko.md) · [Türkçe](./docs/readmes/README.tr.md) · [Tiếng Việt](./docs/readmes/README.vi.md) · [Polski](./docs/readmes/README.pl.md)

</div>

## 为什么做 Growth Lab

大多数 AI 增长工具只解决一个局部问题：有的生成文案，有的研究竞品，有的负责发布，有的展示数据。产品上下文在不同工具之间反复丢失，真正重要的决策仍散落在仪表盘、文档、Prompt 和人工交接中。

增长是一个持续学习的闭环：

```text
理解产品
→ 判断用户与市场
→ 研究渠道与内容
→ 制定策略
→ 生成与分发
→ 收集真实结果
→ 学习并调整下一步行动
```

现代 Coding Agent 已经能够读取代码仓库、搜索网络、操作工具、编辑文件、跨上下文推理，并在会话中与人协作。Growth Lab 以 Codex 和 Claude Code 作为应用 Runtime，将这些能力组织成端到端的增长工作流。

## 产品模型

```text
会话 = 控制面
Codex 或 Claude Code = Runtime
Skill = 增长方法与工作指引
Client = 外部执行能力
文件系统 = 长期记忆
```

Skill 教 Runtime 如何理解产品、开展研究、选择工具、形成策略、制作内容、分析反馈和决定下一步。Client 工具让 Runtime 能够使用浏览器、官方 API、数据导出、内容平台和素材生成等外部能力。文件跨会话保存产品上下文、研究资料、决策与结果。

AI 会话负责控制整个工作流程。

每个 Model 都是一个“观察—行动—复盘”闭环。每个 Model 都拥有独立的持久化 Memory，用来积累按时间采集的运营数据、分析、行动结果和下一步建议。下一轮工作在开始观察前读取这些 Memory。

闭环方法论保存在 Model 中，并通过直接修改 Skill 与 references 持续演进。Memory 记录 Model 被实际使用后发生了什么。

## Growth Lab 有什么不同

### 覆盖每个增长渠道的完整生命周期

Growth Lab 的设计目标是覆盖全部增长渠道，从理解机会、选择行动，到执行、度量和决定下一步。目前已经支持 SEO 页面增长，以及小红书内容采集、爆款研究、创作、生图、卡片渲染、合规检查和发布结果复盘。

### 通过自然语言持续协作

自动化不等于一个永远脱离人类运行的后台程序。用户用自然语言持续提出目标、接收已经完成的工作与结果、提供反馈，再让 Agent 继续跟进。对话就是操作入口。

### 连接信息、方法与执行

增长信息通常留在报表中，方法存在于专家经验中，执行散落在不同工具里。Growth Lab 把三者放进同一个工作区，让 Agent 获取证据、应用方法、完成行动，再把真实结果带进下一轮。

### 开源、数据归用户、让知识自由流动

Growth Lab 完全开源，产品资料、运营数据、Memory 和产物都保存在用户自己的工作区。它不持有用户数据，不通过私有格式和封闭流程制造迁移壁垒；它致力于让有效的增长知识可以被检查、修改和自由使用。

## 如何使用

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

使用 Codex 或 Claude Code 打开该目录，然后询问 Growth Lab 能做什么，或直接描述你希望实现的增长结果。

示例：

```text
你能做什么？

理解这个产品，并运行它的第一个增长闭环。

采集小红书上与这个产品相关的高表现内容，选择可迁移的结构，完成一篇图文稿和配图。

复盘最近的结果，然后执行下一步增长行动。
```

Runtime 会读取已有 Model，建立缺失的产品和市场上下文，调用相关 Collector 与 Executor，并把证据、结果、产物和下一步行动写回工作区。

### 如何接入你的产品

用自然语言告诉 AI 你的产品仓库链接，或者现有资料放在哪里。AI 会先读取能够确认的产品事实；尚未被证据支持的用户、问题和价值会保留为待验证项，并在后续增长闭环中逐步补充。

### 通过自然语言完成配置

Growth Lab 使用一个统一的 [onboarding Skill](models/onboard-growth-lab/SKILL.md) 审计所有能力依赖，不要求用户学习额外命令或打开配置页面。你可以直接问 Agent：

```text
检查 Growth Lab 现在还缺哪些配置。
帮我配置小红书采集和生图；SEO 相关能力暂时跳过。
```

Agent 会检查 API key、第三方 Client、外部仓库、浏览器与登录态，解释缺少的配置从哪里取得，再让你决定配置或本轮绕过。小红书使用本机 browser-first `xiaohongshu-mcp`，首次默认推荐 25 条；AI 生图需要 OpenAI 或 Gemini 其中一组本地凭据。详细字段、配置位置和删除方法见 [CONFIGURATION.md](CONFIGURATION.md)。第三方 Client 与登录态仍保存在仓库外；密钥、cookie 和认证 profile 不进入 Memory。

方法与可执行脚本保存在对应 Collector / Executor / Model Skill 中。仓库不分发私有产品资料、历史采样、生成产物和运营 Memory；用户实际运行某个 Model 时，再由它创建自己的 Memory 命名空间。

## 系统组成

- 面向需求、竞品、内容与产品增长数据的 Collector；
- 协调“观察—行动—复盘”闭环与持久化 Memory 的 Model Skill；
- 面向创作、发布、人类协作与复盘的 Executor Skill；
- 展示完整增长过程的示例工作区。

## 现有能力

一个能力就是一个完整的“观察—行动—复盘”闭环，每个闭环对应一个 Model。Model 协调所需的 Collector 和 Executor，并把运营证据、执行结果与下一步行动保存在自己的 Memory 中。

| 名称 | 介绍 | 实测效果 |
|---|---|---|
| [SEO 页面增长闭环](models/run-seo-page-loop/SKILL.md) | 思考用户在什么场景下可能会需要你的产品，调研这些场景中用户会实际搜索什么，生成具有信息量、能解决用户问题，并引流到产品的 SEO 页面。 | 在我们自己的实测中，新页面执行后 1–2 天被收录；按 7 日平均口径，整体 CTR 降低 50%，页面曝光量和点击量均提高 1000%。 |
| [小红书爆款复刻与复盘闭环](models/xhs-replicate/SKILL.md) | 协调采集、创作、降 AI 味、截图、生图、卡片渲染、合规检查和发布结果复盘。 | 所创作的商业化内容，单篇最高获得 [4000+ 赞/收藏、700+ 评论](http://xhslink.cn/o/37uik9K9WHr)。真实发布仍由人完成。 |

这些数字记录了一次实际运行结果，并作为后续迭代的证据。具体效果会受到产品、域名、搜索需求、页面质量、站点权重和观察窗口影响。

## 当前状态

Growth Lab 已实现 SEO 页面增长闭环，并提供小红书复刻与结果复盘工作流。可复用 Skill、脚本、CLI 和自动检查工具保存在各自能力目录；私有产品数据、样本、截图、生成帖子与历史 Memory 均不随仓库分发。小红书发布继续保持人工边界。

如果你认同这个方向，欢迎提交 Issue，告诉我们你正在增长什么产品、当前工作流断在哪里，以及你希望 Runtime 能够使用哪些工具。

## License

Growth Lab 使用 [Apache License 2.0](./LICENSE) 开源。
