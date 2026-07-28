# 渲染与贴图

## 路线选择

| 需要 | 路线 | 工具 |
|---|---|---|
| 封面或内容卡 | 参考图驱动重新生图 | `executors/generate-image/generate-image.mjs --ref` |
| 设计卡中包含真实 UI/网页/代码/数据 | 真实浏览器截图 + 参考图生图占位 + 像素级贴图 | `screenshot-assets` + `paste_into_placeholder.py` |
| 参考版式中已有干净留白带 | 留白带确定性贴图 | `paste_into_blank.py` |

所有卡片都必须传入用户确认过的来源笔记图片。禁止纯文生图，也禁止 HTML、SVG、CSS、Canvas、PPT、模板引擎或代码绘制卡片。

生图模型是精确中文、英文混排、复杂排版和网页视觉重绘的默认执行者。文字数量和排版复杂度不构成切换到代码绘图的理由。不承担产品事实证据的网页或界面可以直接按参考图重绘；当前产品的真实界面必须走浏览器截图与贴图路线。

## AI 生图

```bash
node executors/generate-image/generate-image.mjs \
  --model gpt-image-2 --prompt-file <prompt.txt> \
  --ref <confirmed-reference.png> \
  --size 1024x1536 --quality high --out <card.png>
```

至少传入一个 `--ref`。需要保持像素可信的产品截图不得经过生成式编辑。

## 截图占位路线

先通过真实浏览器工具抓取当前产品的 UI、官网、代码界面或仓库页面。再要求模型按参考图重新生成卡片，并画一块无纹理、无文字、无阴影、无物体的纯色 `#00C800` 矩形，最后贴入真实截图：

```bash
uv run --with pillow --with numpy python \
  executors/xhs-render-cards/scripts/paste_into_placeholder.py \
  --card <generated-card.png> --shot <real-screenshot.png> --out <final.png>
```

若底板使用干净背景留白带：

```bash
uv run --with pillow python \
  executors/xhs-render-cards/scripts/paste_into_blank.py \
  --board <board.png> --shot <real-screenshot.png> --out <final.png> \
  --scale 2 --fit fill
```

不能接受裁切或变形时改用 `contain`。合成后必须全尺寸检查 UI 小字。

## 标注卡

先取得真实截图，再以确定性方式添加标注。目标点、标签位置和引线路径必须一起确定。完成后裁出标注区域放大核验；整卡缩略图不足以证明标注对齐。

## 输出纪律

- 文件按 `01-cover.png`、`02-context.png` 顺序命名。
- 未明确使用 `--force` 并记录原因，不得覆盖已验收图片。
- 源截图、生成底板和最终合成图必须能够区分。
- 每张最终卡必须能追溯到对应的参考图片和生图命令。
- 每张卡的路线和输入写入 `PROCESS.md`。
