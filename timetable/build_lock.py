# -*- coding: utf-8 -*-
"""手机锁屏版：按手机屏幕比例（9:19.5）出图，顶部留给时钟、底部留给相机/手电筒按钮。

中间的安全区里放完整表格（节次为行、周一~周五为列，作息横贯整行），
上课格子里写班级和时间，和竖版/横版口径一致。
"""
import os, json

from build import (OUT, TITLE, SIGN, SCHEDULE, PERIOD_TIME, PERIOD_LABEL, DAYS,
                   NOTE_CELL, THEMES, item_at, busy_periods, mascot_uri,
                   watermark_css, icon_css)

LOCK_FILES = {k: v["file"].replace(".png", "_锁屏版.png") for k, v in THEMES.items()}

W, H = 1080, 2340          # 9:19.5，主流手机比例
CLOCK_ZONE = 916           # 顶部时钟 + 日期 + iOS 小组件占用（实测到屏幕 40% 左右）
BUTTON_ZONE = 290          # 底部两颗圆形按钮占用


def build_table():
    BUSY = busy_periods()
    out = [f'<div class="lh lh--corner">时间</div>']
    out += [f'<div class="lh">{d}</div>' for d in DAYS]

    run = []                                        # 连续的作息条攒在一起
    def flush():
        if not run:
            return
        chips = "".join(f'<span class="lb"><b>{r["name"]}</b>'
                        f'<i>{r["t"]}</i></span>' for r in run)
        out.append(f'<div class="lband">{chips}</div>')
        run.clear()

    for s in SCHEDULE:
        p = s.get("p")
        if not p:                                   # 作息：并排放进同一行
            run.append(s)
            continue
        flush()

        cls = "lt" + (" lt--mine" if p in BUSY else "")
        out.append(f'<div class="{cls}"><b>{PERIOD_LABEL[p]}</b><i>{PERIOD_TIME[p]}</i></div>')
        for d in range(1, 6):
            it = item_at(d, p)
            note = NOTE_CELL.get((d, p))
            last = " lc--last" if d == 5 else ""
            if it:
                pill = "lpill" + (" lpill--duty" if it["duty"] else
                                  " lpill--qiu" if it.get("qiu") else "")
                pre = (f'<span class="lp__pre">{it["pre"]}</span>' if it.get("pre")
                       else '' if it["duty"] else '<span class="ico"></span>')
                out.append(f'<div class="lc{last}"><div class="{pill}">'
                           f'<span class="lp__k">{pre}{it["main"]}<em>{it["unit"] or it["sub"]}</em></span>'
                           f'<span class="lp__t">{PERIOD_TIME[p]}</span></div></div>')
            elif note:
                out.append(f'<div class="lc lc--note{last}"><span>{note}</span></div>')
            else:
                out.append(f'<div class="lc{last}"><span class="ldot"></span></div>')
    flush()
    return "".join(out)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)spx;height:%(H)spx;overflow:hidden}
body{color:var(--ink);background-color:var(--bg);
     background-image:radial-gradient(var(--dot) 2.4px, transparent 2.5px);background-size:30px 30px;
     font-family:'Noto Sans SC','WenQuanYi Zen Hei',sans-serif;-webkit-font-smoothing:antialiased}
.page{width:%(W)spx;height:%(H)spx;padding:%(CLOCK)spx 20px %(BTN)spx;
      display:flex;flex-direction:column;gap:10px;position:relative}

/* 时钟正下方那片空白放不透明的角色本体；表格里另有半透明水印 */
.page .topm{position:absolute;left:0;right:0;top:%(WMTOP)spx;height:330px;z-index:1;
      pointer-events:none;
      background:url('%(TOPM)s') center center / 320px auto no-repeat;
      filter:drop-shadow(0 6px 10px rgba(0,0,0,.14))}
.page>*{position:relative;z-index:1}

.hd{display:flex;align-items:center;gap:10px;flex:none;padding:0 4px}
.hd__t{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-size:27px;line-height:1.15}
.hd__s{display:block;font-size:15px;font-weight:600;color:var(--muted);margin-top:2px;
       font-family:'Noto Sans SC',sans-serif}
.hd__by{margin-left:auto;background:var(--soft);border:2px solid var(--brand);border-radius:999px;
        padding:3px 12px;font-size:14px;font-weight:700;color:var(--brand);white-space:nowrap}

.grid{flex:1;display:grid;grid-template-columns:150px repeat(5,1fr);
      grid-auto-rows:min-content;align-content:start;
      background:var(--card);border:4px solid var(--ink);border-radius:20px;overflow:hidden;
      box-shadow:0 6px 0 var(--line)}
.lh{background:linear-gradient(150deg,var(--brand),var(--brand2));color:#fff;text-align:center;
    font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-size:25px;padding:7px 0 6px;
    border-right:2px solid rgba(255,255,255,.28)}
.lh:nth-child(6){border-right:none}
.lh--corner{background:var(--ink);font-size:16px;font-weight:700;letter-spacing:2px;
            font-family:'Noto Sans SC',sans-serif;border-right:none;
            display:flex;align-items:center;justify-content:center}

.lt{height:80px;display:flex;flex-direction:column;align-items:center;justify-content:center;
    border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.lt b{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-size:23px;line-height:1.15}
.lt i{font-style:normal;font-size:17px;font-weight:700;color:var(--ink);opacity:.75;
      font-family:'Fredoka','Noto Sans SC',sans-serif;margin-top:2px}
.lt--mine{background:color-mix(in srgb,var(--soft) 76%%,transparent);
          box-shadow:inset 6px 0 0 var(--brand)}
.lt--mine b{color:var(--brand)}

.lband{grid-column:1 / -1;display:flex;align-items:center;justify-content:space-around;
       flex-wrap:wrap;gap:2px 14px;padding:6px 12px;
       background:color-mix(in srgb,var(--bg) 76%%,transparent);
       border-bottom:2px solid var(--line)}
.lb{display:flex;align-items:baseline;gap:6px;white-space:nowrap}
.lb b{font-size:19px;font-weight:700;color:var(--ink);opacity:.8}
.lb i{font-style:normal;font-size:18px;font-weight:700;color:var(--muted);
      font-family:'Fredoka','Noto Sans SC',sans-serif}

.lc{height:80px;display:flex;align-items:center;justify-content:center;padding:5px 6px;
    border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.lc--last{border-right:none}
.ldot{width:9px;height:9px;border-radius:50%%;background:var(--line)}
.lpill{width:100%%;height:100%%;border-radius:15px;color:#fff;
       display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;
       background:linear-gradient(150deg,var(--brand),var(--brandd));
       box-shadow:0 3px 0 rgba(0,0,0,.13)}
.lpill--duty{background:linear-gradient(150deg,var(--warn2),var(--warn))}
/* 邱老师的课：空心虚线牌子 + 深色字，靠形状区分，不只靠颜色 */
.lpill--qiu{background:color-mix(in srgb,var(--qiu) 7%%,#fff);color:var(--qiu);
            border:3px dashed color-mix(in srgb,var(--qiu) 45%%,#fff);box-shadow:none}
.lpill--qiu .lp__t{opacity:.8}
.lp__pre{display:inline-block;background:color-mix(in srgb,var(--qiu) 78%%,#fff);
         color:#fff;border-radius:7px;
         font-size:17px;font-weight:800;padding:1px 7px;margin-right:5px;vertical-align:2px;
         font-family:'Noto Sans SC',sans-serif}
.lp__k{font-size:27px;font-weight:800;line-height:1;
       display:flex;align-items:center;justify-content:center;gap:5px;
       font-family:'Fredoka','Noto Sans SC',sans-serif}
.lpill .ico{width:24px;height:24px}
.lp__k em{font-size:15px;font-style:normal;font-weight:700;margin-left:2px;
          font-family:'Noto Sans SC',sans-serif}
.lp__t{font-size:16px;font-weight:700;opacity:.97;
       font-family:'Fredoka','Noto Sans SC',sans-serif}
.lc--note{background:color-mix(in srgb,var(--bg) 76%%,transparent)}
.lc--note span{font-size:15px;color:var(--ink);font-weight:700;opacity:.8;
               background:var(--soft);border-radius:11px;padding:5px 12px}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<style>:root{--brand:%(brand)s;--brand2:%(brand2)s;--ink:%(ink)s;--bg:%(bg)s;--card:%(card)s;
--soft:%(soft)s;--line:%(line)s;--dot:%(dot)s;--muted:%(muted)s;
--warn:%(warn)s;--warn2:%(warn2)s;--qiu:%(qiu)s;--qiu2:%(qiu2)s;--brandd:%(brandd)s;}
%(css)s</style></head><body><div class="page">
  <div class="topm"></div>
  <div class="hd">
    <span class="hd__t">%(title)s<span class="hd__s">任教 125 / 128 / 129　·　虚线框＝邱老师</span></span>
    <span class="hd__by">%(sign)s 制</span>
  </div>
  <div class="grid">%(table)s</div>
</div></body></html>"""


def main():
    for key, c in THEMES.items():
        html = PAGE % dict(
            css=CSS % dict(W=W, H=H, CLOCK=CLOCK_ZONE, BTN=BUTTON_ZONE,
                           TOPM=mascot_uri(key, plain=True) or "", WMTOP=CLOCK_ZONE - 375)
                + watermark_css(key, '420px', top=42, left=150, opacity=.16)
                + icon_css(key),
            brand=c["brand"], brand2=c["brand2"], ink=c["ink"], bg=c["bg"], card=c["card"],
            soft=c["soft"], line=c["line"], dot=c["dot"], muted=c["muted"],
            warn=c["warn"], warn2=c["warn2"], qiu=c["qiu"], qiu2=c["qiu2"],
            brandd=c["brandd"],
            title=TITLE, sign=SIGN, table=build_table(),
        )
        path = os.path.join(OUT, f"tt_lock_{key}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", path)

    with open(os.path.join(OUT, "themes_lock.json"), "w", encoding="utf-8") as f:
        json.dump(LOCK_FILES, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
