---
name: xhs-render-cards
description: "把小红书草稿变成可发布文案和图文卡片的完整执行 SOP：锁定证据与账号角色、强制执行 DAI 改写、审定 image plan、获取真实素材、AI 或本地渲染，并通过机械与视觉质量闸。准备、渲染、修改或核验小红书图文时使用。DAI 是本 Skill 内部的必要步骤，不得委托给独立 Skill。"
---

# 小红书卡片总 SOP

严格按顺序执行。文案与 `image-plan.md` 未审定前，不得开始生图。

## 0. 确定生产单元

必须具备：草稿、账号角色、目标读者、用户价值；复刻版式时的来源笔记或视觉参考；由当前 workspace 或用户提供的可验证产品事实；调用方 Model 的 Memory 输出目录；以及用户是否要求生图前确认。

按需创建 `draft.md`、`image-plan.md`、`PROCESS.md`、`prompts/`、本地渲染所需的 `cards.json` 和 `img/`。用 [process-doc.md](references/process-doc.md) 记录溯源。不得依赖仓库内置的私有样本或产品 Memory。

## 1. 锁定文案并强制执行 DAI

先确认钩子、用户价值、事实宣称和卡片顺序，再对标题、caption 和所有上图文字完整执行 [DAI SOP](references/deai.md)。官号和个人号都必须执行；角色只影响语气，不影响 DAI 是否执行。

改写后运行：

```bash
python3 executors/xhs-render-cards/scripts/check-banned-phrases.py <post-dir>
python3 executors/xhs-render-cards/scripts/check-compliance.py <post-dir>
```

退出码为 1 时立即停止。机械检查不能代替语义审阅。

## 2. 审定 image plan

写 prompt 或 `cards.json` 前，必须填完 [image-plan.md](references/image-plan.md)。每张卡都要写清用户得到什么、准确文案、来源与版式关系、真实素材、制作路线和验收标准。

没有真实作用或用户价值的卡直接删除。不得为了对齐参考图卡数而虚构内容。

## 3. 获取素材

真实产品 UI 走 [screenshot-assets](../screenshot-assets/SKILL.md)。每份源素材只在当前 loop 的 Memory 保存一次，再链接到帖子生产单元。禁止让生图模型伪造产品界面、数据、logo 或引用。

只有实际生图时才读取对应风格参考：

- 封面/钩子卡：[imagegen-style-cover.md](references/imagegen-style-cover.md)
- 内容卡：[imagegen-style-content.md](references/imagegen-style-content.md)

## 4. 渲染

读取 [rendering.md](references/rendering.md)，逐卡选择路线，只调用仓库内脚本。

- AI 默认入口：[generate-image](../generate-image/SKILL.md)。
- 截图卡：先生成留白或色键区域，再用 `paste_into_placeholder.py` 或 `paste_into_blank.py` 确定性贴图，确保截图像素不变。
- 需要确定性布局或大量精确文字：用 `cards.json` + `render.py`。

不得静默切换路线。任何会改变保真度或视觉风格的 fallback 都要先说明。

## 5. 核验与交付

按 [quality-gates.md](references/quality-gates.md) 检查。逐张以全尺寸查看成图，重跑文案与合规闸，并与 `draft.md`、`image-plan.md` 对照。

只有全部满足以下条件才能交付：文字准确且无多余文字；产品证据真实且未被重画；顺序、裁切、尺寸和移动端可读性正确；无缺失素材、残留占位、水印、假 UI 或无依据宣称；`PROCESS.md` 和来源路径完整。

最终报告输出路径、逐卡制作路线、核验结果、偏差和仍需人工确认的发布事项。本 Skill 不负责发布。
