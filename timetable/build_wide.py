# -*- coding: utf-8 -*-
"""电脑横版（16:9）课表：星期为列（横排）、节次为行（竖排），与手机版方向一致。

作息（早读、课间操、课外活动、晚自修…）与上课节次同在一张表里按时间顺序排，
不再单独列成一条胶囊——单独列出来容易被忽略。

数据与主题直接复用 build.py，只换版式。
"""
import os, json

from build import (OUT, TITLE, SUBTITLE, SIGN, SCHEDULE, PERIOD_TIME, PERIOD_LABEL,
                   DAYS, NOTE_CELL, THEMES, item_at, busy_periods,
                   user_mascot, watermark_css, icon_css)

WIDE_FILES = {k: v["file"].replace(".png", "_横版.png") for k, v in THEMES.items()}


def build_head():
    """表头：左上角是节次栏，右边横排周一~周五"""
    cells = ['<div class="wh wh--corner">节次 · 时间</div>']
    cells += [f'<div class="wh"><span>{d}</span></div>' for d in DAYS]
    return "".join(cells)


def build_rows():
    """按时间顺序铺满一天：上课节次占五列，作息横贯整行"""
    BUSY = busy_periods()
    out = []
    for s in SCHEDULE:
        p = s.get("p")

        if not p:                                    # 作息行（每天相同）
            sub = f'<span class="wb__s">{s["sub"]}</span>' if s.get("sub") else ""
            tag = f'<span class="wb__g">{s["tag"]}</span>' if s.get("tag") else ""
            out.append(f'<div class="wt wt--soft"><i>{s["t"]}</i></div>')
            out.append(f'<div class="wband{" wband--tag" if s.get("tag") else ""}">'
                       f'<span class="wb__n">{s.get("icon","")} {s["name"]}</span>{sub}{tag}</div>')
            continue

        cls = "wt" + (" wt--mine" if p in BUSY else "")
        out.append(f'<div class="{cls}"><b>{PERIOD_LABEL[p]}</b></div>')
        for d in range(1, 6):
            it = item_at(d, p)
            note = NOTE_CELL.get((d, p))
            last = " wc--last" if d == 5 else ""
            if it:
                pill = "wpill" + (" wpill--duty" if it["duty"] else
                                  " wpill--qiu" if it.get("qiu") else "")
                pre = (f'<span class="wpill__pre">{it["pre"]}</span>' if it.get("pre")
                       else '' if it["duty"] else '<span class="ico"></span>')
                out.append(f'<div class="wc wc--on{last}"><div class="{pill}">'
                           f'<span class="wpill__k">{pre}{it["main"]}<em>{it["unit"] or it["sub"]}</em></span>'
                           f'<span class="wpill__u">{PERIOD_TIME[p]}</span></div></div>')
            elif note:
                out.append(f'<div class="wc wc--note{last}"><span>{note}</span></div>')
            else:
                out.append(f'<div class="wc{last}"><span class="wdot"></span></div>')

    return "".join(out)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{color:var(--ink);background-color:var(--bg);
     background-image:radial-gradient(var(--dot) 2px, transparent 2.1px);background-size:26px 26px;
     font-family:'Noto Sans SC','WenQuanYi Zen Hei',sans-serif;-webkit-font-smoothing:antialiased}
.page{width:1920px;height:1080px;padding:14px 34px 12px;display:flex;flex-direction:column;gap:10px}
h1,.wh span,.wt b{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
.wt i,.wpill__k,.wsp{font-family:'Fredoka','Noto Sans SC',sans-serif;font-variant-numeric:tabular-nums}

/* 顶部 */
.hero{position:relative;flex:none;background:var(--card);border:4px solid var(--ink);border-radius:24px;
      padding:9px 26px;display:flex;align-items:center;gap:20px;overflow:hidden;
      box-shadow:0 6px 0 var(--brand)}
.hero:before{content:"";position:absolute;right:-60px;top:-110px;width:280px;height:280px;z-index:0;
             border-radius:50%;background:linear-gradient(150deg,var(--soft),transparent 70%)}
.hero>*{position:relative;z-index:1}
.mascot{width:82px;height:82px;object-fit:contain;flex:none;
        filter:drop-shadow(0 4px 6px rgba(0,0,0,.14))}
h1{font-size:30px;line-height:1.1}
h1 small{display:block;font-size:14px;color:var(--muted);margin-top:3px;
         font-family:'Noto Sans SC',sans-serif}
.stats{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap;justify-content:flex-end;max-width:700px}
.stat{background:var(--soft);border:2.5px solid var(--ink);border-radius:999px;padding:4px 13px;
      font-size:15px;font-weight:700;white-space:nowrap}
.stat b{font-family:'Fredoka',sans-serif;color:var(--brand);font-size:18px}
.by{background:var(--soft);border:2px solid var(--brand);border-radius:999px;padding:3px 12px;
    font-size:13.5px;font-weight:700;color:var(--brand);white-space:nowrap}

/* 主表：星期为列（横排）、节次与作息为行（竖排） */
.grid{flex:none;display:grid;grid-template-columns:170px repeat(5,1fr);
      background:var(--card);border:4px solid var(--ink);border-radius:22px;overflow:hidden;
      box-shadow:0 7px 0 var(--line)}
.wh{background:linear-gradient(150deg,var(--brand),var(--brand2));color:#fff;text-align:center;
    font-size:23px;padding:6px 0 6px;border-right:2px solid rgba(255,255,255,.28)}
.wh:last-child{border-right:none}
.wh--corner{background:var(--ink);font-size:15px;font-weight:700;letter-spacing:2px;
            display:flex;align-items:center;justify-content:center;
            font-family:'Noto Sans SC',sans-serif;border-right:none}
.wt{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:0 14px;
    border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.wt b{font-size:19px;line-height:1;white-space:nowrap}
.wt i{font-style:normal;font-size:16px;font-weight:700;
      color:var(--ink);opacity:.78;white-space:nowrap}
.wt--soft{background:color-mix(in srgb,var(--bg) 76%,transparent)}
.wt--soft i{font-size:14.5px;opacity:.66}
.wt--mine{background:color-mix(in srgb,var(--soft) 76%,transparent);box-shadow:inset 6px 0 0 var(--brand)}
.wt--mine b{color:var(--brand)}
.wt--warn{background:color-mix(in srgb,var(--warnbg) 76%,transparent);box-shadow:inset 6px 0 0 var(--warn)}
.wt--warn b{color:var(--warn)}
.wt--foot{background:color-mix(in srgb,var(--bg) 76%,transparent);border-bottom:none}
.wt--foot b{font-size:17px;opacity:.8}
.wt--foot i{font-size:13.5px;opacity:.6}

/* 作息行：横贯五列 */
.wband{grid-column:2 / -1;height:22px;display:flex;align-items:center;gap:9px;padding:0 16px;
       background:color-mix(in srgb,var(--bg) 76%,transparent);
       border-bottom:2px solid var(--line)}
.wb__n{font-size:14.5px;font-weight:700;color:var(--ink);opacity:.74;white-space:nowrap}
.wb__s{font-size:13px;color:var(--muted);opacity:.9}
.wb__g{font-size:12px;font-weight:800;color:#fff;background:var(--brand);border-radius:99px;
       padding:1px 8px;white-space:nowrap}
.wband--tag{background:color-mix(in srgb,var(--soft) 82%,transparent)}

/* 上课格子 */
.wc{height:52px;display:flex;align-items:center;justify-content:center;padding:4px 8px;
    border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.wc--last{border-right:none}
.wdot{width:8px;height:8px;border-radius:50%;background:var(--line)}
.wpill{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;
       height:100%;padding:0 14px;border-radius:12px;color:#fff;
       background:linear-gradient(150deg,var(--brand2),var(--brand));
       box-shadow:0 3px 0 rgba(0,0,0,.13),0 4px 9px rgba(0,0,0,.13)}
.wpill--duty{background:linear-gradient(150deg,var(--warn2),var(--warn))}
/* 邱老师的课：空心虚线牌子 + 深色字，靠形状区分，不只靠颜色 */
.wpill--qiu{background:color-mix(in srgb,var(--qiu) 10%,#fff);color:var(--qiu);
            border:2.5px dashed var(--qiu);box-shadow:none}
.wpill--qiu .wpill__u{opacity:.8}
.wpill__pre{display:inline-block;background:var(--qiu);color:#fff;border-radius:6px;
            font-size:14px;font-weight:800;padding:0 6px;margin-right:4px;vertical-align:1px;
            font-family:'Noto Sans SC',sans-serif}
.wpill__k{font-size:21px;font-weight:800;line-height:1.05;
          display:flex;align-items:center;justify-content:center;gap:4px}
.wpill .ico{width:20px;height:20px}
.wpill__k em{font-size:13px;font-style:normal;font-weight:700;margin-left:2px;
             font-family:'Noto Sans SC',sans-serif}
.wpill__u{font-size:13.5px;font-weight:700;opacity:.95;letter-spacing:.2px;
          font-family:'Fredoka','Noto Sans SC',sans-serif}
.wc--note{background:color-mix(in srgb,var(--bg) 76%,transparent)}
.wc--note span{font-size:13px;color:var(--muted);font-weight:700;border:2px dashed var(--line);
               border-radius:10px;padding:3px 9px}
.wsp{height:30px;background:color-mix(in srgb,var(--bg) 76%,transparent);
     display:flex;align-items:center;justify-content:center;gap:7px;
     font-size:15px;font-weight:700;color:var(--ink);opacity:.85;
     border-right:2px solid var(--line)}
.wsp--last{border-right:none}
.wb2b{font-style:normal;font-size:12px;font-weight:800;color:#fff;background:var(--brand);
      border-radius:99px;padding:1px 8px;font-family:'Noto Sans SC',sans-serif;opacity:1}

.sign{flex:none;display:flex;align-items:center;justify-content:center;gap:12px}
.sign__l{height:3px;width:150px;border-radius:99px;background:var(--line)}
.sign__p{background:var(--card);border:2.5px solid var(--brand);border-radius:999px;padding:4px 20px;
         font-size:14.5px;font-weight:700;color:var(--muted)}
.sign b{font-size:18px;color:var(--brand);margin:0 4px;
        font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<style>:root{--brand:%(brand)s;--brand2:%(brand2)s;--accent:%(accent)s;--ink:%(ink)s;--bg:%(bg)s;
--card:%(card)s;--soft:%(soft)s;--line:%(line)s;--dot:%(dot)s;--muted:%(muted)s;
--warn:%(warn)s;--warn2:%(warn2)s;--warnbg:%(warnbg)s;--qiu:%(qiu)s;--qiu2:%(qiu2)s;}
%(css)s%(wm)s</style></head><body><div class="page">

  <div class="hero">
    %(mascot)s
    <div><h1>%(title)s<small>%(subtitle)s</small></h1></div>
    <div class="stats">
      <span class="stat">每周 <b>9</b> 节</span>
      <span class="stat">周一到周五 <b>每周相同</b></span>
      <span class="stat">最早 <b>7:40</b></span>
      <span class="by">%(sign)s 制</span>
    </div>
  </div>

  <div class="grid">%(head)s%(rows)s</div>

  <div class="sign">
    <span class="sign__l"></span>
    <span class="sign__p">%(hearts)s 这张课表是 <b>%(sign)s</b> 做的</span>
    <span class="sign__l"></span>
  </div>
</div></body></html>"""


def main():
    for key, c in THEMES.items():
        html = PAGE % dict(
            css=CSS, brand=c["brand"], brand2=c["brand2"], accent=c["accent"], ink=c["ink"],
            bg=c["bg"], card=c["card"], soft=c["soft"], line=c["line"], dot=c["dot"],
            muted=c["muted"], warn=c["warn"], warn2=c["warn2"], warnbg=c["warnbg"],
            qiu=c["qiu"], qiu2=c["qiu2"],
            mascot=(user_mascot(key) or c["mascot"](c)), hearts=c["hearts"],
            title=TITLE, subtitle=SUBTITLE, sign=SIGN,
            head=build_head(), rows=build_rows(),
            wm=watermark_css(key, '560px', top=40, left=170) + icon_css(key),
        )
        path = os.path.join(OUT, f"tt_wide_{key}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", path)

    with open(os.path.join(OUT, "themes_wide.json"), "w", encoding="utf-8") as f:
        json.dump(WIDE_FILES, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
