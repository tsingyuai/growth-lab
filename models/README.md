# Models / 数据模型

Models are observation-action-review loops implemented as Skills. They contain the methodology for coordinating Collectors, Executors, and persistent Memory over time.

每个数据模型都是一个由 Skill 实现的“观察—行动—复盘”闭环，只承载协调 Collector、Executor 和持久化 Memory 的方法论。

## What belongs in a Model / Model 承载什么

- The observation that starts or continues the loop / 启动或继续闭环所需的观察；
- The conditions for choosing and invoking a capability / 选择并调用某项能力的条件；
- The transition from evidence to one next action / 从证据到单个下一步行动的转换；
- The timing and scope of outcome review / 结果复盘的时间与范围；
- The relationship between the loop and its Memory / 闭环与其 Memory 的关系。

## How models work / 工作方式

A Model invokes Collectors to observe and Executors to create, publish, inspect, or review. Collection techniques belong to Collectors. Creation principles, execution techniques, and publishing methods belong to Executors.

Model 调用 Collector 完成观察，调用 Executor 完成创作、发布、检验和复盘。采集技巧属于 Collector；创作原则、执行技巧和发布方法属于 Executor。

Each Model owns a persistent namespace at `memory/<model-name>/`. The Agent reads that Memory before observing, acts on the current evidence, reviews the outcome, and writes the dated operational analysis, synthesis, and next-action recommendation back to Memory.

每个 Model 在 `memory/<model-name>/` 拥有独立的持久化记忆。Agent 在观察前读取 Memory，根据当前证据行动，随后复盘结果，并把带时间的运营数据分析、总结和下一步动作建议写回 Memory。

Model files contain the loop methodology. Memory contains the history produced by running that methodology. Improve the method by editing the Model directly.

Model 文件承载闭环方法论，Memory 承载方法运行后产生的历史记忆。需要改进方法时，直接修改 Model。

## Available models / 已有数据模型

- [`onboard-growth-lab`](onboard-growth-lab/SKILL.md)：通过自然语言统一审计 API key、第三方 Client、外部仓库、浏览器和登录态，并让用户逐项配置或本轮绕过。
- [`run-seo-page-loop`](run-seo-page-loop/SKILL.md)：从热词调研、页面创作和生图，到 IndexNow 与 Bing 数据复盘的 SEO 页面闭环。
- [`xhs-replicate`](xhs-replicate/SKILL.md)：执行“找 idea → 锚定爆款 → 复刻骨架 → 填入真实内容 → 生图与自动检查”的小红书主流程。
- `xhs-replicate` 内部包含结果回收与复盘阶段；发布日志不再对应独立 Model。
