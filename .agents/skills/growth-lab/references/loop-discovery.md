# Loop discovery

Assess only Models implemented under `models/*/SKILL.md`.

## Explain the concept

For a new user, explain once:

```text
增长闭环是：了解现状 → 选择一个行动 → 执行 → 查看真实结果 → 决定下一步。
它不是一次性建议，而是根据结果持续调整的工作方式。
```

Use business language in the rest of the response. Do not require the user to understand Model, Collector, Executor, or Memory.

## Inputs

Read the current Product workspace's `SOUL.md`, the product carrier, available channels and analytics, that workspace's existing Model Memory, and the user's current outcome.

## Status

Assign each implemented Model one status:

- `Ready`: relevant to the product and current outcome; required starting evidence and execution surface are available.
- `Conditional`: relevant, but an important data source, authorization, implementation surface, or review path is missing. State what can still be completed now.
- `Not now`: implemented but not currently supported by the product stage, objective, or constraints.

Do not list planned Models as available. When the requested outcome has no implemented Model, state the missing capability separately.

## Output

For every implemented Model, state:

- result it can produce;
- status and evidence;
- required missing input when conditional;
- safest first run;
- whether automation should be considered now.

Keep each loop explanation to one or two sentences: what business result it targets, what it does from observation to review, and the main input it needs.

Recommend one Model. Do not create empty Memory or automation during assessment.

## Preserve user control

After the capability list, recommend at most one loop and state:

- why it fits the confirmed Product and goal;
- what the first stage will do;
- what the first stage will not do;
- what evidence will trigger the next decision;
- that the user will confirm before implementation, publication, or automation.

End by asking whether to begin only the stated first stage. Do not say a loop has been selected or started before the user agrees.

Example:

```text
SEO 页面增长 — 条件适用
研究用户正在搜索什么，选择一个页面机会，创建或改进页面，再根据曝光、点击和产品转化决定下一步。

推荐原因：产品有公开网站和可索引任务页面。
第一阶段：只做公开需求与页面机会调研。
本阶段不会：修改或发布网站。
下一次决定：发现有证据支持的机会后，再由用户确认是否实施。
```
