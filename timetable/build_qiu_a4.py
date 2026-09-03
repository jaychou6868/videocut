# -*- coding: utf-8 -*-
"""邱老师课表 · A4 打印版（竖向）。

内容和黑白横版完全一致，只是重排成 A4 竖版：
- PNG：2480×3508，正好 300 DPI 的 A4，直接发去打印店也行
- PDF：按真实 A4 尺寸输出，打印时不会被缩放
"""
import os, asyncio

from build_qiu_plain import BANDS, TAIL, CN, TIME, DAYS, lesson

OUT = os.path.dirname(os.path.abspath(__file__))
PNG = "邱老师课表_A4打印版.png"
PDF = "邱老师课表_A4打印版.pdf"

W, H = 1240, 1754          # 150 DPI 的 A4；截图时再乘 2 => 300 DPI


def build_table():
    out = ['<div class="c hd"></div>']
    out += [f'<div class="c hd">{d}</div>' for d in DAYS]
    out.append(f'<div class="c band">{BANDS[0]}</div>')

    for p in range(1, 10):
        out.append(f'<div class="c num">{CN[p]}</div>')
        for d in range(1, 6):
            k = lesson(d, p)
            out.append(f'<div class="c">邱 {k}<br><span class="t">{TIME[p]}</span></div>'
                       if k else '<div class="c"></div>')
        if p in BANDS:
            out.append(f'<div class="c band">{BANDS[p]}</div>')

    out.append(f'<div class="c band">{TAIL}</div>')
    out.append('<div class="c band note">备注：</div>')
    return "".join(out)


PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>
@page{size:A4 portrait;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)spx;height:%(H)spx}
body{background:#fff;color:#000;
     font-family:'Noto Serif SC','Songti SC',serif;-webkit-font-smoothing:antialiased;
     -webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:%(W)spx;height:%(H)spx;padding:64px 58px;display:flex;flex-direction:column}
.grid{display:grid;grid-template-columns:76px repeat(5,1fr);grid-auto-rows:min-content;
      border-left:2px solid #000;border-top:2px solid #000}
.c{border-right:2px solid #000;border-bottom:2px solid #000;
   display:flex;flex-direction:column;align-items:center;justify-content:center;
   text-align:center;font-size:23px;line-height:1.45;padding:5px 3px;min-height:104px}
.hd{min-height:56px;font-size:25px}
.num{font-size:27px}
.t{font-size:20px}
.band{grid-column:1 / -1;min-height:54px;font-size:21px}
.note{align-items:flex-start;justify-content:flex-start;
      min-height:150px;padding:12px 0 0 16px}
</style></head><body><div class="page">
  <div class="grid">%(table)s</div>
</div></body></html>"""


def main():
    path = os.path.join(OUT, "tt_qiu_a4.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PAGE % dict(W=W, H=H, table=build_table()))

    from playwright.async_api import async_playwright

    async def shoot():
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
            pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
            await pg.goto("file://" + path)
            await pg.wait_for_timeout(600)
            over = await pg.evaluate(
                "() => document.querySelector('.grid').getBoundingClientRect().bottom"
                " - (%d - 64)" % H)
            await pg.screenshot(path=os.path.join(OUT, PNG))
            await pg.pdf(path=os.path.join(OUT, PDF), format="A4",
                         print_background=True,
                         margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            for f_ in (PNG, PDF):
                print(f"{f_} {os.path.getsize(os.path.join(OUT, f_))//1024}KB")
            print(f"表格底边距页面下边距还差: {-round(over)}px（负数=溢出）")
            await b.close()

    asyncio.run(shoot())


if __name__ == "__main__":
    main()
