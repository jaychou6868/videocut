# -*- coding: utf-8 -*-
"""邱老师课表 · 黑白表格版（电脑横版）。

照纸质课表 1:1 复刻：同样的行序、同样的合并行、同样的措辞，
只是把带 ★ 的（玥y 自己的课）拿掉，只留邱老师的 126 / 127 / 130。
"""
import os, asyncio

from build import QIU

OUT = os.path.dirname(os.path.abspath(__file__))
FILE = "邱老师课表_黑白版.png"

DAYS = ["周一", "周二", "周三", "周四", "周五"]
CN = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
      6: "六", 7: "七", 8: "八", 9: "九"}
TIME = {1: "7:40—8:20", 2: "8:30—9:10", 3: "9:35—10:15", 4: "10:30—11:10",
        5: "11:20—12:00", 6: "13:35—14:15", 7: "14:25—15:05",
        8: "15:15—15:55", 9: "16:10—16:50"}

# 横贯整行的作息条，措辞和纸质表一致；键 = 排在第几节之后（0 = 表头之后）
BANDS = {
    0: "早读 6:30—7:00　　早自修 7:00—7:25　　课间活动",
    2: "课间操 9:10—9:35",
    3: "眼操 10:25—10:30",
    5: "中餐 12:00—12:35　　午休 12:35—13:15　　唱红歌 13:25—13:35",
    9: "晚餐 16:50—17:40　　课前活动 17:40—18:00　　听力 18:00—18:30",
}
TAIL = "晚一 18:30—19:20　　晚二 19:30—20:20　　晚三 20:30—21:30"


def lesson(d, p):
    for (dd, pp, k) in QIU:
        if dd == d and pp == p:
            return k
    return None


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
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{background:#fff;color:#000;
     font-family:'Noto Serif SC','Songti SC',serif;-webkit-font-smoothing:antialiased}
.page{width:1920px;height:1080px;padding:22px 150px;display:flex;flex-direction:column}
.grid{flex:1;display:grid;grid-template-columns:96px repeat(5,1fr);
      grid-auto-rows:min-content;border-left:2px solid #000;border-top:2px solid #000}
.c{border-right:2px solid #000;border-bottom:2px solid #000;
   display:flex;flex-direction:column;align-items:center;justify-content:center;
   text-align:center;font-size:24px;line-height:1.4;padding:4px 4px;min-height:70px}
.hd{min-height:46px;font-size:26px}
.num{font-size:28px}
.t{font-size:22px}
.band{grid-column:1 / -1;min-height:42px;font-size:23px;letter-spacing:.5px}
.note{align-items:flex-start;padding-left:16px;min-height:72px;justify-content:flex-start;
      padding-top:8px}
</style></head><body><div class="page">
  <div class="grid">%(table)s</div>
</div></body></html>"""


def main():
    path = os.path.join(OUT, "tt_qiu_plain.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PAGE % dict(table=build_table()))

    from playwright.async_api import async_playwright

    async def shoot():
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
            pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=3)
            await pg.goto("file://" + path)
            await pg.wait_for_timeout(600)
            over = await pg.evaluate("() => document.querySelector('.page').scrollHeight - 1080")
            out = os.path.join(OUT, FILE)
            await pg.screenshot(path=out)
            print(f"{FILE} {os.path.getsize(out)//1024}KB  超出: {over}px")
            await b.close()

    asyncio.run(shoot())


if __name__ == "__main__":
    main()
