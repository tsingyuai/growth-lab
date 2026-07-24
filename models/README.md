# Models / 数据模型

Models are observation-action-review loops implemented as Skills. They teach the Coding Agent how to turn raw growth intelligence into evidence, decisions, actions, reviews, and reusable Memory.

每个数据模型都是一个由 Skill 实现的“观察—行动—复盘”闭环，教 Coding Agent 如何把原始增长情报转化为证据、决策、行动、复盘和可复用 Memory。

## Scope / 范围

- Product and demand understanding / 产品与需求理解
- ICP and market discovery / ICP 与市场发现
- Competitive positioning / 竞品与定位分析
- Content pattern analysis / 内容模式分析
- Funnel and retention diagnosis / 漏斗与留存诊断
- Experiment review / 实验复盘
- Growth strategy and next-action selection / 增长策略与下一步行动选择

## How models work / 工作方式

A Model Skill describes the reasoning method, useful evidence, questions to investigate, and ways to turn findings into action. The Agent reads the available context, chooses an appropriate representation for the task, performs the analysis, and persists useful outputs as readable files.

Model Skill 描述推理方法、有价值的证据、需要调查的问题，以及如何把发现转化为行动。Agent 读取已有上下文，为当前任务选择合适的信息表示，完成分析，并把有复用价值的结果保存为可读文件。

Each Model owns a persistent namespace at `memory/<model-name>/`. The Agent reads that Memory before observing, acts on the current evidence, reviews the outcome, and writes the dated operational analysis, synthesis, and next-action recommendation back to Memory.

每个 Model 在 `memory/<model-name>/` 拥有独立的持久化记忆。Agent 在观察前读取 Memory，根据当前证据行动，随后复盘结果，并把带时间的运营数据分析、总结和下一步动作建议写回 Memory。

Model files contain the loop methodology. Memory contains the history produced by running that methodology. Improve the method by editing the Model directly.

Model 文件承载闭环方法论，Memory 承载方法运行后产生的历史记忆。需要改进方法时，直接修改 Model。

The model follows the question. Each task can use the structure that best fits its evidence and decision. When a visual view helps, the Agent generates a task-specific HTML page directly from the current analysis.

数据模型跟随问题变化。每个任务都可以采用最适合其证据和决策的信息结构。当可视化有助于理解时，Agent 直接根据当前分析生成专用 HTML 页面。

## Available models / 已有数据模型

- [`run-seo-page-loop`](run-seo-page-loop/SKILL.md)：从热词调研、页面创作和生图，到 IndexNow 与 Bing 数据复盘的 SEO 页面闭环。
