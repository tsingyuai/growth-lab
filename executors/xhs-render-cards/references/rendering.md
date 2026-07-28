# 渲染与贴图

## 路线选择

| 需要 | 路线 | 工具 |
|---|---|---|
| 编辑感封面或插画 | AI generate | `executors/generate-image/generate-image.mjs` |
| 不承担事实证据的风格变换 | AI edit | 同一 Client，增加 `--ref` |
| 设计卡中包含真实 UI/数据 | 生成占位后确定性贴图 | `paste_into_placeholder.py` |
| 参考版式中已有干净留白带 | 留白带确定性贴图 | `paste_into_blank.py` |
| 大量精确文字或可重复模板 | 本地 HTML 渲染 | `render.py` |

## AI 生图

```bash
node executors/generate-image/generate-image.mjs \
  --model gpt-image-2 --prompt-file <prompt.txt> \
  --size 1024x1536 --quality high --out <card.png>
```

非事实视觉参考可增加 `--ref <reference.png>`。需要保持像素可信的产品截图不得经过生成式编辑。

## 截图占位路线

要求模型画一块无纹理、无文字、无阴影、无物体的纯色 `#00C800` 矩形，再贴入真实截图：

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

## 本地渲染

把已审定的 image plan 翻译成 `cards.json`，只使用 `scripts/templates/card.html.j2` 和 `base.css` 已支持的布局：

```bash
uv run --with playwright --with jinja2 python \
  executors/xhs-render-cards/scripts/render.py \
  --input <post-dir>/cards.json --output <post-dir>/img
```

onboarding 负责提供 `uv`、Chrome 和浏览器配置。不得依赖其他仓库的渲染器或运行环境。

## 标注卡

先取得真实截图，再以确定性方式添加标注。目标点、标签位置和引线路径必须一起确定。完成后裁出标注区域放大核验；整卡缩略图不足以证明标注对齐。

## 输出纪律

- 文件按 `01-cover.png`、`02-context.png` 顺序命名。
- 未明确使用 `--force` 并记录原因，不得覆盖已验收图片。
- 源截图、生成底板和最终合成图必须能够区分。
- 每张卡的路线和输入写入 `PROCESS.md`。
