# Growth Lab

> AI-native growth workspace powered by Codex and Claude Code skills.  
> 由 Codex 与 Claude Code Skills 驱动的 AI 原生增长工作空间。

Growth Lab is an open-source experiment in building a complete product-growth loop directly inside an AI coding workspace—without a frontend, backend, database, or separate orchestration service.

Growth Lab 是一个开源实验：不建设前端、后端、数据库或独立编排服务，直接在 AI Coding Workspace 中建立完整的产品增长闭环。

> This repository is currently at the idea stage. The README describes the direction we intend to build in public.
>
> 项目目前处于构思阶段。本 README 描述的是我们准备公开构建的方向。

## Why Growth Lab / 为什么做 Growth Lab

Most AI growth tools solve only one fragment of the problem. Some generate copy, some research competitors, some schedule posts, and some display analytics. The product context is repeatedly lost between these tools, while the most important decisions still depend on disconnected dashboards, documents, prompts, and manual handoffs.

大多数 AI 增长工具只解决一个局部问题：有的生成文案，有的研究竞品，有的负责发布，有的展示数据。产品上下文在不同工具之间反复丢失，真正重要的决策仍散落在仪表盘、文档、Prompt 和人工交接中。

Growth is not a single content-generation task. It is a continuous learning loop:

增长不是一次内容生成任务，而是一个持续学习的闭环：

```text
Understand the product / 理解产品
→ Identify users and markets / 判断用户与市场
→ Research channels and content / 研究渠道与内容
→ Form a strategy / 制定策略
→ Create and distribute / 生成与分发
→ Observe real outcomes / 收集真实结果
→ Learn and improve / 学习并调整下一轮行动
```

Modern coding agents already know how to read repositories, search the web, operate tools, edit files, reason across many kinds of context, and collaborate with people in a session. Instead of rebuilding these capabilities behind another SaaS interface, Growth Lab treats Codex and Claude Code as the application runtime.

现代 Coding Agent 已经能够读取代码仓库、搜索网络、操作工具、编辑文件、跨上下文推理，并在会话中与人协作。Growth Lab 不再把这些能力重新包装进另一个 SaaS，而是直接把 Codex 和 Claude Code 当作应用 Runtime。

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

There is no additional workflow engine. The AI session itself controls the work.

项目不实现额外的工作流引擎，AI 会话本身就是整个工作的控制面。

## What it can become / 它可以带来什么

### Product-native understanding / 原生理解产品

Because Growth Lab runs in the product workspace, it can study the source code, README, documentation, landing pages, configuration, analytics definitions, and previous growth work together. Its recommendations can be grounded in the actual product instead of a short marketing prompt.

Growth Lab 直接运行在产品 workspace 中，因此能够同时理解源码、README、产品文档、落地页、配置、数据定义和历史增长资料。它的建议可以建立在真实产品之上，而不是依赖一段简短的营销 Prompt。

### One continuous context / 连续的增长上下文

Research, strategy, content, experiments, and results live alongside the product. The Runtime can reuse previous findings and connect new evidence to earlier decisions without rebuilding context in every tool.

研究、策略、内容、实验和结果与产品共同存在于文件系统中。Runtime 可以复用历史发现，把新证据连接到过去的决策，而不必在每个工具中重新建立上下文。

### From advice to action / 从建议走向执行

With Client tools, the same session that produces a recommendation can also inspect a website, analyze exported metrics, prepare a campaign, generate assets, or call an authorized publishing API. This shortens the distance between thinking and doing.

通过 Client 工具，提出建议的同一个会话还可以检查网站、分析导出数据、准备 Campaign、生成素材，或调用已授权的发布 API，从而缩短从思考到行动的距离。

### Transparent and adaptable / 透明且可演进

Skills, templates, Clients, memory, and outputs are ordinary local files. Teams can read them, change the methodology, add a platform integration, or ask the Runtime to improve its own working instructions. The application can evolve while it is being used.

Skills、模板、Clients、Memory 和产物都是普通本地文件。团队可以阅读和修改方法、增加平台连接，也可以在使用过程中让 Runtime 改进自己的工作指引。应用能够一边运行，一边演进。

### Local-first and open / 本地优先与开放

The workspace remains under the user's control and can be versioned with Git. Growth Lab can use the tools and services a team already trusts instead of forcing all product and growth data into a new hosted system.

Workspace 始终由用户控制，并可以使用 Git 管理。Growth Lab 可以复用团队已经信任的工具和服务，而不必把全部产品与增长数据迁移到一个新的托管系统。

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

Growth Lab is designed to work with products at different stages. You can connect a product in one of three ways:

Growth Lab 面向不同阶段的产品，可以通过三种方式接入：

1. **Run it inside the product repository / 直接在产品仓库中运行**  
   Add Growth Lab's Skill, Clients, and templates to your existing workspace. This gives the Runtime the richest product context.
   将 Growth Lab 的 Skill、Clients 和模板加入现有产品 workspace，Runtime 可以直接读取最完整的产品上下文。

2. **Place the product beside Growth Lab / 将产品放在相邻目录**  
   Keep Growth Lab as its own repository and provide the Runtime with the local path to the product repository.
   保持 Growth Lab 为独立仓库，并在会话中向 Runtime 提供产品仓库的本地路径。

3. **Provide a product brief / 提供产品资料**  
   For products without an accessible codebase, add the website URL, product brief, screenshots, customer notes, analytics exports, and previous campaigns to the workspace.
   如果无法提供源码，可以把官网链接、产品介绍、截图、客户记录、数据导出和历史 Campaign 放入 workspace。

A useful starting context includes / 推荐首先提供：

- What the product does / 产品解决什么问题；
- Who currently uses or buys it / 当前用户或购买者是谁；
- Product stage and business goals / 产品阶段与业务目标；
- Website and distribution channels / 官网与现有渠道；
- Available behavioral, acquisition, and revenue data / 可用的行为、获客与收入数据；
- Brand, legal, budget, and platform constraints / 品牌、法律、预算与平台限制。

You do not need to normalize everything before starting. The Runtime can inspect what already exists and use the Skill to decide what information is relevant.

开始前不需要先把所有资料标准化。Runtime 可以检查已有内容，并按照 Skill 判断哪些信息与当前任务相关。

## Planned building blocks / 计划中的组成部分

- A core growth-loop Skill / 核心增长闭环 Skill；
- Product-understanding and market-research methods / 产品理解与市场调研方法；
- Content research, strategy, and creation playbooks / 内容研究、策略与生产方法；
- Thin Client tools for useful external capabilities / 面向外部能力的轻量 Client 工具；
- Reusable research and output templates / 可复用的研究与输出模板；
- Example workspaces showing complete growth journeys / 展示完整增长过程的示例 workspace。

## Principles / 原则

- Ground recommendations in product evidence / 建议应建立在产品证据之上；
- Separate facts, hypotheses, and creative ideas / 区分事实、假设与创意；
- Prefer official and authorized data access / 优先使用官方或已授权的数据访问方式；
- Keep the method readable and changeable / 保持方法可读、可修改；
- Let the Runtime reason instead of rebuilding its control plane / 使用 Runtime 的推理能力，不重复建设控制面；
- Optimize for learning and real product outcomes, not vanity metrics / 面向学习和真实产品结果，而非虚荣指标。

## Status / 当前状态

Growth Lab is at the beginning. We are publishing the idea first, then turning it into a practical Skill and a small set of useful Clients through real product-growth work.

Growth Lab 目前刚刚开始。我们先公开这个想法，再通过真实的产品增长工作，把它逐步构建成可用的 Skill 和一组必要的 Client 工具。

If this direction resonates with you, open an issue and tell us what product you are growing, where your current workflow breaks, and which tools the Runtime should be able to use.

如果你认同这个方向，欢迎提交 Issue，告诉我们你正在增长什么产品、当前工作流断在哪里，以及你希望 Runtime 能够使用哪些工具。

## License

To be decided before the first implementation release. / 将在首个实现版本发布前确定。
