# Memory / 持久化记忆

Every Model owns one Memory namespace:

每个 Model 拥有一个对应的 Memory 命名空间：

```text
models/<model-name>/       # 方法论：如何观察、行动和复盘
memory/<model-name>/       # 记忆：历次真实运营观察、结论和下一步动作
```

## What Memory contains / Memory 保存什么

- Operational data collected at a known time or over a known period / 在明确时间点或时间窗口采集的运营数据；
- Analysis of that data and changes from previous observations / 对数据及其相对历史变化的分析；
- A concise synthesis of what the Model learned / Model 本轮得到的总结性认识；
- Recommended next actions and the evidence supporting them / 下一步动作建议及其证据；
- Later outcomes that confirm, refine, or overturn an earlier conclusion / 后续结果对历史结论的验证、修正或推翻。

Memory uses ordinary files and follows the needs of each observation. The Agent may use Markdown, JSON, CSV, screenshots, exported source data, or a standalone HTML review. Name files with a sortable date or timestamp and a clear subject, for example:

Memory 使用普通文件，并根据每次观察的实际需要选择形式。Agent 可以使用 Markdown、JSON、CSV、截图、导出的原始数据或独立 HTML 复盘。文件名使用可排序的日期或时间戳和清晰主题，例如：

```text
memory/run-seo-page-loop/
├── 2026-07-24-keyword-baseline.json
├── 2026-07-24-page-launch.md
└── 2026-08-07-bing-performance-review.html
```

需要小红书工作流时，由对应 Model 在运行时创建命名空间：

```text
memory/xhs-replicate/                 # 运行时生成；不随仓库分发私有基线内容
memory/xhs-replicate/publish-log/     # 该 loop 运行时产生的 24h / 48h / 7d 数据
```

仓库不内置任何私有 `knowledge`、`products`、`samples`、`outputs` 或 `assets`。这些内容只能由使用者在自己的运行中产生。密钥、第三方 client 和浏览器登录 profile 也不属于 Memory。

The content should make its collection time, analysis window, source, observed change, conclusion, and recommended next action understandable. These are semantic requirements, not a fixed schema.

文件内容应让采集时间、分析窗口、来源、变化、结论和下一步动作清楚可读。这些是语义要求，不是固定 schema。

## Where methodology changes belong / 方法改进写到哪里

Instructions for how the loop observes, chooses an action, invokes capabilities, reviews outcomes, and reads or writes Memory belong in `models/<model-name>/`.

闭环如何观察、选择行动、调用能力、复盘结果和读写 Memory，直接写入 `models/<model-name>/`。

Collection methods belong in the relevant Collector. Creation, execution, publishing, and task-specific review methods belong in the relevant Executor. Update the owning Skill directly when a run reveals a better method.

采集方法写入对应 Collector，创作、执行、发布和具体复盘方法写入对应 Executor。一次运行发现更好的方法时，直接修改负责该方法的 Skill。Memory 始终聚焦真实运营证据、分析结论、复盘和下一步动作。

## Privacy / 隐私

Real operational Memory is ignored by Git in this public repository. Teams may choose their own private versioning and retention policy in the product workspace. Keep credentials and unnecessary personal data out of Memory.

本公开仓库默认通过 `.gitignore` 排除真实运营 Memory。团队可以在产品 workspace 中采用自己的私有版本管理和保留策略。Memory 不保存凭据和无关个人数据。
