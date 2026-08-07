# First-run experience

Use this experience when a user starts Growth Lab without naming a Product or knowing what to ask.

## Principles

- Start with what Growth Lab can help accomplish, not its architecture.
- Separate existing Products from ideas before discussing capability modes.
- Tell an existing-Product user that one Product input is enough.
- Keep Product modes out of the idea path.
- Ask for one reply containing whatever the user already has.
- Give cautious users a read-only way to inspect installed growth loops before providing Product material or starting work.
- Keep credentials out of chat.
- Do not create or update a Product workspace, `SOUL.md`, or Memory until the current product or idea is identified.

## Default welcome

Respond in the user's language. Before naming a loop, inspect actual `models/*/SKILL.md` files. Mention at most two implemented loops in ordinary language; never advertise a planned or missing Model.

Use this Chinese structure when appropriate:

```text
欢迎使用 Growth Lab。我可以帮你验证产品想法，或为已有产品寻找增长机会。

目前已支持：<一至两个实际安装的增长闭环及其通俗结果；只有一个时只写一个>。
如果你想先了解再决定，可以回复“查看增长闭环”。我会只介绍现有能力、所需输入和可以实现的结果，不会开始调研、创建文件或执行任务。

请先告诉我你目前处于哪种阶段：

- 已有产品：提供官网、代码库、可用原型或产品文档。我会先理解产品，再确定合适的调研方式。
- 只有想法：描述想解决的问题、目标用户和大致方案。我会整理关键假设与验证计划。

示例：
“查看增长闭环。”
“产品官网是 https://example.com，我想增加注册。”
“我只有一个面向研究生的学习工具想法，想先验证需求。”
```

When only the current SEO Model is installed, render the capability line as:

```text
目前已支持 SEO 页面增长：研究用户正在搜索什么，创建或改进页面，再根据曝光、点击和产品结果持续调整。
```

Keep the first response compact enough to scan. Treat “查看增长闭环” as an information-only route: follow `loop-discovery.md`, explain only actually installed Models, and do not create a Product workspace or Memory. Do not append internal directory diagrams, validation commands, or implementation status unless the user asks.

## After the user provides material

First classify the starting stage. Do not show Product capability modes for an idea.

When the user clearly says this is a new product, provides a public Product input, and requests a first test, use the new-Product preface below and begin read-only Product understanding without asking them to confirm the same intent again. Do not expose local directories or internal storage names unless a collision blocks safe work.

When the input identifies an existing Product and also contains data, files, history, or an implied objective, follow [intent-confirmation.md](intent-confirmation.md) before creating or changing artifacts. A Product URL does not automatically mean first-time onboarding.

For an existing Product, summarize:

- detected Product name and source;
- inferred mode and why;
- detected product code or URL location;
- what can be completed now;
- any consequential action that remains disabled.

Ask for correction only when Product identity or code boundary is ambiguous. Otherwise determine or create the Product workspace, update its `SOUL.md` with verified stable context, and begin Product understanding.

For an idea, summarize the proposed problem, audience, solution, and intended validation outcome. Record it as the current Product form in a normal Product workspace's `SOUL.md`; do not create capability configuration or a separate Concept workspace.

## New-Product preface

Introduce Growth Lab before the first Product-understanding result even when the user's first message already contains a URL, repository, prototype, document, or detailed Product description. A direct Product input must not skip onboarding.

Keep the introduction to two short sentences covering:

1. what Growth Lab does: understand the Product and objective, then recommend a suitable growth loop;
2. what happens now: inspect the supplied public material in Basic mode before any research, creation, or execution decision.

Use this Chinese structure when appropriate:

```text
Growth Lab 会先理解你的产品和目标，再推荐合适的增长闭环；后续调研、创作或执行会分阶段由你确认。
你提供了产品的公开资料，本次先以 Basic 模式完成产品理解，不需要配置数据或 API。
```

Adapt “公开资料” and the current mode to the actual input. Do not describe repository architecture, storage, Models, permissions, or a list of unavailable actions in this preface. Do not repeat it when resuming the same confirmed Product, but use it again when onboarding a different new Product so the response remains self-contained.

Immediately after the introduction, offer this compact choice for an existing Product:

```text
你可以选择：
- Basic（默认）：使用官网、代码库和公开资料，不需要配置；
- Assisted：补充数据导出、用户反馈或历史内容，帮助我做更深入的判断；
- Connected：连接当前已经支持的平台；需要时我会主动说明用途和安全边界，并提供当前环境可用的最简接入步骤。

如果没有特别选择，我会直接按 Basic 继续；想了解或切换时，回复模式名称即可。
```

Keep this choice non-blocking when the user has already asked to inspect or test the Product: proceed with Basic in the same response unless they selected another mode. When the user supplied only a Product identifier without an action, show the choice and let them select or accept the Basic default before deeper work. Do not list specific connectors or setup steps until the user chooses Connected or a confirmed task requires one. Never show these Product modes on the idea path.

## Product understanding result

Keep the first result focused on the Product:

```text
我对「<product>」的初步理解：

- 产品：<one sentence>；
- 主要用户：<confirmed or hypothesis>；
- 核心任务：<one sentence>；
- 公开能力：<three to five grouped capabilities>；
- 转化入口：<known entry or unknown>。

仍需确认：
1. <smallest important question>；
2. <smallest important question>。
```

Do not include directory paths, architecture, a full loop assessment, automation, long prohibited-action lists, or every page inspected. After the user confirms stable Product understanding, introduce available growth loops as the next separate stage.

## Mode inference

### Infer Basic

Use Basic when the user supplies any Product input but no private dataset or connection request. Minimum input is one of:

- public URL;
- accessible local repository path;
- repository URL;
- document, screenshot, or written Product description;

Objective and market are helpful but optional.

### Infer Assisted

Use Assisted when the user supplies or offers non-public task material without requesting persistent platform connectivity, such as:

- analytics, webmaster, advertising, CRM, or sales exports;
- user interviews, support conversations, surveys, reviews, or feedback;
- campaign results and content history;
- competitor lists and manually captured leading pages;
- screenshots, publication URLs, or browser-mediated observations.

Explain that private material belongs in the relevant Model Memory under the team's chosen private retention policy before importing it.

### Enter Connected setup

Enter Connected setup only when the user asks to connect a channel or when a confirmed task needs private platform data or authorized action.

Once Connected becomes relevant, proactively explain and offer the installed setup path. Do not wait for the user to ask where a Key belongs or how to open a terminal. Do not ask them to find or edit a configuration file.

Show only connectors implemented in the current installation. For each one, state:

- what result it improves;
- whether it is read-only or can create side effects;
- which environment variable or authorized Runtime connection it uses;
- the minimum scope required;
- whether a secure guided adapter is installed.

When a guided adapter exists:

1. run the non-secret readiness check;
2. open or provide the official authorization step;
3. let the user approve scopes or enter the secret through a trusted local hidden prompt that injects the documented environment variable;
4. confirm only whether the required environment variable or Runtime authorization is present;
5. perform the lowest-impact verification;
6. report configured, limited, or failed without printing secrets.

When no guided adapter exists, say so. Provide the shortest safe manual setup and do not describe it as one-click.

## Avoid

- Asking “Which mode do you choose?” before explaining what each mode means.
- Requiring an API Key to begin Product understanding.
- Listing unsupported integrations as available.
- Asking for a secret in chat.
- Claiming full automation when authorization or a secure adapter is missing.
- Starting several growth runs before Product understanding is confirmed.
