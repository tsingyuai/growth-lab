---
name: xhs-render-cards
description: "把小红书草稿变成可发布文案和图文卡片的完整执行 SOP：锁定证据与账号角色、强制执行 DAI 改写、审定 image plan、获取真实浏览器素材、把风格参考图与真实截图共同投入模型重新生图，并通过自动与视觉质量检查。准备、渲染、修改或核验小红书图文时使用。禁止用 HTML、SVG、占位符或贴图脚本生成卡片；DAI 是本 Skill 内部的必要步骤。"
---

# 小红书卡片总 SOP

严格按顺序执行。文案与 `image-plan.md` 未审定前，不得开始生图。

## 0. 确定生产单元

必须具备：草稿、账号角色、目标读者、用户价值；复刻版式时的来源笔记或视觉参考；由当前 workspace 或用户提供的可验证产品事实；调用方 Model 的 Memory 输出目录；以及用户是否要求生图前确认。

按需创建 `draft.md`、`image-plan.md`、`PROCESS.md`、`prompts/`、`screenshots/` 和 `img/`。用 [process-doc.md](references/process-doc.md) 记录溯源。不得依赖仓库内置的私有样本或产品 Memory。

## 1. 锁定文案并强制执行 DAI

先确认钩子、用户价值、事实宣称和卡片顺序，再对标题、caption 和所有上图文字完整执行 [DAI SOP](references/deai.md)。官号和个人号都必须执行；角色只影响语气，不影响 DAI 是否执行。

改写后运行：

```bash
python3 executors/xhs-render-cards/scripts/check-banned-phrases.py <post-dir>
python3 executors/xhs-render-cards/scripts/check-compliance.py <post-dir>
```

退出码为 1 时立即停止。机械检查不能代替语义审阅。

## 2. 审定 image plan

写 prompt 或抓取截图前，必须填完 [image-plan.md](references/image-plan.md)。每张卡都要写清用户得到什么、准确文案、对应参考图、真实素材、制作路线和验收标准。

没有真实作用或用户价值的卡直接删除。不得为了对齐参考图卡数而虚构内容。

## 3. 获取素材

当前产品的真实 UI、官网、代码界面和仓库页面都走 [screenshot-assets](../screenshot-assets/SKILL.md)，使用真实浏览器访问真实 URL 后抓取。每份源素材只在当前 loop 的 Memory 保存一次，再链接到帖子生产单元。生图模型可以按参考图重绘不承担事实证据的网页或界面视觉；不得把生成界面冒充当前产品的真实截图、代码、数据、logo 或引用。

只有实际生图时才读取对应风格参考：

- 封面/钩子卡：[imagegen-style-cover.md](references/imagegen-style-cover.md)
- 内容卡：[imagegen-style-content.md](references/imagegen-style-content.md)

## 4. 参考图驱动生图

读取 [rendering.md](references/rendering.md)，逐卡选择路线，只调用仓库内脚本。

- 每张卡必须使用用户确认的来源笔记图片作为视觉参考，通过 [generate-image](../generate-image/SKILL.md) 的 `--ref` 重新生图；没有参考图不得开始。
- 生图模型能够处理精确中文、英文混排和复杂网页视觉。不得因为文字多、含中英文、需要精确排版或需要像素级网页重绘而选择 SVG、HTML 或其他代码绘图路线。
- 截图卡：把确认过的视觉参考图与真实浏览器截图同时作为 `--ref` 输入，一次完成构图、裁剪、放大、标注和风格融合。prompt 必须逐一说明每张 reference 的角色以及截图中必须保留的事实内容。
- 禁止先生成留白、色键或占位符再用代码贴图，也禁止把截图预先合成进底板后再交给模型。
- 禁止使用 HTML、SVG、CSS、Canvas、PPT、模板引擎或代码绘制卡片，也禁止在失败后切换到这些路线。

不得静默切换路线。单次生成出现文字错误时，使用更明确的逐字文字约束做针对性重生；不能把“模型可能写错字”当作预先改用 SVG/HTML 的理由，也不能用确定性模板兜底。任何会改变保真度或视觉风格的 fallback 都要先说明。

## 5. 核验与交付

按 [quality-gates.md](references/quality-gates.md) 检查。逐张以全尺寸查看成图，重跑文案与合规检查，并与 `draft.md`、`image-plan.md` 对照。

只有全部满足以下条件才能交付：文字准确且无多余文字；截图中的产品名称、结构和关键事实与源图一致；顺序、裁切、标注、尺寸和移动端可读性正确；无缺失素材、水印、假 UI 或无依据宣称；`PROCESS.md` 和来源路径完整。

最终报告输出路径、逐卡制作路线、核验结果、偏差和仍需人工确认的发布事项。本 Skill 不负责发布。
