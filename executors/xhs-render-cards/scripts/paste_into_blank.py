#!/usr/bin/env python3
"""贴图工具(留白带路线)—— 把真截图贴进 image2 底板预留的纯色**留白带**,截图 100% 原像素。

与姊妹工具 paste_into_placeholder.py 的分工:
  - placeholder 路线:底板上画一块**纯色色键块**(#00C800),按颜色找 bbox 贴 —— generate 从零出钩子卡用。
  - blank 路线(本工具):底板下半留**干净纯背景空白带**(image2 edit 复刻爆款原图时,prompt 要求截图区留空),
    按「逐行低方差」找最长纯背景带贴 —— image2 edit 爆款原图做底板 + 贴图 的复刻路线用(见 xhs-render-cards.md
    §复刻爆款图文)。

它一并收了帖子里一次性脚本(composite.py / hires.py)的通用能力:
  - 留白带检测(逐行 std)
  - fit=fill(横向 1:1 全保留 + 纵向适度拉伸 ≤max-stretch,减少留白,不砍双栏半边)/ contain(等比不裁)
  - scale=2 supersample(底板放大 N 倍 + 原像素贴截图 → 破 image2 1024×1536 画布上限导致的小字糊)
  - logo(贴真 logo 图标 + 字标锁定块,盖掉 image2 渲的文字 logo)

用法(repo 根;Growth Lab 不绑定项目 venv,用 uv 拉临时依赖):
  uv run --with pillow python executors/xhs-render-cards/scripts/paste_into_blank.py \
    --board outputs/.../img-board/01-cover-board.png \
    --shot  "outputs/.../temp/首页展示:结果.png" \
    --out   outputs/.../img-final/01-cover.png \
    --scale 2 --fit fill --logo
flags:
  --scale       底板放大倍数(1=不放大;2=高清,原像素贴截图破画布上限)。默认 1
  --fit         fill(默认,横向全保留+纵向轻拉伸)/ contain(等比,不裁不拉)
  --max-stretch fill 模式纵向拉伸上限(默认 1.25,>1.3 会形变明显)
  --fill-frac   fill 模式截图占留白带高度的目标比例(默认 0.80)
  --top-frac/--bot-frac  留白带搜索范围(占整图高,默认 0.30 / 0.95)
  --margin/--pad         图区左右留白 / 上下内边距(@scale=1 像素,自动乘 scale)
  --logo / --no-logo     是否贴真 logo 锁定块(默认不贴)
  --logo-path   真 logo 路径(--logo 时必填)
  --wordmark    可选 logo 字标文字
  --font        字标字体(默认 macOS Arial Bold)
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

DEFAULT_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BG_FALLBACK = (247, 245, 243)
BORDER = (214, 207, 195)


def detect_band(base, top_frac, bot_frac, thr=6.0):
    """逐行 std,找最长低方差(纯背景)带 -> (y0, y1)。"""
    W, H = base.size
    g = base.convert("L")
    lo, hi = int(H * top_frac), int(H * bot_frac)
    best = cur_start = None
    cur = 0
    for i, y in enumerate(range(lo, hi)):
        s = ImageStat.Stat(g.crop((40, y, W - 40, y + 1))).stddev[0]
        if s < thr:
            if cur == 0:
                cur_start = i
            cur += 1
            if best is None or cur > best[1]:
                best = (cur_start, cur)
        else:
            cur = 0
    if best is None:
        raise SystemExit("error: 未检测到留白带(底板下半未留空?检查 image2 prompt 是否要求截图区留纯背景)")
    return lo + best[0], lo + best[0] + best[1]


def sample_bg(base):
    """从顶部 logo 右侧空白处采背景中位色(盖旧 logo 用),失败回退常量。"""
    W, H = base.size
    px = base.convert("RGB").load()
    xs = range(int(W * 0.45), int(W * 0.65), 6)
    ys = range(int(H * 0.035), int(H * 0.065), 4)
    cols = [px[x, y] for x in xs for y in ys]
    if not cols:
        return BG_FALLBACK
    cols.sort(key=lambda c: c[0] + c[1] + c[2])
    return cols[len(cols) // 2]


def stamp_logo(base, scale, logo_path, wordmark, font_path):
    """盖掉 image2 文字 logo,贴真图标 + 字标锁定块(尺度随 scale)。"""
    S = scale
    d = ImageDraw.Draw(base)
    bg = sample_bg(base)
    d.rectangle((round(24 * S), round(26 * S), round(392 * S), round(116 * S)), fill=bg)
    icon = Image.open(logo_path).convert("RGBA").resize((round(54 * S), round(54 * S)), Image.LANCZOS)
    ix, iy = round(40 * S), round(44 * S)
    base.paste(icon, (ix, iy), icon)
    try:
        font = ImageFont.truetype(font_path, round(42 * S))
    except OSError:
        font = ImageFont.load_default()
    tx = round((40 + 54 + 14) * S)
    bb = d.textbbox((0, 0), wordmark, font=font)
    cy = iy + round(27 * S)
    d.text((tx, cy - (bb[3] - bb[1]) / 2 - bb[1]), wordmark, font=font, fill=(20, 20, 20))


def main():
    ap = argparse.ArgumentParser(description="把真截图贴进 image2 底板的留白带(复刻路线)。")
    ap.add_argument("--board", required=True)
    ap.add_argument("--shot", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--fit", choices=["fill", "contain"], default="fill")
    ap.add_argument("--max-stretch", type=float, default=1.25)
    ap.add_argument("--fill-frac", type=float, default=0.80)
    ap.add_argument("--top-frac", type=float, default=0.30)
    ap.add_argument("--bot-frac", type=float, default=0.95)
    ap.add_argument("--margin", type=int, default=48)
    ap.add_argument("--pad", type=int, default=16)
    ap.add_argument("--logo", dest="logo", action="store_true")
    ap.add_argument("--no-logo", dest="logo", action="store_false")
    ap.set_defaults(logo=False)
    ap.add_argument("--logo-path")
    ap.add_argument("--wordmark", default="")
    ap.add_argument("--font", default=DEFAULT_FONT)
    a = ap.parse_args()
    if a.logo and not a.logo_path:
        ap.error("--logo requires --logo-path")

    S = a.scale
    board = Image.open(a.board).convert("RGB")
    if S != 1.0:
        board = board.resize((round(board.width * S), round(board.height * S)), Image.LANCZOS)
    W, H = board.size

    y0, y1 = detect_band(board, a.top_frac, a.bot_frac)
    margin, pad = round(a.margin * S), round(a.pad * S)
    tw = W - 2 * margin
    band_h = y1 - y0

    shot = Image.open(a.shot).convert("RGB")
    nat_h = round(shot.height * tw / shot.width)
    if a.fit == "contain":
        th = min(nat_h, band_h - 2 * pad)
        tw2 = round(shot.width * th / shot.height)
        shot_r = shot.resize((tw2, th), Image.LANCZOS)
    else:  # fill:横向全保留(=tw),纵向适度拉伸
        th = min(round(band_h * a.fill_frac), round(nat_h * a.max_stretch), band_h - 2 * pad)
        tw2 = tw
        shot_r = shot.resize((tw2, th), Image.LANCZOS)
    x = (W - tw2) // 2
    y = y0 + (band_h - th) // 2

    sh = max(1, round(6 * S))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [x - sh // 3, y - sh // 3 + sh * 2, x + tw2 + sh // 3, y + th + sh // 3 + sh * 2],
        radius=round(6 * S), fill=(60, 50, 40, 55))
    board = Image.alpha_composite(
        board.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(round(12 * S)))).convert("RGB")
    board.paste(shot_r, (x, y))
    bw = max(1, round(S))
    ImageDraw.Draw(board).rectangle([x - bw, y - bw, x + tw2 + bw - 1, y + th + bw - 1], outline=BORDER, width=bw)

    if a.logo:
        stamp_logo(board, S, a.logo_path, a.wordmark, a.font)

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    board.save(a.out)
    print(f"wrote {a.out} | 画布 {W}x{H} | 图区 {tw2}x{th} @ ({x},{y}) | scale={S} fit={a.fit} logo={a.logo}")


if __name__ == "__main__":
    main()
