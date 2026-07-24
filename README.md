# Growth Lab

> AI-native growth workspace powered by Codex and Claude Code skills.  
> 由 Codex 与 Claude Code Skills 驱动的 AI 原生增长工作空间。

Growth Lab is an open-source, end-to-end growth tool that takes a product from code to market. Powered by Coding Agents, it understands the product, connects the tools and channels it needs, researches the market, creates growth assets, executes campaigns, and reviews real-world data to improve the next round of growth.

Growth Lab 是一个从代码到市场的开源端到端增长工具。它由 Coding Agent 驱动，理解产品、连接所需工具与渠道、研究市场、创作增长内容、执行增长行动，并基于真实数据完成复盘，持续改进下一轮增长。

> This repository is currently at the idea stage. The README describes the direction we intend to build in public.
>
> 项目目前处于构思阶段。本 README 描述的是我们准备公开构建的方向。

## Why Growth Lab / 为什么做 Growth Lab

Most AI growth tools solve only one fragment of the problem. Some generate copy, some research competitors, some schedule posts, and some display analytics. The product context is repeatedly lost between these tools, while the most important decisions still depend on disconnected dashboards, documents, prompts, and manual handoffs.

大多数 AI 增长工具只解决一个局部问题：有的生成文案，有的研究竞品，有的负责发布，有的展示数据。产品上下文在不同工具之间反复丢失，真正重要的决策仍散落在仪表盘、文档、Prompt 和人工交接中。

Growth is a continuous learning loop:

增长是一个持续学习的闭环：

```text
Understand the product / 理解产品
→ Identify users and markets / 判断用户与市场
→ Research channels and content / 研究渠道与内容
→ Form a strategy / 制定策略
→ Create and distribute / 生成与分发
→ Observe real outcomes / 收集真实结果
→ Learn and improve / 学习并调整下一轮行动
```

Modern coding agents can read repositories, search the web, operate tools, edit files, reason across many kinds of context, and collaborate with people in a session. Growth Lab uses Codex and Claude Code as its application runtime and turns these capabilities into an end-to-end growth workflow.

现代 Coding Agent 已经能够读取代码仓库、搜索网络、操作工具、编辑文件、跨上下文推理，并在会话中与人协作。Growth Lab 以 Codex 和 Claude Code 作为应用 Runtime，将这些能力组织成端到端的增长工作流。

## The model / 产品模型

```text
Session = Control Plane / 会话 = 控制面
Codex or Claude Code = Runtime
Skill = Growth Method / Skill = 增长方法与工作指引
Client = Action / Client = 外部执行能力
Filesystem = Memory / 文件系统 = 长期记忆
```

The Skill teaches the Runtime how to understand a product, conduct research, choose tools, develop a strategy, create assets, examine feedback, and decide what to do next. Client tools give the Runtime access to capabilities such as browsers, official APIs, analytics exports, content platforms, and media generation. Files preserve product context, research, decisions, and outputs across conversations.

Skill 教 Runtime 如何理解产品、开展研究、选择工具、形成策略、制作内容、分析反馈和决定下一步。Client 工具让 Runtime 能够使用浏览器、官方 API、数据导出、内容平台和素材生成等外部能力。文件则跨会话保存产品上下文、研究资料、决策与结果。

The AI session controls the entire workflow.

AI 会话负责控制整个工作流程。

Every Model is an observation-action-review loop. Every Model owns a persistent Memory that accumulates time-based operational data analysis, synthesis, outcomes, and recommended next actions. The next run reads that Memory before making a new observation.

每个 Model 都是一个“观察—行动—复盘”闭环。每个 Model 都拥有独立的持久化 Memory，用来积累按时间采集的运营数据分析、总结、行动结果和下一步动作建议。下一轮工作在开始观察前读取这些 Memory。

Loop coordination methodology lives in the Model and evolves through direct edits to its Skill and references. Memory records what happened when the Model was used.

闭环怎样观察、行动和复盘的方法论保存在 Model 中，并通过直接修改 Skill 与 references 持续演进。Memory 记录 Model 被实际使用后发生了什么。

## What it can become / 它可以带来什么

### Product-native understanding / 原生理解产品

Because Growth Lab runs in the product workspace, it can study the source code, README, documentation, landing pages, configuration, analytics definitions, and previous growth work together. Its recommendations are grounded in the actual product context and accumulated evidence.

Growth Lab 直接运行在产品 workspace 中，因此能够同时理解源码、README、产品文档、落地页、配置、数据定义和历史增长资料。它的建议建立在真实产品上下文和持续积累的证据之上。

### One continuous context / 连续的增长上下文

Research, strategy, content, experiments, and results live alongside the product. The Runtime reuses previous findings and connects new evidence to earlier decisions through one continuous context.

研究、策略、内容、实验和结果与产品共同存在于文件系统中。Runtime 在一个连续的上下文中复用历史发现，并把新证据连接到过去的决策。

### From advice to action / 从建议走向执行

With Client tools, the same session that produces a recommendation can also inspect a website, analyze exported metrics, prepare a campaign, generate assets, or call an authorized publishing API. This shortens the distance between thinking and doing.

通过 Client 工具，提出建议的同一个会话还可以检查网站、分析导出数据、准备 Campaign、生成素材，或调用已授权的发布 API，从而缩短从思考到行动的距离。

### Transparent and adaptable / 透明且可演进

Skills, templates, Clients, memory, and outputs are ordinary local files. Teams can read them, change the methodology, add a platform integration, or ask the Runtime to improve its own working instructions. The application can evolve while it is being used.

Skills、模板、Clients、Memory 和产物都是普通本地文件。团队可以阅读和修改方法、增加平台连接，也可以在使用过程中让 Runtime 改进自己的工作指引。应用能够一边运行，一边演进。

### Local-first and open / 本地优先与开放

The workspace remains under the user's control and can be versioned with Git. Growth Lab works with the tools and services a team already trusts while keeping product and growth data in the team's chosen environment.

Workspace 始终由用户控制，并可以使用 Git 管理。Growth Lab 复用团队已经信任的工具和服务，让产品与增长数据保留在团队选择的环境中。

## How to use it / 如何使用

The intended experience is deliberately small:

预期的使用方式非常简单：

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Open the directory in Codex or Claude Code, then start the Growth Lab Skill in a new session. Tell the Runtime which product you want to work on and what outcome you care about.

使用 Codex 或 Claude Code 打开该目录，在新会话中启动 Growth Lab Skill，然后告诉 Runtime 你要接入哪个产品，以及当前关注的增长目标。

Example prompts / 示例：

```text
Use Growth Lab to understand this product and propose the first growth research plan.
使用 Growth Lab 理解这个产品，并给出第一轮增长调研计划。

Analyze the existing product and growth materials, then identify our strongest ICP hypotheses.
分析现有产品和增长资料，找出最值得验证的 ICP 假设。

Review the latest campaign results and recommend what we should try next.
分析最近一次 Campaign 的结果，并建议下一步行动。
```

The Runtime will follow the Skill, read relevant files, ask for missing context when useful, call available tools, and write its research and deliverables back into the workspace.

Runtime 将按照 Skill 工作：读取相关文件，在需要时补充产品上下文，调用可用工具，并把研究与交付物写回 workspace。

## Connect your product / 如何接入你的产品

Growth Lab can start with a product at day zero: an idea, an early repository, a working prototype, or a live product. Having no customers, campaigns, analytics, or historical growth data is a valid starting point.

Growth Lab 可以从产品的第零天开始工作：一个想法、一个早期代码仓库、一个可用原型或一个已经上线的产品都可以。尚未拥有客户、Campaign、分析系统或历史增长数据，就是正常的起点。

Give the Agent access to the product in the form that already exists:

把产品以当前已有的形式交给 Agent：

1. **Open the product repository / 打开产品仓库**
   Run Growth Lab inside the product workspace so the Agent can understand the source code, documentation, routes, product experience, and existing instrumentation.
   在产品 workspace 中运行 Growth Lab，让 Agent 直接理解源码、文档、路由、产品体验和已有数据埋点。

2. **Point to a local product / 指向本地产品**
   Open Growth Lab as its own workspace and provide the path to a neighboring product repository.
   保持 Growth Lab 为独立 workspace，并向 Agent 提供相邻产品仓库的路径。

3. **Start from an idea or URL / 从想法或网址开始**
   Describe the product idea in the session or provide the current website. The Agent turns the available material into the first product understanding and growth hypotheses.
   在会话中描述产品想法，或提供当前网址。Agent 根据已有材料形成第一版产品理解和增长假设。

The Agent builds the missing growth context as part of the work:

Agent 会在工作过程中主动建立缺失的增长上下文：

```text
Read the product / 读取产品
→ Form user and scenario hypotheses / 形成用户与场景假设
→ Collect market and demand evidence / 主动采集市场与需求证据
→ Create or connect analytics pipelines / 建立或接入分析管线
→ Execute the selected growth action / 执行增长动作
→ Collect real outcomes / 采集真实结果
→ Update Memory and choose the next action / 更新 Memory 并选择下一步
```

For external evidence, the Agent searches public sources and uses available Collectors. For product data, it inspects existing analytics first, then can help add event instrumentation, connect an analytics provider, import exports, or create a lightweight collection path that matches the product's current stage. As users and traffic arrive, the same Model incorporates those signals into later decisions.

对于外部证据，Agent 会搜索公开来源并使用可用的 Collector。对于产品内部数据，Agent 先检查已有分析能力，再根据产品阶段帮助增加事件埋点、接入分析服务、导入数据，或建立轻量的数据采集路径。随着真实用户和流量出现，同一个 Model 会把这些信号纳入后续决策。

The user provides the product and the outcome they care about. The Agent discovers which additional information is useful, collects what it can, and asks for access or clarification only when the next action requires it.

用户只需要提供产品和当前关注的结果。Agent 负责判断还需要什么信息、主动采集可获得的数据，并只在下一步确实需要授权或补充判断时向用户提问。

## Planned building blocks / 计划中的组成部分

- Collectors for demand, competitors, content, and product growth data / 面向需求、竞品、内容与产品增长数据的采集器；
- Model Skills for coordinating observation-action-review loops and persistent Memory / 面向“观察—行动—复盘”编排与持久化 Memory 的 Model Skills；
- Executor Skills for concrete creation, publishing, human collaboration, and review methods / 承载具体创作、发布、人类协作与复盘方法的 Executor Skills；
- Example workspaces showing complete growth journeys / 展示完整增长过程的示例 workspace。

## Available capabilities / 现有能力

One capability is one complete observation-action-review loop, and every loop is represented by one Model. The Model coordinates Collectors and Executors, then preserves operational evidence, outcomes, and next actions in its own Memory.

一个能力就是一个完整的“观察—行动—复盘”闭环，每个闭环对应一个 Model。Model 协调所需的 Collector 和 Executor，并把运营证据、执行结果与下一步动作保存在自己的 Memory 中。

| Name / 名称 | Introduction / 介绍 | Observed result / 实测效果 |
|---|---|---|
| [SEO Page Growth Loop](models/run-seo-page-loop/SKILL.md) / SEO 页面增长闭环 | Identify the situations in which users may need your product, research what they actually search for in those situations, and create informative SEO pages that solve their problems and lead them to the product. / 思考用户在什么场景下可能会需要你的产品，调研这些场景中用户会实际搜索什么，生成具有信息量、能解决用户问题，并引流到产品的 SEO 页面。 | In our own run, new pages were indexed within 1–2 days. On a 7-day average basis, overall CTR decreased by 50%, while impressions and clicks each increased by 1000%. / 在我们自己的实测中，新页面执行后 1–2 天被收录；按 7 日平均口径，整体 CTR 降低 50%，页面曝光量和点击量均提高 1000%。 |

These figures describe one observed run and provide evidence for continued iteration. Results depend on the product, domain, search demand, page quality, site authority, and observation window.

这些数字记录了一次实际运行结果，并作为后续迭代的证据。具体效果会受到产品、域名、搜索需求、页面质量、站点权重和观察窗口影响。

## Status / 当前状态

Growth Lab is at the beginning. We are publishing the idea first, then turning it into a practical Skill and a small set of useful Clients through real product-growth work.

Growth Lab 目前刚刚开始。我们先公开这个想法，再通过真实的产品增长工作，把它逐步构建成可用的 Skill 和一组必要的 Client 工具。

If this direction resonates with you, open an issue and tell us what product you are growing, where your current workflow breaks, and which tools the Runtime should be able to use.

如果你认同这个方向，欢迎提交 Issue，告诉我们你正在增长什么产品、当前工作流断在哪里，以及你希望 Runtime 能够使用哪些工具。

## License

To be decided before the first implementation release. / 将在首个实现版本发布前确定。
