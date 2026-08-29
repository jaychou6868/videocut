# -*- coding: utf-8 -*-
"""电脑横版（16:9）课表：星期为列（横排）、节次为行（竖排），与手机版方向一致。

数据与主题直接复用 build.py，只换版式。
"""
import os, json

from build import (OUT, TITLE, SUBTITLE, SIGN, SCHEDULE, PERIOD_TIME, MY, DAYS,
                   NOTE_CELL, THEMES, lesson_at, day_lessons, day_span, user_mascot,
                   watermark_css)

PERIODS = sorted(PERIOD_TIME)                       # 1..9
WARN_P = {s["p"] for s in SCHEDULE if s.get("warn") and s.get("p")}
ROUTINE = [s for s in SCHEDULE if not s.get("p")]   # 作息（非上课时段）

WIDE_FILES = {k: v["file"].replace(".png", "_横版.png") for k, v in THEMES.items()}


def build_head():
    """表头：左上角是节次栏，右边横排周一~周五"""
    cells = ['<div class="wh wh--corner">节次 · 时间</div>']
    cells += [f'<div class="wh"><span>{d}</span></div>' for d in DAYS]
    return "".join(cells)


def build_rows():
    """每行一个节次，行内横排五天；最后补一行当天跨度"""
    out = []
    for p in PERIODS:
        warn = p in WARN_P
        mine = any(m[1] == p for m in MY)
        cls = "wt" + (" wt--warn" if warn else (" wt--mine" if mine else ""))
        badge = ""
        out.append(f'<div class="{cls}"><b>第{p}节</b>{badge}<i>{PERIOD_TIME[p]}</i></div>')
        for d in range(1, 6):
            k = lesson_at(d, p)
            note = NOTE_CELL.get((d, p))
            last = " wc--last" if d == 5 else ""
            if k:
                pill = "wpill" + (" wpill--nine" if warn else "")
                out.append(f'<div class="wc wc--on{last}"><div class="{pill}">'
                           f'<span class="wpill__k">{k}<em>班</em></span>'
                           f'<span class="wpill__u">政治</span></div></div>')
            elif note:
                out.append(f'<div class="wc wc--note{last}"><span>{note}</span></div>')
            else:
                out.append(f'<div class="wc{last}"><span class="wdot"></span></div>')

    out.append('<div class="wt wt--foot"><b>当天</b><i>上课跨度</i></div>')
    for d in range(1, 6):
        span, b2b = day_span(day_lessons(d))
        tag = '<em class="wb2b">连堂</em>' if b2b else ""
        out.append(f'<div class="wsp{" wsp--last" if d == 5 else ""}">{span}{tag}</div>')
    return "".join(out)


def build_routine():
    return "".join(
        f'<div class="rc"><span class="rc__i">{s.get("icon","")}</span>'
        f'<span class="rc__n">{s["name"]}</span><span class="rc__t">{s["t"]}</span></div>'
        for s in ROUTINE)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{color:var(--ink);background-color:var(--bg);
     background-image:radial-gradient(var(--dot) 2px, transparent 2.1px);background-size:26px 26px;
     font-family:'Noto Sans SC','WenQuanYi Zen Hei',sans-serif;-webkit-font-smoothing:antialiased}
.page{width:1920px;height:1080px;padding:26px 34px 20px;display:flex;flex-direction:column;gap:16px}
h1,.wd,.wh b,h3{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
.wh i,.wpill__k,.wsp,.rc__t{font-family:'Fredoka','Noto Sans SC',sans-serif;font-variant-numeric:tabular-nums}

/* 顶部 */
.hero{position:relative;flex:none;background:var(--card);border:4px solid var(--ink);border-radius:26px;
      padding:12px 26px;display:flex;align-items:center;gap:22px;overflow:hidden;
      box-shadow:0 7px 0 var(--brand)}
.hero:before{content:"";position:absolute;right:-60px;top:-110px;width:300px;height:300px;z-index:0;
             border-radius:50%;background:linear-gradient(150deg,var(--soft),transparent 70%)}
.hero>*{position:relative;z-index:1}
.mascot{width:130px;height:130px;object-fit:contain;flex:none;
        filter:drop-shadow(0 4px 6px rgba(0,0,0,.14))}
h1{font-size:38px;line-height:1.1}
h1 small{display:block;font-size:15px;color:var(--muted);margin-top:4px;
         font-family:'Noto Sans SC',sans-serif}
.stats{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap;justify-content:flex-end;max-width:660px}
.stat{background:var(--soft);border:2.5px solid var(--ink);border-radius:999px;padding:5px 14px;
      font-size:16px;font-weight:700;white-space:nowrap}
.stat b{font-family:'Fredoka',sans-serif;color:var(--brand);font-size:19px}
.by{background:var(--soft);border:2px solid var(--brand);border-radius:999px;padding:3px 12px;
    font-size:14px;font-weight:700;color:var(--brand);white-space:nowrap}
.deco{position:absolute;left:152px;bottom:9px;font-size:17px;letter-spacing:5px;opacity:.75;z-index:1}

/* 主表：星期为列（横排）、节次为行（竖排） */
.grid{flex:none;display:grid;grid-template-columns:268px repeat(5,1fr);
      background:var(--card);border:4px solid var(--ink);border-radius:24px;overflow:hidden;
      box-shadow:0 8px 0 var(--line)}
.wh{background:linear-gradient(150deg,var(--brand),var(--brand2));color:#fff;text-align:center;
    font-size:27px;padding:12px 0 11px;border-right:2px solid rgba(255,255,255,.28)}
.wh:last-child{border-right:none}
.wh--corner{background:var(--ink);font-size:16px;font-weight:700;letter-spacing:2px;
            display:flex;align-items:center;justify-content:center;
            font-family:'Noto Sans SC',sans-serif;border-right:none}
.wt{display:flex;align-items:center;gap:8px;padding:0 15px;
    border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.wt b{font-size:21px;line-height:1;white-space:nowrap}
.wt i{margin-left:auto;font-style:normal;font-size:17.5px;font-weight:700;
      color:var(--ink);opacity:.78;white-space:nowrap}
.wt--mine{background:color-mix(in srgb,var(--soft) 76%,transparent);box-shadow:inset 6px 0 0 var(--brand)}
.wt--mine b{color:var(--brand)}
.wt--warn{background:color-mix(in srgb,var(--warnbg) 76%,transparent);box-shadow:inset 6px 0 0 var(--warn)}
.wt--warn b{color:var(--warn)}
.wt--foot{background:color-mix(in srgb,var(--bg) 76%,transparent);border-bottom:none}
.wt--foot b{font-size:18px;opacity:.8}
.wt--foot i{font-size:14px;opacity:.6}
.wtag{font-size:11.5px;font-weight:800;color:#fff;background:var(--warn);border-radius:99px;
      padding:1px 7px;font-family:'Noto Sans SC',sans-serif}
.wc{height:56px;display:flex;align-items:center;justify-content:center;padding:5px 8px;
    border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.wc--last{border-right:none}
.wdot{width:9px;height:9px;border-radius:50%;background:var(--line)}
.wpill{display:flex;align-items:center;justify-content:center;gap:8px;height:100%;
       padding:0 20px;border-radius:13px;color:#fff;
       background:linear-gradient(150deg,var(--brand2),var(--brand));
       box-shadow:0 3px 0 rgba(0,0,0,.13),0 4px 10px rgba(0,0,0,.13)}
.wpill--nine{background:linear-gradient(150deg,var(--warn2),var(--warn))}
.wpill__k{font-size:25px;font-weight:800;line-height:1}
.wpill__k em{font-size:14px;font-style:normal;font-weight:700;margin-left:2px;
             font-family:'Noto Sans SC',sans-serif}
.wpill__u{font-size:13px;font-weight:700;opacity:.92;letter-spacing:1px}
.wc--note{background:color-mix(in srgb,var(--bg) 76%,transparent)}
.wc--note span{font-size:14px;color:var(--muted);font-weight:700;border:2px dashed var(--line);
               border-radius:11px;padding:4px 10px}
.wsp{height:46px;background:color-mix(in srgb,var(--bg) 76%,transparent);display:flex;align-items:center;justify-content:center;gap:7px;
     font-size:16px;font-weight:700;color:var(--ink);opacity:.85;
     border-right:2px solid var(--line)}
.wsp--last{border-right:none}
.wb2b{font-style:normal;font-size:12.5px;font-weight:800;color:#fff;background:var(--brand);
      border-radius:99px;padding:1px 8px;font-family:'Noto Sans SC',sans-serif}

/* 作息条 */
.routine{flex:none;background:var(--card);border:3px solid var(--ink);border-radius:22px;
         padding:11px 16px;box-shadow:0 6px 0 var(--line);
         display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.rtitle{font-size:16px;font-weight:800;color:var(--brand);margin-right:4px;white-space:nowrap}
.rc{display:flex;align-items:center;gap:5px;background:var(--bg);border:2px solid var(--line);
    border-radius:999px;padding:4px 12px;white-space:nowrap}
.rc__i{font-size:14px}
.rc__n{font-size:15px;font-weight:700;color:var(--ink);opacity:.8}
.rc__t{font-size:15px;font-weight:700;color:var(--muted)}

/* 说明 */
.notes{flex:1;display:grid;grid-template-columns:1.6fr 1fr;gap:14px;min-height:0}
.note{background:var(--card);border:3px solid var(--ink);border-radius:20px;padding:10px 16px;
      box-shadow:0 5px 0 var(--line);overflow:hidden}
.note--warn{background:var(--warnbg);border-color:var(--warn);box-shadow:0 5px 0 var(--warn)}
.note h3{font-size:18px;margin-bottom:4px}
.note li,.note p{font-size:14.5px;line-height:1.55;font-weight:500}
.note ul{margin-left:19px}
.note b{color:var(--warn)}
.notes{flex:none;display:block}
.note--sr{display:flex;align-items:center;gap:22px;height:100%}
.note--sr h3{margin:0;white-space:nowrap}
.note--sr .sr{flex:1;margin:0}
.note--sr .sr__t{margin:0;white-space:nowrap}
.sr{display:flex;gap:9px;margin-top:3px}
.sr__i{flex:1;background:var(--soft);border:2.5px solid var(--ink);border-radius:14px;
       padding:6px 6px 7px;text-align:center}
.sr__d{display:block;font-size:12.5px;color:var(--muted);font-weight:700}
.sr__i b{font-size:21px;color:var(--brand);
         font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
.sr__i--b b{color:var(--warn)}
.sr__t{margin-top:7px;text-align:center;font-size:13.5px;font-weight:700;color:var(--ink);opacity:.7}

.sign{flex:none;display:flex;align-items:center;justify-content:center;gap:12px}
.sign__l{height:3px;width:150px;border-radius:99px;background:var(--line)}
.sign__p{background:var(--card);border:2.5px solid var(--brand);border-radius:999px;padding:5px 20px;
         font-size:15px;font-weight:700;color:var(--muted)}
.sign b{font-size:19px;color:var(--brand);margin:0 4px;
        font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<style>:root{--brand:%(brand)s;--brand2:%(brand2)s;--accent:%(accent)s;--ink:%(ink)s;--bg:%(bg)s;
--card:%(card)s;--soft:%(soft)s;--line:%(line)s;--dot:%(dot)s;--muted:%(muted)s;
--warn:%(warn)s;--warn2:%(warn2)s;--warnbg:%(warnbg)s;}
%(css)s%(wm)s</style></head><body><div class="page">

  <div class="hero">
    %(mascot)s
    <div><h1>%(title)s<small>%(subtitle)s</small></h1></div>
    <div class="deco">%(deco)s</div>
    <div class="stats">
      <span class="stat">每周 <b>9</b> 节</span>
      <span class="stat">周一到周五 <b>每周相同</b></span>
      <span class="stat">最早 <b>7:40</b></span>
      <span class="by">%(sign)s 制</span>
    </div>
  </div>

  <div class="grid">%(head)s%(rows)s</div>

  <div class="routine"><span class="rtitle">⏰ 每天固定作息</span>%(routine)s</div>

  <div class="notes">
    <div class="note note--sr">
      <h3>📖 早自修（全校统一）</h3>
      <div class="sr">
        <div class="sr__i"><span class="sr__d">周一 · 周三 · 周五</span><b>英语</b></div>
        <div class="sr__i sr__i--b"><span class="sr__d">周二 · 周四</span><b>语文</b></div>
      </div>
      <div class="sr__t">早读 6:30—7:00　·　早自修 7:00—7:25</div>
    </div>
  </div>

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
            mascot=(user_mascot(key) or c["mascot"](c)), hearts=c["hearts"], deco=c["deco"],
            title=TITLE, subtitle=SUBTITLE, sign=SIGN,
            head=build_head(), rows=build_rows(), routine=build_routine(),
            wm=watermark_css(key, '480px'),
        )
        path = os.path.join(OUT, f"tt_wide_{key}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", path)

    with open(os.path.join(OUT, "themes_wide.json"), "w", encoding="utf-8") as f:
        json.dump(WIDE_FILES, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
