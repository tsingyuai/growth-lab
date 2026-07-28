# 参考图驱动生图

## 路线选择

| 需要 | 路线 | 工具 |
|---|---|---|
| 封面或内容卡 | 参考图驱动重新生图 | `executors/generate-image/generate-image.mjs --ref` |
| 设计卡中包含真实 UI/网页/代码/数据 | 视觉参考图与真实浏览器截图共同驱动重新生图 | `screenshot-assets` + `generate-image --ref ... --ref ...` |

所有卡片都必须传入用户确认过的来源笔记图片。禁止纯文生图，也禁止 HTML、SVG、CSS、Canvas、PPT、模板引擎或代码绘制卡片。

生图模型是精确中文、英文混排、复杂排版和网页视觉重绘的默认执行者。文字数量和排版复杂度不构成切换到代码绘图的理由。当前产品的界面必须先由真实浏览器抓取，再与视觉参考图一起投入模型；模型可以在 prompt 指挥下裁剪、放大、标注和融入版式。

## AI 生图

```bash
node executors/generate-image/generate-image.mjs \
  --model gpt-image-2 --prompt-file <prompt.txt> \
  --ref <confirmed-style-reference.png> \
  --ref <real-browser-screenshot.png> \
  --size 1024x1536 --quality high --out <card.png>
```

普通卡至少传入一个确认过的视觉参考图。截图卡至少传入两个 reference：视觉参考图与真实浏览器截图。prompt 必须按输入顺序声明每张图的用途，明确截图的裁剪范围、缩放、标注、在成图中的位置，以及必须保留的产品名称、目录结构、关键文字和界面关系。

## 截图卡路线

先通过真实浏览器工具抓取当前产品的 UI、官网、代码界面或仓库页面。把截图与对应视觉参考图同时传入：

```bash
node executors/generate-image/generate-image.mjs \
  --model gpt-image-2 --prompt-file <prompt.txt> \
  --ref <confirmed-style-reference.png> \
  --ref <real-browser-screenshot.png> \
  --size 1024x1536 --quality high --out <card.png>
```

需要局部截图时，在 prompt 中指定裁剪对象和保留范围；需要突出交互或能力时，直接要求模型加箭头、圈选、编号、局部放大或文字标注。不得创建纯色占位区，不得调用代码贴图或后期合成脚本。生成后必须全尺寸对照源截图检查关键事实。

## 标注卡

先取得真实截图，再在 prompt 中同时确定目标点、标签文字、标签位置和引线路径，由模型直接生成标注。完成后放大核验标注是否指向正确对象；整卡缩略图不足以证明标注对齐。

## 输出纪律

- 文件按 `01-cover.png`、`02-context.png` 顺序命名。
- 未明确使用 `--force` 并记录原因，不得覆盖已验收图片。
- 源截图、视觉参考图和最终生成图必须能够区分。
- 每张最终卡必须能追溯到全部 reference images、prompt 和生图命令。
- 每张卡的路线和输入写入 `PROCESS.md`。
