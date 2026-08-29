# -*- coding: utf-8 -*-
"""把用户提供的贴纸图去掉纯色背景、裁到主体、输出透明底 PNG 到 assets/"""
import os
import numpy as np
from PIL import Image, ImageFilter
from collections import Counter

OUT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(OUT, "assets")
os.makedirs(ASSETS, exist_ok=True)

UP = "/root/.claude/uploads/42d4cf6b-ae7f-521b-95e1-0219f2719637"
JOBS = [
    ("puppy", f"{UP}/b1c48e29-image.jpg", 34, None),                  # 帕恰狗（浅蓝壁纸）
    ("kitty", f"{UP}/6808d15a-image.jpg", 40, (0.00, 0.00, 1.00, 0.93)),  # Hello Kitty（粉底）
    ("bunny", f"{UP}/c5d2e410-image.jpg", 60, None),                  # 米菲（深蓝底）
]


def flood_bg(arr, tol):
    """从四边出发，把与背景色相近且连通的像素标为背景"""
    h, w, _ = arr.shape
    border = np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]]).reshape(-1, 3)
    bg = np.array(Counter(map(tuple, border)).most_common(1)[0][0], dtype=np.int16)
    close = np.linalg.norm(arr.astype(np.int16) - bg, axis=2) <= tol

    seen = np.zeros((h, w), bool)
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if close[y, x]:
                stack.append((y, x)); seen[y, x] = True
    for y in range(h):
        for x in (0, w - 1):
            if close[y, x] and not seen[y, x]:
                stack.append((y, x)); seen[y, x] = True
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and close[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    return seen, bg


def largest_blob(mask):
    """保留最大连通主体，丢掉零散小装饰（星星、帽子等）"""
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    cur, best, best_n = 0, 0, 0
    for sy in range(h):
        for sx in range(w):
            if mask[sy, sx] and lab[sy, sx] == 0:
                cur += 1
                n = 0
                stack = [(sy, sx)]
                lab[sy, sx] = cur
                while stack:
                    y, x = stack.pop(); n += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            stack.append((ny, nx))
                if n > best_n:
                    best_n, best = n, cur
    return lab == best


for key, path, tol, box in JOBS:
    im = Image.open(path).convert("RGB")
    if box:
        w, h = im.size
        im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    if max(im.size) > 900:                      # 降采样，加快连通域计算
        im.thumbnail((900, 900), Image.LANCZOS)

    arr = np.array(im)
    bgmask, bg = flood_bg(arr, tol)
    fg = largest_blob(~bgmask)

    alpha = (fg * 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([arr, alpha]), "RGBA")
    # 边缘羽化一点点，去锯齿
    a = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.7))
    out.putalpha(a)
    out = out.crop(out.getbbox())

    side = 560
    k = side / max(out.size)                    # 主体等比缩放到统一尺寸（可放大）
    out = out.resize((max(1, round(out.width * k)), max(1, round(out.height * k))), Image.LANCZOS)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(out, ((side - out.width) // 2, (side - out.height) // 2), out)
    dst = os.path.join(ASSETS, f"mascot_{key}.png")
    canvas.save(dst)
    print(f"{key}: bg={tuple(bg)} -> {dst} {canvas.size} 主体占比 {fg.mean():.1%}")
