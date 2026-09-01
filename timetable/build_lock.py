# -*- coding: utf-8 -*-
"""手机锁屏版：按手机屏幕比例（9:19.5）出图，顶部留给时钟、底部留给相机/手电筒按钮。

完整课表在锁屏上必然被遮挡，也小到读不清；锁屏真正需要的只有
「今天几点、去哪个班」，所以这一版只放五天速览，字放大。
"""
import os, json

from build import (OUT, TITLE, SIGN, PERIOD_TIME, PERIOD_LABEL, DAYS,
                   THEMES, day_items, user_mascot, mascot_uri)

LOCK_FILES = {k: v["file"].replace(".png", "_锁屏版.png") for k, v in THEMES.items()}

W, H = 1080, 2340          # 9:19.5，主流手机比例
CLOCK_ZONE = 600           # 顶部时钟/日期占用
BUTTON_ZONE = 300          # 底部两颗圆形按钮占用


def build_days():
    out = []
    for d in range(1, 6):
        items = "".join(
            f'<div class="it{" it--duty" if it["duty"] else ""}">'
            f'<span class="it__k">{it["main"]}<em>{it["unit"] or it["sub"]}</em></span>'
            f'<span class="it__t">{PERIOD_TIME[p]}</span>'
            f'<span class="it__p">{PERIOD_LABEL[p]}</span></div>'
            for p, it in day_items(d))
        out.append(f'<div class="day"><div class="day__d">{DAYS[d-1]}</div>'
                   f'<div class="day__l">{items}</div></div>')
    return "".join(out)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)spx;height:%(H)spx;overflow:hidden}
body{color:var(--ink);background-color:var(--bg);
     background-image:radial-gradient(var(--dot) 2.4px, transparent 2.5px);background-size:30px 30px;
     font-family:'Noto Sans SC','WenQuanYi Zen Hei',sans-serif;-webkit-font-smoothing:antialiased}
.page{width:%(W)spx;height:%(H)spx;padding:%(CLOCK)spx 42px %(BTN)spx;
      display:flex;flex-direction:column;justify-content:center;gap:18px;position:relative}

/* 角色放在时钟正下方那片空白里：那块本来就空着，也不会压到任何文字 */
.page:before{content:'';position:absolute;left:0;right:0;top:%(WMTOP)spx;height:%(WMH)spx;
             z-index:0;pointer-events:none;opacity:.3;
             background:url('%(WM)s') center center / 340px auto no-repeat}
.page>*{position:relative;z-index:1}

.hd{display:flex;align-items:center;gap:14px;margin-bottom:4px}
.hd img{width:74px;height:74px;object-fit:contain;flex:none;
        filter:drop-shadow(0 4px 6px rgba(0,0,0,.14))}
.hd__t{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-size:34px;line-height:1.15}
.hd__s{display:block;font-size:16px;color:var(--muted);font-weight:600;margin-top:3px;
       font-family:'Noto Sans SC',sans-serif}
.hd__by{margin-left:auto;background:var(--soft);border:2.5px solid var(--brand);border-radius:999px;
        padding:5px 15px;font-size:16px;font-weight:700;color:var(--brand);white-space:nowrap}

.day{display:flex;align-items:stretch;gap:14px;background:var(--card);
     border:3.5px solid var(--ink);border-radius:24px;padding:12px 14px;
     box-shadow:0 6px 0 var(--line)}
.day__d{flex:none;width:104px;display:flex;align-items:center;justify-content:center;
        font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-size:36px;color:var(--brand);
        background:var(--soft);border-radius:16px}
.day__l{flex:1;display:flex;gap:10px}
.it{flex:1;background:linear-gradient(150deg,var(--brand2),var(--brand));border-radius:18px;
    padding:11px 8px 12px;text-align:center;color:#fff;
    box-shadow:0 4px 0 rgba(0,0,0,.13)}
.it--duty{background:linear-gradient(150deg,var(--warn2),var(--warn))}
.it__k{display:block;font-size:38px;font-weight:800;line-height:1;
       font-family:'Fredoka','Noto Sans SC',sans-serif}
.it__k em{font-size:19px;font-style:normal;font-weight:700;margin-left:2px;
          font-family:'Noto Sans SC',sans-serif}
.it__t{display:block;font-size:22px;font-weight:700;margin-top:5px;opacity:.97;
       font-family:'Fredoka','Noto Sans SC',sans-serif}
.it__p{display:block;font-size:15px;font-weight:700;opacity:.85;margin-top:1px}
.day--off .day__l{align-items:center;color:var(--muted);font-size:20px;font-weight:700}

.foot{text-align:center;font-size:17px;font-weight:700;color:var(--muted);margin-top:6px}
.foot b{color:var(--brand);font-size:21px;margin:0 4px;
        font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<style>:root{--brand:%(brand)s;--brand2:%(brand2)s;--ink:%(ink)s;--bg:%(bg)s;--card:%(card)s;
--soft:%(soft)s;--line:%(line)s;--dot:%(dot)s;--muted:%(muted)s;
--warn:%(warn)s;--warn2:%(warn2)s;}
%(css)s</style></head><body><div class="page">
  <div class="hd">
    %(mascot)s
    <div class="hd__t">%(title)s<span class="hd__s">本周固定 · 每周相同</span></div>
    <span class="hd__by">%(sign)s 制</span>
  </div>
  %(days)s
  <div class="foot">%(hearts)s 这张课表是 <b>%(sign)s</b> 做的</div>
</div></body></html>"""


def main():
    for key, c in THEMES.items():
        uri = mascot_uri(key) or ""
        html = PAGE % dict(
            css=CSS % dict(W=W, H=H, CLOCK=CLOCK_ZONE, BTN=BUTTON_ZONE, WM=uri,
                           WMTOP=CLOCK_ZONE + 10, WMH=330),
            brand=c["brand"], brand2=c["brand2"], ink=c["ink"], bg=c["bg"], card=c["card"],
            soft=c["soft"], line=c["line"], dot=c["dot"], muted=c["muted"],
            warn=c["warn"], warn2=c["warn2"],
            mascot=(user_mascot(key) or ""), hearts=c["hearts"],
            title=TITLE, sign=SIGN, days=build_days(),
        )
        path = os.path.join(OUT, f"tt_lock_{key}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", path)

    with open(os.path.join(OUT, "themes_lock.json"), "w", encoding="utf-8") as f:
        json.dump(LOCK_FILES, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
