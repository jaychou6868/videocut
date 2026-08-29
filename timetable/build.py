# -*- coding: utf-8 -*-
"""生成三个主题的个人政治课表 HTML（随后用 Chromium 截成 PNG）

版式：周一~周五 为列，作息时间点为行；只标政治课，其余学科隐藏。
"""
import os, json, base64

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------- 数据 ----------------
# 作息表（萧山三中作息时间表）。kind: rest / class / meal / night
# p = 节次编号（与课表行号对应）
SCHEDULE = [
    dict(t="6:10",         name="起床 · 早餐",  kind="rest",  icon="☀️"),
    dict(t="6:30—7:00",    name="早读",        kind="rest",  icon="📖"),
    dict(t="7:00—7:25",    name="早自修",      kind="rest",  icon="✏️",
         sub="周一·周三·周五 英语　周二·周四 语文"),
    dict(t="7:25—7:40",    name="课间活动",    kind="rest",  icon="🤸", tag="时间推算"),
    dict(t="7:40—8:20",    name="第1节",       kind="class", p=1),
    dict(t="8:30—9:10",    name="第2节",       kind="class", p=2),
    dict(t="9:10—9:35",    name="课间操",      kind="rest",  icon="🏃"),
    dict(t="9:35—10:15",   name="第3节",       kind="class", p=3),
    dict(t="10:25—10:30",  name="眼保健操",    kind="rest",  icon="👀"),
    dict(t="10:30—11:10",  name="第4节",       kind="class", p=4),
    dict(t="11:20—12:00",  name="第5节",       kind="class", p=5),
    dict(t="12:00—12:35",  name="中餐",        kind="meal",  icon="🍚"),
    dict(t="12:35—13:15",  name="午休",        kind="rest",  icon="😴"),
    dict(t="13:25—13:35",  name="班班有歌声",  kind="rest",  icon="🎵"),
    dict(t="13:35—14:15",  name="第6节",       kind="class", p=6),
    dict(t="14:25—15:05",  name="第7节",       kind="class", p=7),
    dict(t="15:15—15:55",  name="第8节",       kind="class", p=8),
    dict(t="16:05—17:05",  name="第9节",       kind="class", p=9, warn=True,
         sub="作息表上叫「课外活动」，60分钟"),
    dict(t="17:05",        name="晚餐",        kind="meal",  icon="🍜"),
    dict(t="17:40—18:00",  name="课前活动",    kind="rest",  icon="🚶"),
    dict(t="18:00—18:30",  name="听力",        kind="rest",  icon="🎧"),
    dict(t="18:30—19:20",  name="晚一",        kind="night", icon="🌙"),
    dict(t="19:30—20:20",  name="晚二",        kind="night", icon="🌙"),
    dict(t="20:30—21:30",  name="晚三",        kind="night", icon="🌙"),
    dict(t="22:10",        name="就寝熄灯",    kind="night", icon="🛏️"),
]

PERIOD_TIME = {s["p"]: s["t"] for s in SCHEDULE if s.get("p")}

# 我的政治课：(星期, 节次, 班级)
MY = [
    (1, 5, "125"),
    (2, 8, "129"), (2, 9, "128"),
    (3, 1, "125"), (3, 5, "129"),
    (4, 8, "128"), (4, 9, "129"),
    (5, 2, "125"), (5, 3, "128"),
]
DAYS = ["周一", "周二", "周三", "周四", "周五"]      # 周六周日无政治课，不入表
NOTE_CELL = {(1, 6): "全校会议"}                     # 非政治课，但影响作息的提示

def lesson_at(d, p):
    for (dd, pp, k) in MY:
        if dd == d and pp == p:
            return k
    return None

def day_lessons(d):
    return sorted([m for m in MY if m[0] == d], key=lambda m: m[1])

# ---------------- 手绘形象（无自备素材时的兜底） ----------------
def kitty_svg(c):
    return f'''
<svg viewBox="0 0 120 108" class="mascot" aria-hidden="true">
  <ellipse cx="60" cy="64" rx="46" ry="38" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <path d="M20 40 L16 10 L48 30 Z" fill="#fff" stroke="{c['ink']}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M100 40 L104 10 L72 30 Z" fill="#fff" stroke="{c['ink']}" stroke-width="3" stroke-linejoin="round"/>
  <g fill="{c['brand']}">
    <circle cx="103" cy="26" r="10"/>
    <path d="M103 26 L88 14 L88 38 Z"/><path d="M103 26 L118 14 L118 38 Z"/>
    <circle cx="103" cy="26" r="4" fill="#fff" opacity=".85"/>
  </g>
  <ellipse cx="44" cy="62" rx="4.6" ry="6" fill="{c['ink']}"/>
  <ellipse cx="76" cy="62" rx="4.6" ry="6" fill="{c['ink']}"/>
  <ellipse cx="60" cy="74" rx="6" ry="4.5" fill="{c['accent']}"/>
  <g stroke="{c['ink']}" stroke-width="2.6" stroke-linecap="round">
    <path d="M8 56h20"/><path d="M6 68h22"/><path d="M92 56h20"/><path d="M92 68h22"/>
  </g>
</svg>'''

def puppy_svg(c):
    return f'''
<svg viewBox="0 0 120 108" class="mascot" aria-hidden="true">
  <ellipse cx="24" cy="52" rx="16" ry="26" fill="{c['brand']}" stroke="{c['ink']}" stroke-width="3"/>
  <ellipse cx="96" cy="52" rx="16" ry="26" fill="{c['brand']}" stroke="{c['ink']}" stroke-width="3"/>
  <circle cx="60" cy="58" r="42" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <circle cx="45" cy="52" r="5.5" fill="{c['ink']}"/><circle cx="75" cy="52" r="5.5" fill="{c['ink']}"/>
  <ellipse cx="60" cy="68" rx="7" ry="5.5" fill="{c['ink']}"/>
</svg>'''

def bunny_svg(c):
    return f'''
<svg viewBox="0 0 120 108" class="mascot" aria-hidden="true">
  <ellipse cx="42" cy="26" rx="12" ry="26" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <ellipse cx="78" cy="26" rx="12" ry="26" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <ellipse cx="60" cy="72" rx="40" ry="32" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <circle cx="46" cy="68" r="4.6" fill="{c['ink']}"/><circle cx="74" cy="68" r="4.6" fill="{c['ink']}"/>
</svg>'''

THEMES = {
    "kitty": dict(
        file="政治课表_Kitty版.png",
        brand="#E8455F", accent="#FFC93C", ink="#3A2B33",
        bg="#FFF3F6", card="#FFFFFF", soft="#FFE8EF", line="#F6D3DE",
        muted="#9A8791", warn="#F27E2C", warnbg="#FFF1E3",
        mascot=kitty_svg, deco="🎀 💗 🍓",
    ),
    "puppy": dict(
        file="政治课表_帕恰狗版.png",
        brand="#2E86DE", accent="#FFD23F", ink="#25384D",
        bg="#EFF7FF", card="#FFFFFF", soft="#E1F0FF", line="#CCE4F8",
        muted="#7E93A8", warn="#EF7C3C", warnbg="#FFF0E6",
        mascot=puppy_svg, deco="☁️ 🐾 ⭐",
    ),
    "bunny": dict(
        file="政治课表_米菲版.png",
        brand="#E8532C", accent="#F5B700", ink="#25384D",
        bg="#FFF6EE", card="#FFFFFF", soft="#FFE9DC", line="#F5D9C7",
        muted="#94806F", warn="#2C6FBB", warnbg="#E8F1FB",
        mascot=bunny_svg, deco="🥕 🌼 ⭐",
    ),
}

# ---------------- 自备贴纸 ----------------
# 把图片放到 timetable/assets/ 下，命名 mascot_kitty.* / mascot_puppy.* / mascot_bunny.*
ASSETS = os.path.join(OUT, "assets")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}

def user_mascot(key):
    if not os.path.isdir(ASSETS):
        return None
    for fn in sorted(os.listdir(ASSETS)):
        stem, ext = os.path.splitext(fn)
        if stem.lower() == f"mascot_{key}" and ext.lower() in MIME:
            data = base64.b64encode(open(os.path.join(ASSETS, fn), "rb").read()).decode()
            print(f"  · {key} 使用自备素材 {fn}")
            return f'<img class="mascot mascot--img" src="data:{MIME[ext.lower()]};base64,{data}" alt="">'
    return None

# ---------------- HTML 片段 ----------------
def build_glance():
    out = []
    for d in range(1, 6):
        ls = day_lessons(d)
        items = "".join(
            f'<div class="gl__i{" gl__i--nine" if p == 9 else ""}">'
            f'<b>{k}</b><span>{PERIOD_TIME[p].split("—")[0]}</span></div>'
            for (_, p, k) in ls)
        out.append(f'''
      <div class="gl">
        <div class="gl__d">{DAYS[d-1]}</div>
        <div class="gl__n">{len(ls)} 节</div>
        {items}
      </div>''')
    return "\n".join(out)

def build_grid():
    cells = ['<div class="hd hd--t">时间</div>']
    cells += [f'<div class="hd">{d}</div>' for d in DAYS]

    for s in SCHEDULE:
        p = s.get("p")
        if not p:                                   # 作息条（每天相同）
            sub = f'<span class="bd__s">{s["sub"]}</span>' if s.get("sub") else ""
            tag = f'<span class="tag">{s["tag"]}</span>' if s.get("tag") else ""
            cells.append(f'<div class="tc tc--soft tc--{s["kind"]}"><i>{s["t"]}</i></div>')
            cells.append(f'<div class="bd bd--{s["kind"]}">'
                         f'<span class="bd__n">{s.get("icon","")} {s["name"]}</span>{sub}{tag}</div>')
            continue

        mine = any(m[1] == p for m in MY)
        warn = s.get("warn")
        tcls = "tc" + (" tc--mine" if mine else "") + (" tc--warn" if warn else "")
        badge = '<span class="tag tag--warn">待确认</span>' if warn else ""
        sub = f'<em>{s["sub"]}</em>' if s.get("sub") else ""
        cells.append(f'<div class="{tcls}"><b>{s["name"]}</b>{badge}<i>{s["t"]}</i>{sub}</div>')

        for d in range(1, 6):
            k = lesson_at(d, p)
            note = NOTE_CELL.get((d, p))
            last = " c--last" if d == 5 else ""
            if k:
                cls = "c c--on" + (" c--nine" if p == 9 else "") + last
                cells.append(f'<div class="{cls}"><span class="c__k">{k}</span>'
                             f'<span class="c__u">班 · 政治</span></div>')
            elif note:
                cells.append(f'<div class="c c--note{last}">{note}</div>')
            else:
                cells.append(f'<div class="c{last}"><span class="c__dot">·</span></div>')
    return "\n      ".join(cells)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);
     font-family:'Noto Sans SC','WenQuanYi Zen Hei',sans-serif;-webkit-font-smoothing:antialiased}
.page{width:1080px;padding:36px 30px 40px}
h1,h2,.hd,.gl__d{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
.c__k,.tc i,.gl__i span{font-family:'Fredoka','Noto Sans SC',sans-serif;font-variant-numeric:tabular-nums}

/* ---------- 头部 ---------- */
.hero{position:relative;background:var(--card);border:4px solid var(--ink);border-radius:32px;
      padding:22px 30px;display:flex;align-items:center;gap:24px;overflow:hidden;
      box-shadow:0 9px 0 var(--brand)}
.hero:before{content:"";position:absolute;right:-40px;top:-60px;width:300px;height:300px;
             border-radius:50%;background:var(--soft)}
.hero>*{position:relative}
.mascot{width:150px;height:140px;flex:none}
.mascot--img{width:172px;height:172px;object-fit:contain;
             filter:drop-shadow(0 5px 7px rgba(0,0,0,.13))}
h1{font-size:50px;line-height:1.1}
h1 small{display:block;font-size:19px;color:var(--muted);margin-top:7px;
         font-family:'Noto Sans SC',sans-serif}
.stats{display:flex;gap:9px;margin-top:14px;flex-wrap:wrap;max-width:660px}
.stat{background:var(--soft);border:2.5px solid var(--ink);border-radius:999px;
      padding:6px 15px;font-size:18px;font-weight:700}
.stat b{font-family:'Fredoka',sans-serif;color:var(--brand);font-size:21px}
.deco{position:absolute;right:26px;top:16px;font-size:22px;letter-spacing:4px;opacity:.85}

/* ---------- 速览 ---------- */
.glance{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:22px}
.gl{background:var(--card);border:3px solid var(--ink);border-radius:20px;padding:12px 10px 14px;
    text-align:center;box-shadow:0 5px 0 var(--line)}
.gl__d{font-size:26px;color:var(--brand);line-height:1.2}
.gl__n{font-size:14px;color:var(--muted);font-weight:700;margin-bottom:9px}
.gl__i{background:var(--soft);border-radius:12px;padding:5px 4px;margin-top:6px}
.gl__i b{display:block;font-size:25px;font-family:'Fredoka',sans-serif;line-height:1.1}
.gl__i span{display:block;font-size:15px;color:var(--muted);font-weight:700}
.gl__i--nine{background:var(--warnbg);outline:2px dashed var(--warn);outline-offset:-2px}

/* ---------- 主表 ---------- */
.sec__hd{display:flex;align-items:center;gap:12px;margin:26px 0 14px}
h2{font-size:30px}
.sec__hd .kicker{font-size:16px;color:var(--muted);font-weight:700}
.sec__hd .bar{flex:1;height:5px;border-radius:99px;background:var(--line)}
.grid{display:grid;grid-template-columns:212px repeat(5,1fr);
      background:var(--card);border:3.5px solid var(--ink);border-radius:26px;overflow:hidden;
      box-shadow:0 8px 0 var(--line)}
.hd{background:var(--ink);color:#fff;font-size:26px;text-align:center;padding:13px 0}
.hd--t{font-size:19px;background:var(--ink);opacity:.92}
.tc{padding:10px 8px 10px 16px;border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.tc b{display:block;font-size:22px;font-weight:800;line-height:1.2}
.tc i{display:block;font-style:normal;font-size:17px;color:var(--muted);font-weight:600;margin-top:2px}
.tc em{display:block;font-style:normal;font-size:12.5px;color:var(--muted);margin-top:3px;line-height:1.35}
.tc--soft{display:flex;align-items:center;background:var(--bg)}
.tc--soft i{font-size:16px;margin:0}
.tc--mine{background:var(--soft)}
.tc--mine b{color:var(--brand)}
.tc--warn{background:var(--warnbg)}
.tc--warn b{color:var(--warn)}
.tag{display:inline-block;font-size:12px;font-weight:800;border-radius:99px;padding:1px 8px;
     border:2px solid var(--line);color:var(--muted);margin-left:2px;vertical-align:2px}
.tag--warn{background:var(--warn);color:#fff;border-color:var(--warn)}
.c{border-bottom:2px solid var(--line);border-right:2px solid var(--line);
   min-height:74px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px}
.c--last{border-right:none}
.c__dot{color:var(--line);font-size:26px;line-height:1}
.c--on{background:var(--brand);color:#fff}
.c__k{font-size:32px;font-weight:800;line-height:1}
.c__u{font-size:13px;font-weight:700;opacity:.92}
.c--nine{background:var(--warn)}
.c--note{font-size:15px;color:var(--muted);font-weight:700;background:var(--bg)}
.bd{grid-column:2 / -1;border-bottom:2px solid var(--line);background:var(--bg);
    display:flex;align-items:center;gap:10px;padding:9px 18px;min-height:46px}
.bd__n{font-size:19px;font-weight:700;color:var(--muted)}
.bd__s{font-size:15px;color:var(--muted);opacity:.85}
.bd--night{background:var(--bg);opacity:.82}
.bd--meal .bd__n{color:var(--ink);opacity:.75}

/* ---------- 说明 ---------- */
.notes{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:20px}
.note{background:var(--card);border:3px solid var(--ink);border-radius:22px;padding:16px 20px;
      box-shadow:0 6px 0 var(--line)}
.note--warn{background:var(--warnbg);border-color:var(--warn);box-shadow:0 6px 0 var(--warn);
            grid-column:1/-1}
.note h3{font-size:22px;margin-bottom:8px}
.note li,.note p{font-size:17px;line-height:1.7;font-weight:500}
.note ul{margin-left:20px}
.note b{color:var(--warn)}
.foot{margin-top:22px;text-align:center;font-size:15px;color:var(--muted);font-weight:600}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<style>:root{--brand:%(brand)s;--accent:%(accent)s;--ink:%(ink)s;--bg:%(bg)s;--card:%(card)s;
--soft:%(soft)s;--line:%(line)s;--muted:%(muted)s;--warn:%(warn)s;--warnbg:%(warnbg)s;}
%(css)s</style></head><body><div class="page">

  <div class="hero">
    %(mascot)s
    <div class="hero__txt">
      <h1>我的政治课表<small>2026 学年第一学期 · 民族团结班 · 任教 125 / 128 / 129 班</small></h1>
      <div class="stats">
        <span class="stat">每周 <b>9</b> 节</span>
        <span class="stat">周一到周五 <b>每周相同</b></span>
        <span class="stat">最早 <b>7:40</b> 上课</span>
        <span class="stat">第9节 <b>2</b> 节待确认</span>
      </div>
    </div>
    <div class="deco">%(deco)s</div>
  </div>

  <div class="glance">%(glance)s</div>

  <div class="sec__hd"><h2>⏰ 作息 × 政治课</h2>
    <span class="kicker">彩色格子＝我要上课，灰点＝没我的课</span><span class="bar"></span></div>
  <div class="grid">
      %(grid)s
  </div>

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
        <li>周一 第6节是<b>全校会议</b>，全年级不上课</li>
        <li>「课间活动」作息表未标时间，按 7:25—7:40 推算</li>
      </ul>
    </div>
    <div class="note">
      <h3>📖 早自修（全校统一）</h3>
      <ul>
        <li>周一 · 周三 · 周五 → <b>英语</b>　　周二 · 周四 → <b>语文</b></li>
        <li>早读 6:30—7:00　早自修 7:00—7:25</li>
      </ul>
    </div>
  </div>

  <div class="foot">依据：民族团结班课表（8.25 版）＋ 萧山三中作息时间表　·　本学期每周相同　·　只显示政治课</div>
</div></body></html>"""

for key, c in THEMES.items():
    html = PAGE % dict(
        css=CSS, brand=c["brand"], accent=c["accent"], ink=c["ink"], bg=c["bg"], card=c["card"],
        soft=c["soft"], line=c["line"], muted=c["muted"], warn=c["warn"], warnbg=c["warnbg"],
        mascot=(user_mascot(key) or c["mascot"](c)), deco=c["deco"],
        glance=build_glance(), grid=build_grid(),
    )
    path = os.path.join(OUT, f"tt_{key}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)

with open(os.path.join(OUT, "themes.json"), "w", encoding="utf-8") as f:
    json.dump({k: v["file"] for k, v in THEMES.items()}, f, ensure_ascii=False)
print("总课数:", len(MY))
