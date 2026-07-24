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

Growth Lab is designed to work with products at different stages. You can connect a product in one of three ways:

Growth Lab 面向不同阶段的产品，可以通过三种方式接入：

1. **Run it inside the product repository / 直接在产品仓库中运行**  
   Add Growth Lab's Skill, Clients, and templates to your existing workspace. This gives the Runtime the richest product context.
   将 Growth Lab 的 Skill、Clients 和模板加入现有产品 workspace，Runtime 可以直接读取最完整的产品上下文。

2. **Place the product beside Growth Lab / 将产品放在相邻目录**  
   Keep Growth Lab as its own repository and provide the Runtime with the local path to the product repository.
   保持 Growth Lab 为独立仓库，并在会话中向 Runtime 提供产品仓库的本地路径。

3. **Provide a product brief / 提供产品资料**  
   Represent the product in the workspace with its website URL, product brief, screenshots, customer notes, analytics exports, and previous campaigns.
   可以通过官网链接、产品介绍、截图、客户记录、数据导出和历史 Campaign，在 workspace 中呈现产品的完整背景。

A useful starting context includes / 推荐首先提供：

- What the product does / 产品解决什么问题；
- Who currently uses or buys it / 当前用户或购买者是谁；
- Product stage and business goals / 产品阶段与业务目标；
- Website and distribution channels / 官网与现有渠道；
- Available behavioral, acquisition, and revenue data / 可用的行为、获客与收入数据；
- Brand, legal, budget, and platform constraints / 品牌、法律、预算与平台限制。

The Runtime starts from the materials already available and uses the Skill to identify the information relevant to the current goal.

Runtime 从已有资料开始工作，并按照 Skill 判断哪些信息与当前目标相关。

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
- Let the Runtime own reasoning and workflow control / 由 Runtime 负责推理与流程控制；
- Optimize for learning and real product outcomes / 面向学习和真实产品结果。

## Status / 当前状态

Growth Lab is at the beginning. We are publishing the idea first, then turning it into a practical Skill and a small set of useful Clients through real product-growth work.

Growth Lab 目前刚刚开始。我们先公开这个想法，再通过真实的产品增长工作，把它逐步构建成可用的 Skill 和一组必要的 Client 工具。

If this direction resonates with you, open an issue and tell us what product you are growing, where your current workflow breaks, and which tools the Runtime should be able to use.

如果你认同这个方向，欢迎提交 Issue，告诉我们你正在增长什么产品、当前工作流断在哪里，以及你希望 Runtime 能够使用哪些工具。

## License

To be decided before the first implementation release. / 将在首个实现版本发布前确定。
