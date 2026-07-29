<a id="english"></a>

<div align="center">

# 🧪 Growth Lab

<p>Run product operations and user growth loops through natural language: understand your product, find real demand, take action, and learn what to do next.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Open Source](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[English](#english) · [中文](#中文)

</div>

## Why Growth Lab

Most AI growth tools solve one fragment of the problem. Some generate copy, some research competitors, some schedule posts, and some display analytics. Product context is repeatedly lost between these tools, while the most important decisions still depend on disconnected dashboards, documents, prompts, and manual handoffs.

Growth is a continuous learning loop:

```text
Understand the product
→ Identify users and markets
→ Research channels and content
→ Form a strategy
→ Create and distribute
→ Observe real outcomes
→ Learn and improve the next action
```

Modern coding agents can read repositories, search the web, operate tools, edit files, reason across many kinds of context, and collaborate with people in a session. Growth Lab uses Codex and Claude Code as its application runtime and turns these capabilities into an end-to-end growth workflow.

## The model

```text
Session = Control Plane
Codex or Claude Code = Runtime
Skill = Growth Method
Client = External Action
Filesystem = Memory
```

Skills teach the Runtime how to understand a product, conduct research, choose tools, develop a strategy, create assets, examine feedback, and decide what to do next. Client tools provide access to browsers, official APIs, analytics exports, content platforms, and media generation. Files preserve product context, research, decisions, and outputs across conversations.

The AI session controls the entire workflow.

Every Model is an observation-action-review loop. Every Model owns persistent Memory containing time-based operational data, analysis, outcomes, and recommended next actions. The next run reads that Memory before making a new observation.

Loop methodology lives in the Model and evolves through direct edits to its Skill and references. Memory records what happened when the Model was used.

## What makes Growth Lab different

### Every channel, through its full lifecycle

Growth Lab is designed to cover every growth channel from understanding the opportunity and choosing an action to execution, measurement, and the next decision. It currently supports SEO page growth plus Xiaohongshu content collection, high-performing-content research, writing, image generation, card rendering, compliance checks, and post-result feedback.

### Continuous collaboration through natural language

Automation does not have to mean an unattended process running forever. People give the Agent goals in natural language, receive completed work and results, provide feedback, and ask it to continue. The conversation is the interface.

### Information, methods, and execution connected

Growth information usually lives in reports, methods live in specialists' experience, and execution lives across disconnected tools. Growth Lab brings them into one workspace so the Agent can collect evidence, apply a method, complete the action, and carry the result into the next round.

### Open source, user-owned data, accessible knowledge

Growth Lab is open source and stores product context, operational data, Memory, and outputs in the user's own workspace. It does not hold user data or create lock-in through private formats and closed workflows. Its purpose is to make effective growth knowledge inspectable, adaptable, and available to everyone.

## How to use it

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Open the directory in Codex or Claude Code, then ask what Growth Lab can do or describe the growth outcome you want.

Example prompts:

```text
What can you do?

Understand this product and run its first growth loop.

Collect high-performing Xiaohongshu content related to this product, choose a transferable structure, and create a complete post with images.

Review the latest results and execute the next growth action.
```

The Runtime reads the available Models, builds the missing product and market context, invokes the relevant Collectors and Executors, and writes its evidence, results, deliverables, and next actions back into the workspace.

### Connect your product

Tell the AI, in natural language, where your product repository or existing materials are located. The AI first reads the product facts it can verify. Users, problems, and value propositions that lack evidence remain open questions and are developed progressively through later growth loops.

### Configure through natural language

One unified [onboarding Skill](models/onboard-growth-lab/SKILL.md) audits dependencies across every Growth Lab capability. Users do not need to learn a separate command or open a setup page. Ask the Agent directly:

```text
Check which Growth Lab configuration is still missing.
Set up Xiaohongshu collection and image generation; skip SEO for now.
```

The Agent checks API keys, third-party clients, external repositories, browsers, and authentication, explains where missing configuration comes from, and lets the user configure or bypass each capability for the current session. Third-party clients and authentication remain outside the repository; secrets, cookies, and browser profiles do not enter Memory.

Methods and executable scripts stay with their owning Collector, Executor, or Model Skill. Private product materials, collected samples, generated outputs, and historical operating Memory are not distributed with the repository. A Model creates its own Memory namespace when the user runs it.

## System components

- Collectors for demand, competitors, content, and product growth data;
- Model Skills coordinating observation-action-review loops and persistent Memory;
- Executor Skills for creation, publishing, human collaboration, and review;
- Example workspaces showing complete growth journeys.

## Available capabilities

One capability is one complete observation-action-review loop, represented by one Model. The Model coordinates Collectors and Executors and preserves operational evidence, outcomes, and next actions in its own Memory.

| Name | Introduction | Observed result |
|---|---|---|
| [SEO Page Growth Loop](models/run-seo-page-loop/SKILL.md) | Identify the situations in which users may need your product, research what they actually search for in those situations, and create informative SEO pages that solve their problems and lead them to the product. | In our own run, new pages were indexed within 1–2 days. On a 7-day average basis, overall CTR decreased by 50%, while impressions and clicks each increased by 1000%. |
| [Xiaohongshu Replication and Review Loop](models/xhs-replicate/SKILL.md) | Coordinates collection, drafting, editing, screenshots, image generation, card rendering, compliance checks, and post-result review. | Commercial content created with this workflow has reached [4,000+ likes/saves and 700+ comments on a single post](http://xhslink.cn/o/37uik9K9WHr). Publishing remains manual. |

These figures describe one observed run and provide evidence for continued iteration. Results depend on the product, domain, search demand, page quality, site authority, and observation window.

## Status

Growth Lab includes a working SEO Page Growth Loop and a Xiaohongshu replication and review workflow. Reusable Skills, scripts, CLIs, and automated checks remain in their owning capability directories. Private product data, samples, screenshots, generated posts, and historical Memory are intentionally excluded. Xiaohongshu publishing remains manual.

If this direction resonates with you, open an issue and tell us what product you are growing, where the current workflow breaks, and which tools the Runtime should be able to use.

## License

To be decided before the first implementation release.

<a id="中文"></a>

---

<div align="center">

## 中文

<p>用自然语言运行产品运营和用户增长闭环：理解产品，发现真实需求，采取行动，再从结果中找到下一步。</p>

[English](#english)

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

Agent 会检查 API key、第三方 Client、外部仓库、浏览器与登录态，解释缺少的配置从哪里取得，再让你决定配置或本轮绕过。第三方 Client 与登录态仍保存在仓库外；密钥、cookie 和认证 profile 不进入 Memory。

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

将在首个实现版本发布前确定。
