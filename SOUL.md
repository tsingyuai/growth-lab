# Product Soul

> 本文件保存 Coding Agent 对当前产品的持续认识。它不是首次接入时一次性生成的完整画像。每次 loop 只把新获得、可追溯、能跨任务复用的认知增量写入；代码通常只能先确认产品形态和可见能力，用户、问题与价值需要在后续执行中逐步验证。没有证据的字段保持待理解、假设或未知。

## Product / 产品

- Name / 名称：Growth Lab
- One-line description / 一句话介绍：用自然语言运行产品运营与用户增长闭环，并把产品认知、采集证据、行动结果和下一步行动保存在工作区文件中。
- Product form / 产品形态：开源代码仓库与本地优先的 Coding Agent Runtime 工作流。
- Stage / 阶段：持续开发与能力扩展；具体增长闭环的使用阶段取决于接入的产品。

## Users and situations / 用户与场景

- Current users / 当前用户：使用 Codex 或 Claude Code、希望以自然语言执行增长工作的产品团队与独立开发者；来自 README 中的使用说明，尚未有用户访谈证据。
- Candidate users / 候选用户：缺少专门增长团队但已有产品代码、官网或原型的 0→1 与小团队。
- Situations of need / 需求场景：需要从产品理解、需求研究、内容采集、创作、发布到结果复盘的连续上下文，而不想拼接多个孤立工具。
- Core job to be done / 核心任务：让 Agent 在当前工作区观察真实证据、选择一个可度量行动、完成执行，并把结果留给下一轮继续。

## Value / 产品价值

- Problem solved / 解决的问题：减少增长方法、外部工具、产品上下文和运营结果分散导致的重复交接与上下文丢失。
- Core value proposition / 核心价值主张：以普通文件承载 Skill、Client、Memory 与产物，让增长过程可检查、可修改、可跨会话继续。
- Differentiation / 差异化：Model 组织完整“观察—行动—复盘”闭环；Collector 和 Executor 是可替换的执行能力，而不是被单独包装的产品能力。
- Desired business outcome / 当前业务目标：扩展可靠、合规、可验证的增长渠道能力，同时保持本地数据和用户控制权。

## Product reality / 产品现状

- Available capabilities / 已有能力：`onboard-growth-lab`、`run-seo-page-loop`、`xhs-replicate`、`run-wechat-article-loop` 四个 Model；SEO、小红书、微信公众号、媒体平台研究等 Collector/Executor。
- Website and channels / 官网与渠道：官网为 <https://growthlab.tsingyuai.com>；源代码通过 GitHub `tsingyuai/growth-lab` 分发。
- Analytics and data / 分析与数据：项目自身没有已识别的一体化分析埋点；真实运营 Memory 默认由 Git 忽略。
- Constraints / 品牌、法律、预算与平台约束：使用官方 API、授权访问和公开来源；密钥与登录态不得进入仓库或 Memory；外部 Client 留在仓库外；需要遵守平台条款、隐私和版权。

## Evidence and hypotheses / 证据与假设

- Verified facts / 已验证事实：
  - 产品使用“会话 = 控制面、Coding Agent = Runtime、普通文件 = 方法与记忆”的结构，见 `README.md`、`AGENTS.md`。
  - 当前 Model 清单以 `models/` 实际 `SKILL.md` 为准。
  - 知乎内容采集已切换为知乎官方 `zhihu-cli` 与 Open Platform API；MediaCrawler 不再覆盖知乎。
  - 统一 onboarding 已覆盖知乎官方 CLI 的检查、安装、无回显认证、在线验证和非空内容读取验收。
- Active hypotheses / 当前假设：
  - 用户更愿意用自然语言驱动完整闭环，而不是操作一组独立脚本。
  - 本地文件记忆能降低跨工具上下文丢失，但需要经过真实增长任务验证留存与复用效果。
- Open questions / 待回答问题：
  - 哪类产品与增长阶段从 Growth Lab 获得的价值最明确？
  - 用户在哪些闭环中最容易在“观察”与“行动”之间中断？
  - 官方渠道能力接入后，实际使用频率和结果质量如何？
- Last updated / 最近更新：2026-11-13 America/Los_Angeles
