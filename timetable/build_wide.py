# -*- coding: utf-8 -*-
"""电脑横版（16:9）课表：星期为行、节次为列，一屏看完不用滚动。

数据与主题直接复用 build.py，只换版式。
"""
import os, json

from build import (OUT, TITLE, SUBTITLE, SIGN, SCHEDULE, PERIOD_TIME, MY, DAYS,
                   NOTE_CELL, THEMES, lesson_at, day_lessons, day_span, user_mascot)

PERIODS = sorted(PERIOD_TIME)                       # 1..9
WARN_P = {s["p"] for s in SCHEDULE if s.get("warn") and s.get("p")}
ROUTINE = [s for s in SCHEDULE if not s.get("p")]   # 作息（非上课时段）

WIDE_FILES = {k: v["file"].replace(".png", "_横版.png") for k, v in THEMES.items()}


def build_head():
    cells = ['<div class="wh wh--day">星期</div>']
    for p in PERIODS:
        warn = " wh--warn" if p in WARN_P else ""
        cells.append(f'<div class="wh{warn}"><b>第{p}节</b><i>{PERIOD_TIME[p]}</i></div>')
    cells.append('<div class="wh wh--day">当天</div>')
    return "".join(cells)


def build_rows():
    out = []
    for d in range(1, 6):
        out.append(f'<div class="wd">{DAYS[d-1]}</div>')
        for p in PERIODS:
            k = lesson_at(d, p)
            note = NOTE_CELL.get((d, p))
            if k:
                pill = "wpill" + (" wpill--nine" if p in WARN_P else "")
                out.append(f'<div class="wc wc--on"><div class="{pill}">'
                           f'<span class="wpill__k">{k}<em>班</em></span>'
                           f'<span class="wpill__u">政治</span></div></div>')
            elif note:
                out.append(f'<div class="wc wc--note"><span>{note}</span></div>')
            else:
                out.append('<div class="wc"><span class="wdot"></span></div>')
        span, b2b = day_span(day_lessons(d))
        tag = '<em class="wb2b">连堂</em>' if b2b else ""
        out.append(f'<div class="wsp">{span}{tag}</div>')
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

/* 主表：星期为行、节次为列 */
.grid{flex:none;display:grid;grid-template-columns:126px repeat(9,1fr) 176px;
      background:var(--card);border:4px solid var(--ink);border-radius:24px;overflow:hidden;
      box-shadow:0 8px 0 var(--line)}
.wh{background:linear-gradient(150deg,var(--brand),var(--brand2));color:#fff;text-align:center;
    padding:9px 2px 10px;border-right:2px solid rgba(255,255,255,.28)}
.wh b{display:block;font-size:23px;line-height:1.15}
.wh i{display:block;font-style:normal;font-size:14.5px;font-weight:600;opacity:.95;margin-top:1px}
.wh--warn{background:linear-gradient(150deg,var(--warn),var(--warn2))}
.wh--day{background:var(--ink);font-size:17px;font-weight:700;letter-spacing:3px;
         display:flex;align-items:center;justify-content:center;
         font-family:'Noto Sans SC',sans-serif;border-right:none}
.wd{background:var(--soft);border-bottom:2px solid var(--line);border-right:2px solid var(--line);
    display:flex;align-items:center;justify-content:center;font-size:28px;color:var(--brand)}
.wc{border-bottom:2px solid var(--line);border-right:2px solid var(--line);height:92px;
    display:flex;align-items:center;justify-content:center;padding:7px 8px}
.wdot{width:9px;height:9px;border-radius:50%;background:var(--line)}
.wpill{width:100%;height:100%;border-radius:15px;display:flex;flex-direction:column;
       align-items:center;justify-content:center;color:#fff;
       background:linear-gradient(150deg,var(--brand2),var(--brand));
       box-shadow:0 4px 0 rgba(0,0,0,.13),0 5px 11px rgba(0,0,0,.13)}
.wpill--nine{background:linear-gradient(150deg,var(--warn2),var(--warn))}
.wpill__k{font-size:30px;font-weight:800;line-height:1.05}
.wpill__k em{font-size:15px;font-style:normal;font-weight:700;margin-left:2px;
             font-family:'Noto Sans SC',sans-serif}
.wpill__u{font-size:12.5px;font-weight:700;opacity:.95;letter-spacing:1.5px;margin-top:1px}
.wc--note{background:var(--bg)}
.wc--note span{font-size:14px;color:var(--muted);font-weight:700;border:2px dashed var(--line);
               border-radius:11px;padding:5px 9px}
.wsp{border-bottom:2px solid var(--line);background:var(--bg);display:flex;align-items:center;
     justify-content:center;gap:7px;font-size:16px;font-weight:700;color:var(--ink);opacity:.8}
.wb2b{font-style:normal;font-size:12.5px;font-weight:800;color:#fff;background:var(--brand);
      border-radius:99px;padding:1px 8px;font-family:'Noto Sans SC',sans-serif;opacity:1}

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
.notes{flex:1;display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:14px;min-height:0}
.note{background:var(--card);border:3px solid var(--ink);border-radius:20px;padding:10px 16px;
      box-shadow:0 5px 0 var(--line);overflow:hidden}
.note--warn{background:var(--warnbg);border-color:var(--warn);box-shadow:0 5px 0 var(--warn)}
.note h3{font-size:18px;margin-bottom:4px}
.note li,.note p{font-size:14.5px;line-height:1.55;font-weight:500}
.note ul{margin-left:19px}
.note b{color:var(--warn)}
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
%(css)s</style></head><body><div class="page">

  <div class="hero">
    %(mascot)s
    <div><h1>%(title)s<small>%(subtitle)s</small></h1></div>
    <div class="deco">%(deco)s</div>
    <div class="stats">
      <span class="stat">每周 <b>9</b> 节</span>
      <span class="stat">周一到周五 <b>每周相同</b></span>
      <span class="stat">最早 <b>7:40</b></span>
      <span class="stat">第9节 <b>2</b> 节待确认</span>
      <span class="by">%(sign)s 制</span>
    </div>
  </div>

  <div class="grid">%(head)s%(rows)s</div>

  <div class="routine"><span class="rtitle">⏰ 每天固定作息</span>%(routine)s</div>

  <div class="notes">
    <div class="note note--warn">
      <h3>⚠️ 第9节 —— 需要问清楚</h3>
      <p>课表排到第9节，但作息表上没有「第9节」，只有 <b>课外活动 16:05—17:05</b>（60分钟，其他节次都是40分钟）。
         白天能对上的只有这一格，<b>实际几点上、上多久，建议跟班主任 / 教务确认一次</b>。
         涉及：<b>周二 128班</b> ／ <b>周四 129班</b>。</p>
    </div>
    <div class="note">
      <h3>📌 小提醒</h3>
      <ul>
        <li><b>周二、周四连堂</b>，第8节下课到第9节只隔 10 分钟</li>
        <li>两天<b>换班顺序相反</b>：周二 129→128，周四 128→129</li>
        <li>周一 第6节全校会议，不上课</li>
      </ul>
    </div>
    <div class="note">
      <h3>📖 早自修（全校统一）</h3>
      <ul>
        <li>周一 · 周三 · 周五 → <b>英语</b></li>
        <li>周二 · 周四 → <b>语文</b></li>
        <li>早读 6:30—7:00　早自修 7:00—7:25</li>
      </ul>
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
        )
        path = os.path.join(OUT, f"tt_wide_{key}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", path)

    with open(os.path.join(OUT, "themes_wide.json"), "w", encoding="utf-8") as f:
        json.dump(WIDE_FILES, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
