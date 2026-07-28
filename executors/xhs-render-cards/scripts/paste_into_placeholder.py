#!/usr/bin/env python3
"""贴图工具 —— 把真实截图贴进 GPT Image 2 预留的纯色占位位,保证截图 100% 原像素。

为什么:截图卡若走 image2 `edit --image`,截图会经过生成式模型,有重画 / 改字 / 改数字的风险
(基准数字、DOI、产品 UI 文案零容忍)。改法:image2 `generate` 时只画标题 / caption / 裱框 +
一块**纯色占位块**(色键),截图全程不经 image2,由本工具检测占位 bbox 后贴进去 —— 物理上不可能被改。

配套 prompt 片段(写进该卡的 prompts/*.txt,让 image2 留位):
  THE CENTRAL HERO is a PLACEHOLDER: one single perfectly FLAT, SOLID, PURE GREEN rectangle,
  fill color exactly #00C800, COMPLETELY EMPTY — no text/icons/chart/lines/texture/gradient/inner border.
  A real screenshot will be pasted into it later. Make it a landscape rectangle about {W}:{H} ratio
  (= the screenshot's aspect, to avoid letterboxing), centered, the dominant central element,
  with a clean 1px light-gray border and a barely-visible soft shadow.

用法(repo 根;Growth Lab 不绑定项目 venv,用 uv 拉临时依赖):
  uv run --with pillow --with numpy python executors/xhs-render-cards/scripts/paste_into_placeholder.py \
    --card outputs/.../img/_gen-01-cover.png \
    --shot outputs/.../img/_src-bench-crop.png \
    --out  outputs/.../img/01-cover.png
flags:
  --color  占位色键十六进制(默认 00C800 纯绿)
  --fit    contain(默认,等比缩放+白边,不裁切)/ cover(填满+轻裁)
  --pad    contain 模式留白颜色(默认 white)
"""
import argparse
import sys

from PIL import Image
import numpy as np


def hex2rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def find_placeholder_bbox(card: Image.Image, color, tol_other=140, dom=40):
    """返回占位块 bbox (x0,y0,x1,y1)。色键 = 某通道明显占主导(默认纯绿)。"""
    arr = np.asarray(card.convert("RGB")).astype(int)
    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
    cr, cg, cb = color
    # 以「主导通道」判定,容忍 image2 渲染时的轻微色差 / 抗锯齿
    if cg >= cr and cg >= cb:            # 纯绿类
        mask = (G > 120) & (R < tol_other) & (B < tol_other) & (G - R > dom) & (G - B > dom)
    elif cr >= cg and cr >= cb:          # 纯红类
        mask = (R > 120) & (G < tol_other) & (B < tol_other) & (R - G > dom) & (R - B > dom)
    else:                                # 纯蓝类
        mask = (B > 120) & (R < tol_other) & (G < tol_other) & (B - R > dom) & (B - G > dom)
    cnt = int(mask.sum())
    total = arr.shape[0] * arr.shape[1]
    if cnt < total * 0.01:               # 占位块应占可观面积,过小=没找到
        return None, cnt
    ys, xs = np.where(mask)
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), cnt


def paste(card_path, shot_path, out_path, color, fit, pad):
    card = Image.open(card_path).convert("RGB")
    bbox, cnt = find_placeholder_bbox(card, color)
    if bbox is None:
        sys.exit(f"✗ 没检测到占位块(色键 {color},匹配像素 {cnt})。确认 image2 prompt 画了纯色占位块。")
    x0, y0, x1, y1 = bbox
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    shot = Image.open(shot_path).convert("RGB")
    sw, sh = shot.size
    if fit == "cover":
        scale = max(bw / sw, bh / sh)
        nw, nh = int(round(sw * scale)), int(round(sh * scale))
        shot_r = shot.resize((nw, nh), Image.LANCZOS)
        # 居中裁到占位框大小
        cx, cy = (nw - bw) // 2, (nh - bh) // 2
        shot_r = shot_r.crop((cx, cy, cx + bw, cy + bh))
        card.paste(shot_r, (x0, y0))
    else:  # contain:等比缩放,白边填充,不裁切(截图数字全保留)
        scale = min(bw / sw, bh / sh)
        nw, nh = int(round(sw * scale)), int(round(sh * scale))
        shot_r = shot.resize((nw, nh), Image.LANCZOS)
        card.paste(pad, (x0, y0, x1 + 1, y1 + 1))  # 先用 pad 色填占位区(盖掉绿)
        card.paste(shot_r, (x0 + (bw - nw) // 2, y0 + (bh - nh) // 2))
    card.save(out_path)
    print(f"✓ 占位 bbox {bbox} ({bw}x{bh}) ← 截图 {sw}x{sh} [{fit}] → {out_path}")


def main():
    ap = argparse.ArgumentParser(description="把真截图贴进 image2 预留的纯色占位位")
    ap.add_argument("--card", required=True, help="image2 生成的带占位卡图")
    ap.add_argument("--shot", required=True, help="真实截图(_src-*.png)")
    ap.add_argument("--out", required=True, help="输出成卡路径")
    ap.add_argument("--color", default="00C800", help="占位色键十六进制(默认纯绿 00C800)")
    ap.add_argument("--fit", choices=["contain", "cover"], default="contain")
    ap.add_argument("--pad", default="white", help="contain 留白色(默认 white)")
    args = ap.parse_args()
    paste(args.card, args.shot, args.out, hex2rgb(args.color), args.fit, args.pad)


if __name__ == "__main__":
    main()
