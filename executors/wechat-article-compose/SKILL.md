---
name: wechat-article-compose
description: 把一个已确认的选题写成微信公众号长文。锁定复刻锚与用户价值、写出 article.md / wechat.yml / _review.md，并通过公众号通用合规检查和人工预览前自检。准备、改写或核验公众号文章时使用；不负责发布，也不产出小红书卡片。
---

# 公众号长文创作 SOP

公众号读者愿意读完长文，前提是标题让他点开、首屏说中他的卡点、每一节都给他一个可带走的结果。本 SOP 的重心在“完整解释 + 真实产品能力 + 可转发价值”。

严格按顺序执行。`source-review.md` 未经用户确认前，不写正文。

## 0. 确定生产单元

必须具备：选题、目标读者、文章类型（教程 / 案例 / 观点 / 更新）、账号角色（官号 / 个人号）、调用方 Model 的 Memory 输出目录，以及来自 `SOUL.md`、产品代码、页面或用户明确提供资料的可验证产品事实。

生产单元目录由调用方决定，默认 `memory/<model-name>/outputs/<YYYYMMDD-slug>/`：

| 文件 | 作用 |
|---|---|
| `source-review.md` | 阶段一 brief：写什么、参考哪 1-2 篇、为什么读者需要、证据与能力边界 |
| `article.md` | 正文源文件，模板见 [templates/article.md](references/templates/article.md) |
| `wechat.yml` | 标题、摘要、作者、封面、评论、发布审批，模板见 [templates/wechat.yml](references/templates/wechat.yml) |
| `_review.md` | 复刻锚、价值三问、标题候选、合规与发布自检，模板见 [templates/_review.md](references/templates/_review.md) |
| `cover.png` / `assets/` | 封面与正文图片；正文图片只用本地相对路径 |

## 1. 阶段一 brief

先读：

1. [article-structure.md](references/article-structure.md)
2. [replicate-value-guide.md](references/replicate-value-guide.md)
3. [title-patterns.md](references/title-patterns.md)
4. [editorial-voice.md](references/editorial-voice.md)
5. [compliance.md](references/compliance.md)

然后写 `source-review.md`：文章类型；1-2 篇复刻锚（已发布公众号长文、本产品已验证的小红书爆款或真实产品工作流）及复刻了什么；读者问题与可量化证据；产品能力边界（哪些已上线可验证、哪些只能作为探索写出边界）。交给用户确认后再进入下一步。

## 2. 大纲与标题

按“读者问题 → 先给结论 → 方法/案例 → 产品能力 → 截图证据 → 下一步”编排大纲，每个小标题都能单独被扫读。

写 5 个标题候选，每个标注钩子类型：痛点 / 反差 / 结果 / 数字 / 物证。

## 3. 写正文

- 逐节回答用户价值三问，把“产品有某功能”改写成“读者因此能做到什么”。
- 产品能力只写已上线、可验证的内容；来源不明确就停下询问，禁止补写。
- 对标题、摘要和正文执行 [xhs-render-cards 的 DAI SOP](../xhs-render-cards/references/deai.md) 的第一、二遍（恢复真实说话者、删除模型腔），语气按 [editorial-voice.md](references/editorial-voice.md) 校准；不套小红书口吻。
- 卡片、表格、步骤、数据对比等结构化内容直接用排版块写进正文，不截取网页卡片当配图（公众号不渲染 Markdown 表格）：

  ```text
  ::: card [accent|soft|dark]   #### 眉题 / ### 标题 / 段落 / --- 分隔 / - 列表项 [| 标签]
  ::: steps                     - 标题 | 说明 | 补充
  ::: stats                     - 数值 | 说明
  ::: bars 系列A | 系列B          - 指标 | A 百分比 | B 百分比
  :::
  ```

- 配图只承担排版做不到的事：第一印象、真实产品与成果物证、转化入口。先写 `image-plan.md`（位置、要传达什么、构图、素材来源、制作路线），正文用 `::: figure` 配图位占位（首行图题，其余为说明），图片生成后再替换；仍含配图位时发布 Executor 拒绝创建草稿。
- 产品界面图必须来自 [screenshot-assets](../screenshot-assets/SKILL.md) 的真实截图；概念图、封面可以走 [generate-image](../generate-image/SKILL.md)。不得让 AI 伪造产品 UI。
- 封面建议 2.35:1（如 900×383）；正文图片放在生产单元的 `assets/` 下并以相对路径引用。
- 标题只写在 `wechat.yml`，正文不写 H1；`article.md` 中不留 `>` 说明行或 `{…}` 占位符，渲染器会把它们原样输出到正文。
- 小标题用 `## 01 标题` 形式，两位编号显示为主题强调色。
- 品牌色通过 `wechat.yml` 的 `theme` 设置，只作点缀色（编号、线条、标记、强调字），底色保持白色。
- 需要可点击入口时使用 `[![入口文字](assets/cta.png)](https://...)`，alt 会显示为图片下方的链接文字。

## 4. 配置与自检

1. 生成 `wechat.yml`，按品牌设置 `theme`（通常以 `base: white-accent` 加品牌色 `accent` / `link` 覆盖），默认 `publish.mode: draft_only`、`publish.approved: false`。`author`、`content_source_url` 留空时由发布 Executor 用环境变量默认值补齐。
2. 运行机械检查，退出码为 1 时立即停止：

   ```bash
   python3 executors/wechat-article-compose/scripts/check-wechat-compliance.py <post-dir>
   python3 executors/xhs-render-cards/scripts/check-banned-phrases.py <post-dir>/article.md
   ```

3. 语义审阅：机械检查只拦字面。逐条核对 [compliance.md](references/compliance.md) 与 `SOUL.md` 中的品牌、法律和平台约束。
4. 填写 `_review.md`，记录复刻锚、价值三问、标题候选、合规结论与未决项。

## 交付

报告生产单元路径、最终标题与摘要、复刻锚、自检结果、偏差和仍需人工确认的事项。渲染预览与草稿同步交给 [wechat-mp-publish](../wechat-mp-publish/SKILL.md)。

## 不做

- 不调用 `xhs-render-cards` 出卡片，不套小红书口吻；只借标题钩子、痛点和价值表达。
- 不发布，不创建草稿。
- 不把密钥、AppSecret 或授权配置写进文章目录。
