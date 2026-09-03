# -*- coding: utf-8 -*-
"""邱老师的精简版课表（电脑横版 16:9）。

只留核心：周一~周五 × 第1~9节，有课的格子写班级和时间。
作息、早读、晚自修、打卡、全校会议这些都不放——那是给天天盯着表的人用的。
"""
import os, asyncio

from build import SIGN, PERIOD_TIME, PERIOD_LABEL, DAYS, QIU, THEMES, mascot_uri

OUT = os.path.dirname(os.path.abspath(__file__))
FILE = "政治课表_邱老师版_精简.png"
TITLE = "邱老师的政治课表"
PERIODS = sorted({p for _, p, _ in QIU})     # 只留有课的节次，空行全部去掉


def lesson(d, p):
    for (dd, pp, k) in QIU:
        if dd == d and pp == p:
            return k
    return None


def build_table():
    out = ['<div class="h h--corner">节次</div>']
    out += [f'<div class="h">{d}</div>' for d in DAYS]
    for p in PERIODS:
        out.append(f'<div class="t t--on">'
                   f'<b>{PERIOD_LABEL[p]}</b><i>{PERIOD_TIME[p]}</i></div>')
        for d in range(1, 6):
            k = lesson(d, p)
            last = " c--last" if d == 5 else ""
            if k:
                out.append(f'<div class="c{last}"><div class="pill">'
                           f'<span class="k">{k}<em>班</em></span>'
                           f'<span class="tm">{PERIOD_TIME[p]}</span></div></div>')
            else:
                out.append(f'<div class="c{last}"><span class="dot"></span></div>')
    return "".join(out)


PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>
:root{--brand:%(brand)s;--brand2:%(brand2)s;--brandd:%(brandd)s;--ink:%(ink)s;--bg:%(bg)s;
--card:%(card)s;--soft:%(soft)s;--line:%(line)s;--dot:%(dot)s;--muted:%(muted)s;}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{color:var(--ink);background-color:var(--bg);
     background-image:radial-gradient(var(--dot) 2px,transparent 2.1px);background-size:26px 26px;
     font-family:'Noto Sans SC','WenQuanYi Zen Hei',sans-serif;-webkit-font-smoothing:antialiased}
.page{width:1920px;height:1080px;padding:30px 46px 26px;display:flex;flex-direction:column;gap:18px}
h1,.h,.t b{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
.t i,.k{font-family:'Fredoka','Noto Sans SC',sans-serif;font-variant-numeric:tabular-nums}

.hero{flex:none;display:flex;align-items:center;gap:22px;padding:0 8px}
.hero img{width:96px;height:96px;object-fit:contain;
          filter:drop-shadow(0 5px 8px rgba(0,0,0,.14))}
h1{font-size:44px;line-height:1.1}
h1 small{display:block;font-size:19px;color:var(--muted);margin-top:6px;
         font-family:'Noto Sans SC',sans-serif}
.by{margin-left:auto;background:var(--soft);border:2.5px solid var(--brand);border-radius:999px;
    padding:6px 18px;font-size:18px;font-weight:700;color:var(--brand)}

.grid{position:relative;flex:1;display:grid;grid-template-columns:220px repeat(5,1fr);
      grid-auto-rows:1fr;background:var(--card);border:4px solid var(--ink);border-radius:26px;
      overflow:hidden;box-shadow:0 8px 0 var(--line)}
.grid:before{content:'';position:absolute;top:92px;bottom:0;left:220px;right:0;z-index:0;
             pointer-events:none;opacity:.16;
             background:url('%(wm)s') center center / 520px auto no-repeat}
.grid>*{position:relative;z-index:1}
.h{background:linear-gradient(150deg,var(--brand),var(--brand2));color:#fff;text-align:center;
   font-size:30px;padding:16px 0 14px;border-right:2px solid rgba(255,255,255,.28)}
.h:nth-child(6){border-right:none}
.h--corner{background:var(--ink);font-size:20px;font-weight:700;letter-spacing:3px;
           font-family:'Noto Sans SC',sans-serif;border-right:none;
           display:flex;align-items:center;justify-content:center}
.t{display:flex;flex-direction:column;align-items:center;justify-content:center;
   border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.t b{font-size:31px;line-height:1.15}
.t i{font-style:normal;font-size:23px;font-weight:700;opacity:.72;margin-top:3px}
.t--on{background:color-mix(in srgb,var(--soft) 76%%,transparent);
       box-shadow:inset 7px 0 0 var(--brand)}
.t--on b{color:var(--brand)}
.c{display:flex;align-items:center;justify-content:center;padding:9px 12px;
   border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.c--last{border-right:none}
.dot{width:10px;height:10px;border-radius:50%%;background:var(--line)}
.pill{width:100%%;height:100%%;border-radius:18px;color:#fff;
      display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;
      background:linear-gradient(150deg,var(--brand),var(--brandd));
      box-shadow:0 4px 0 rgba(0,0,0,.13),0 6px 14px rgba(0,0,0,.13)}
.k{font-size:48px;font-weight:800;line-height:1}
.tm{font-size:23px;font-weight:700;opacity:.96;
    font-family:'Fredoka','Noto Sans SC',sans-serif}
.k em{font-size:24px;font-style:normal;font-weight:700;margin-left:4px;
      font-family:'Noto Sans SC',sans-serif}

.foot{flex:none;text-align:center;font-size:17px;font-weight:600;color:var(--muted)}
</style></head><body><div class="page">
  <div class="hero">
    <img src="%(mascot)s" alt="">
    <h1>%(title)s<small>2026 学年第一学期　·　任教 126 / 127 / 130 班</small></h1>
    <span class="by">%(sign)s 制</span>
  </div>
  <div class="grid">%(table)s</div>
  <div class="foot">每周固定，本学期相同</div>
</div></body></html>"""


def main():
    c = THEMES["kuromi"]
    uri = mascot_uri("kuromi", plain=True) or ""
    html = PAGE % dict(brand=c["brand"], brand2=c["brand2"], brandd=c["brandd"], ink=c["ink"],
                       bg=c["bg"], card=c["card"], soft=c["soft"], line=c["line"], dot=c["dot"],
                       muted=c["muted"], wm=mascot_uri("kuromi") or "", mascot=uri,
                       title=TITLE, sign=SIGN, table=build_table())
    path = os.path.join(OUT, "tt_qiu_simple.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    from playwright.async_api import async_playwright

    async def shoot():
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
            pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=3)
            await pg.goto("file://" + path)
            await pg.wait_for_timeout(700)
            over = await pg.evaluate("() => document.querySelector('.page').scrollHeight - 1080")
            out = os.path.join(OUT, FILE)
            await pg.screenshot(path=out)
            print(f"{FILE} {os.path.getsize(out)//1024}KB  超出: {over}px")
            await b.close()

    asyncio.run(shoot())


if __name__ == "__main__":
    main()
