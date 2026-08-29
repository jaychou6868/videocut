# -*- coding: utf-8 -*-
"""生成三个主题的个人政治课表 HTML（随后用 Chromium 截成 PNG）"""
import os, json

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------- 数据 ----------------
# 作息表（萧山三中作息时间表）。kind: rest / class / meal / night
# p = 节次编号（与课表行号对应）
SCHEDULE = [
    dict(t="6:10",         name="起床 · 早餐",  kind="rest",  icon="☀️"),
    dict(t="6:30—7:00",    name="早读",        kind="rest",  icon="📖"),
    dict(t="7:00—7:25",    name="早自修",      kind="rest",  icon="✏️", sub="周一三五 英语 · 周二四六 语文"),
    dict(t="7:25—7:40",    name="课间活动",    kind="rest",  icon="🤸", tag="推算"),
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
    dict(t="13:35—14:15",  name="第6节",       kind="class", p=6, sub="周一为全校会议，不上课"),
    dict(t="14:25—15:05",  name="第7节",       kind="class", p=7),
    dict(t="15:15—15:55",  name="第8节",       kind="class", p=8),
    dict(t="16:05—17:05",  name="课外活动（第9节）", kind="class", p=9, warn=True,
         sub="作息表上叫「课外活动」，整整 60 分钟，和其他 40 分钟的课不一样"),
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
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六"]

def day_lessons(d):
    return sorted([m for m in MY if m[0] == d], key=lambda m: m[1])

def period_owners(p):
    return sorted([m for m in MY if m[1] == p], key=lambda m: m[0])

# ---------------- 主题 ----------------
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
  <ellipse cx="30" cy="76" rx="7" ry="4.5" fill="{c['blush']}" opacity=".9"/>
  <ellipse cx="90" cy="76" rx="7" ry="4.5" fill="{c['blush']}" opacity=".9"/>
</svg>'''

def puppy_svg(c):
    return f'''
<svg viewBox="0 0 120 108" class="mascot" aria-hidden="true">
  <ellipse cx="24" cy="52" rx="16" ry="26" fill="{c['brand']}" stroke="{c['ink']}" stroke-width="3"/>
  <ellipse cx="96" cy="52" rx="16" ry="26" fill="{c['brand']}" stroke="{c['ink']}" stroke-width="3"/>
  <circle cx="60" cy="58" r="42" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <circle cx="45" cy="52" r="5.5" fill="{c['ink']}"/>
  <circle cx="75" cy="52" r="5.5" fill="{c['ink']}"/>
  <circle cx="46.8" cy="50" r="1.8" fill="#fff"/><circle cx="76.8" cy="50" r="1.8" fill="#fff"/>
  <ellipse cx="60" cy="68" rx="7" ry="5.5" fill="{c['ink']}"/>
  <path d="M60 74 v6 M60 80 q-9 0 -11 -6 M60 80 q9 0 11 -6" fill="none" stroke="{c['ink']}" stroke-width="2.8" stroke-linecap="round"/>
  <path d="M52 82 q8 12 16 0 z" fill="{c['blush']}" stroke="{c['ink']}" stroke-width="2" stroke-linejoin="round"/>
  <ellipse cx="32" cy="68" rx="7" ry="4.5" fill="{c['blush']}" opacity=".85"/>
  <ellipse cx="88" cy="68" rx="7" ry="4.5" fill="{c['blush']}" opacity=".85"/>
</svg>'''

def bunny_svg(c):
    return f'''
<svg viewBox="0 0 120 108" class="mascot" aria-hidden="true">
  <ellipse cx="42" cy="26" rx="12" ry="26" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <ellipse cx="78" cy="26" rx="12" ry="26" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <ellipse cx="42" cy="26" rx="5" ry="17" fill="{c['blush']}" opacity=".7"/>
  <ellipse cx="78" cy="26" rx="5" ry="17" fill="{c['blush']}" opacity=".7"/>
  <ellipse cx="60" cy="72" rx="40" ry="32" fill="#fff" stroke="{c['ink']}" stroke-width="3"/>
  <circle cx="46" cy="68" r="4.6" fill="{c['ink']}"/>
  <circle cx="74" cy="68" r="4.6" fill="{c['ink']}"/>
  <path d="M55 82 q5 6 10 0" fill="none" stroke="{c['ink']}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="60" cy="78" r="2.6" fill="{c['brand']}"/>
  <ellipse cx="33" cy="80" rx="7" ry="4.5" fill="{c['blush']}" opacity=".9"/>
  <ellipse cx="87" cy="80" rx="7" ry="4.5" fill="{c['blush']}" opacity=".9"/>
</svg>'''

THEMES = {
    "kitty": dict(
        file="政治课表_小猫版.png", label="小猫咪 · 红白粉",
        brand="#E8455F", brand2="#FF89A9", accent="#FFC93C", ink="#3A2B33",
        blush="#FFB7C9", bg="#FFF3F6", card="#FFFFFF", soft="#FFE8EF",
        line="#F6D3DE", muted="#9A8791", warn="#F27E2C", warnbg="#FFF1E3",
        mascot=kitty_svg, deco=["🎀", "💗", "🐾", "🍓"],
    ),
    "puppy": dict(
        file="政治课表_小狗版.png", label="帕恰狗风 · 蓝白",
        brand="#2E86DE", brand2="#6FB6F2", accent="#FFD23F", ink="#25384D",
        blush="#FFC0CB", bg="#EFF7FF", card="#FFFFFF", soft="#E1F0FF",
        line="#CCE4F8", muted="#7E93A8", warn="#EF7C3C", warnbg="#FFF0E6",
        mascot=puppy_svg, deco=["⚽", "☁️", "🐾", "⭐"],
    ),
    "bunny": dict(
        file="政治课表_小兔版.png", label="米菲风 · 橙蓝",
        brand="#F08A24", brand2="#FFB45C", accent="#2C6FBB", ink="#33302B",
        blush="#FFC9A3", bg="#FFF8EC", card="#FFFFFF", soft="#FFF0D8",
        line="#F2DFC0", muted="#9B8E7A", warn="#D2542C", warnbg="#FDEDE6",
        mascot=bunny_svg, deco=["🥕", "🌼", "🧡", "⭐"],
    ),
}

# ---------------- HTML 片段 ----------------
def build_week_cards(c):
    html = []
    for d in range(1, 7):
        ls = day_lessons(d)
        head_extra = "" if ls else " day--off"
        rows = []
        if ls:
            for (_, p, k) in ls:
                nine = " lesson--nine" if p == 9 else ""
                mark = '<span class="nine-mark">待确认</span>' if p == 9 else ""
                rows.append(f'''
        <div class="lesson{nine}">
          <span class="lesson__p">第{p}节</span>
          <span class="lesson__k">{k}<em>班</em></span>
          <span class="lesson__t">{PERIOD_TIME[p]}{mark}</span>
        </div>''')
        else:
            rows.append('<div class="lesson lesson--none">没有政治课 ☕<br><small>好好休息一下</small></div>')
        cnt = f'{len(ls)} 节' if ls else '休息'
        html.append(f'''
      <div class="day{head_extra}">
        <div class="day__hd"><span class="day__n">{DAYS[d-1]}</span><span class="day__c">{cnt}</span></div>
        {''.join(rows)}
      </div>''')
    return "\n".join(html)

def build_timeline(c):
    rows = []
    for s in SCHEDULE:
        p = s.get("p")
        owners = period_owners(p) if p else []
        mine = bool(owners)
        cls = ["tl"]
        cls.append("tl--" + s["kind"])
        if mine:
            cls.append("tl--mine")
        if s.get("warn"):
            cls.append("tl--warn")
        chips = ""
        if mine:
            chips = "".join(
                f'<span class="chip{" chip--nine" if p==9 else ""}">{DAYS[d-1]} · {k}班</span>'
                for (d, _, k) in owners)
        elif p:
            chips = '<span class="chip chip--free">空</span>'
        sub = f'<div class="tl__sub">{s["sub"]}</div>' if s.get("sub") else ""
        tag = f'<span class="tl__tag">{s["tag"]}</span>' if s.get("tag") else ""
        icon = s.get("icon", "")
        icon_html = f'<span class="tl__icon">{icon}</span>' if icon else ""
        rows.append(f'''
      <div class="{' '.join(cls)}">
        <div class="tl__time">{s["t"]}</div>
        <div class="tl__body">
          <div class="tl__name">{icon_html}{s["name"]}{tag}</div>
          {sub}
        </div>
        <div class="tl__chips">{chips}</div>
      </div>''')
    return "\n".join(rows)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);
     font-family:'Noto Sans SC','WenQuanYi Zen Hei',sans-serif;
     -webkit-font-smoothing:antialiased}
.page{width:1080px;padding:38px 34px 44px}
.num,.tl__time,.lesson__t{font-family:'Fredoka','Noto Sans SC',sans-serif;font-variant-numeric:tabular-nums}
h1,h2,.day__n,.brandname{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}

/* ---------- header ---------- */
.hero{position:relative;background:var(--card);border:4px solid var(--ink);border-radius:34px;
      padding:30px 34px;display:flex;align-items:center;gap:26px;overflow:hidden;
      box-shadow:0 10px 0 var(--brand)}
.hero:before{content:"";position:absolute;inset:0;background:
   radial-gradient(circle at 88% 8%,var(--soft) 0 120px,transparent 121px),
   radial-gradient(circle at 12% 96%,var(--soft) 0 90px,transparent 91px);}
.hero>*{position:relative}
.mascot{width:150px;height:135px;flex:none}
.hero__txt{flex:1}
h1{font-size:52px;line-height:1.1;letter-spacing:1px}
h1 small{display:block;font-size:20px;color:var(--muted);letter-spacing:0;margin-top:8px;
         font-family:'Noto Sans SC',sans-serif}
.stats{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap;max-width:700px}
.stat{background:var(--soft);border:2.5px solid var(--ink);border-radius:999px;
      padding:7px 16px;font-size:19px;font-weight:700}
.stat b{font-family:'Fredoka',sans-serif;color:var(--brand);font-size:22px}
.deco{position:absolute;right:30px;top:16px;font-size:24px;letter-spacing:7px;opacity:.85}

/* ---------- section ---------- */
.sec{margin-top:34px}
.sec__hd{display:flex;align-items:center;gap:12px;margin-bottom:16px}
h2{font-size:33px}
.sec__hd .bar{flex:1;height:5px;border-radius:99px;background:var(--line)}
.sec__hd .kicker{font-size:17px;color:var(--muted);font-weight:700}

/* ---------- week cards ---------- */
.week{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.day{background:var(--card);border:3.5px solid var(--ink);border-radius:26px;padding:16px 16px 18px;
     box-shadow:0 7px 0 var(--line);min-height:236px}
.day__hd{display:flex;align-items:baseline;justify-content:space-between;
         border-bottom:3px dashed var(--line);padding-bottom:10px;margin-bottom:12px}
.day__n{font-size:31px;color:var(--brand)}
.day__c{font-size:16px;font-weight:700;color:var(--muted)}
.day--off{background:var(--soft);box-shadow:0 7px 0 var(--line)}
.day--off .day__n{color:var(--muted)}
.lesson{display:flex;flex-direction:column;gap:3px;background:var(--soft);
        border:2.5px solid var(--ink);border-radius:18px;padding:11px 13px;margin-bottom:10px}
.lesson__p{font-size:16px;font-weight:800;color:var(--brand);letter-spacing:.5px}
.lesson__k{font-size:33px;font-weight:900;line-height:1.05;font-family:'Fredoka','Noto Sans SC',sans-serif}
.lesson__k em{font-size:17px;font-style:normal;font-weight:700;margin-left:3px;
              font-family:'Noto Sans SC',sans-serif}
.lesson__t{font-size:20px;font-weight:700;color:var(--ink);opacity:.85}
.lesson--nine{background:var(--warnbg);border-style:dashed;border-color:var(--warn)}
.lesson--nine .lesson__p{color:var(--warn)}
.nine-mark{display:inline-block;margin-left:8px;background:var(--warn);color:#fff;font-size:14px;
           font-weight:800;border-radius:99px;padding:2px 9px;vertical-align:2px;
           font-family:'Noto Sans SC',sans-serif}
.lesson--none{background:transparent;border:3px dashed var(--line);color:var(--muted);
              text-align:center;font-size:21px;font-weight:700;padding:26px 10px;line-height:1.5}
.lesson--none small{font-size:15px;font-weight:400}

/* ---------- timeline ---------- */
.tlwrap{background:var(--card);border:3.5px solid var(--ink);border-radius:28px;
        padding:12px 18px;box-shadow:0 8px 0 var(--line)}
.tl{display:grid;grid-template-columns:172px 1fr auto;align-items:center;gap:14px;
    padding:11px 10px;border-bottom:2px dashed var(--line);border-radius:14px}
.tl:last-child{border-bottom:none}
.tl__time{font-size:21px;font-weight:600;color:var(--muted);white-space:nowrap}
.tl__name{font-size:23px;font-weight:700;display:flex;align-items:center;gap:8px}
.tl__icon{font-size:20px}
.tl__sub{font-size:15px;color:var(--muted);margin-top:3px;font-weight:500}
.tl__tag{font-size:13px;font-weight:700;color:var(--muted);border:2px solid var(--line);
         border-radius:99px;padding:1px 8px}
.tl__chips{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end;max-width:400px}
.chip{background:var(--brand);color:#fff;font-size:18px;font-weight:800;border-radius:99px;
      padding:5px 14px;white-space:nowrap;border:2.5px solid var(--ink)}
.chip--nine{background:var(--warn)}
.chip--free{background:transparent;color:var(--muted);border:2px dashed var(--line);font-weight:600;font-size:15px}
.tl--rest .tl__name,.tl--night .tl__name,.tl--meal .tl__name{font-weight:600;color:var(--muted)}
.tl--rest .tl__time,.tl--night .tl__time,.tl--meal .tl__time{opacity:.75}
.tl--mine{background:var(--soft);border:3px solid var(--ink);border-bottom:3px solid var(--ink);
          box-shadow:0 4px 0 var(--line);margin:8px 0}
.tl--mine .tl__name{font-size:26px;font-weight:900;color:var(--ink)}
.tl--mine .tl__time{color:var(--ink);font-weight:700}
.tl--warn{background:var(--warnbg);border:3px dashed var(--warn)}

/* ---------- notes ---------- */
.notes{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:18px}
.note{background:var(--card);border:3px solid var(--ink);border-radius:24px;padding:18px 20px;
      box-shadow:0 6px 0 var(--line)}
.note--warn{background:var(--warnbg);border-color:var(--warn);box-shadow:0 6px 0 var(--warn);
            grid-column:1/-1}
.note h3{font-size:23px;margin-bottom:9px;display:flex;align-items:center;gap:8px}
.note ul{margin-left:20px}
.note li{font-size:18px;line-height:1.75;font-weight:500}
.note li b{color:var(--warn)}
.note p{font-size:18px;line-height:1.75;font-weight:500}
.foot{margin-top:26px;text-align:center;font-size:16px;color:var(--muted);font-weight:600}
.foot span{margin:0 8px}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<style>:root{--brand:%(brand)s;--brand2:%(brand2)s;--accent:%(accent)s;--ink:%(ink)s;
--blush:%(blush)s;--bg:%(bg)s;--card:%(card)s;--soft:%(soft)s;--line:%(line)s;
--muted:%(muted)s;--warn:%(warn)s;--warnbg:%(warnbg)s;}
%(css)s</style></head><body><div class="page">

  <div class="hero">
    %(mascot)s
    <div class="hero__txt">
      <h1>我的政治课表<small>2026 学年第一学期 · 民族团结班 · 任教 125 / 128 / 129 班</small></h1>
      <div class="stats">
        <span class="stat">每周 <b>9</b> 节</span>
        <span class="stat">最早 <b>7:40</b> 上课</span>
        <span class="stat">周六 <b>全天没课</b></span>
        <span class="stat">第9节 <b>2</b> 节待确认</span>
      </div>
    </div>
    <div class="deco">%(deco)s</div>
  </div>

  <div class="sec">
    <div class="sec__hd"><h2>📅 本周一览</h2><span class="kicker">今天上什么，一眼看完</span><span class="bar"></span></div>
    <div class="week">%(week)s</div>
  </div>

  <div class="sec">
    <div class="sec__hd"><h2>⏰ 每日作息 · 我的课在哪</h2><span class="kicker">作息每天相同，彩色格子＝我要上课</span><span class="bar"></span></div>
    <div class="tlwrap">%(timeline)s</div>
  </div>

  <div class="notes">
    <div class="note note--warn">
      <h3>⚠️ 关于「第9节」——需要问清楚</h3>
      <p>课表排到第9节，但作息表上没有「第9节」，只有 <b>课外活动 16:05—17:05</b>（60分钟，其他节次都是40分钟）。
      两处对得上的只有这一格，但<b>实际几点上、上多久还需要跟班主任 / 教务确认</b>。</p>
      <ul>
        <li>涉及我的课：<b>周二 第9节 128班</b> ／ <b>周四 第9节 129班</b></li>
        <li>另一种可能：作息表是旧版，学校已把这一小时正式拆成「第9节＋活动」</li>
      </ul>
    </div>
    <div class="note">
      <h3>📌 排课小提醒</h3>
      <ul>
        <li>周一 <b>第6节是全校会议</b>，全年级都不上课</li>
        <li>周三 第9节 = 班会 ／ 周五 有活动、心理课</li>
        <li>「课间活动」作息表上没写时间，此处按 7:25—7:40 推算</li>
      </ul>
    </div>
    <div class="note">
      <h3>📖 早自修安排（全校统一）</h3>
      <ul>
        <li>周一 · 周三 · 周五 → <b>英语</b></li>
        <li>周二 · 周四 · 周六 → <b>语文</b></li>
        <li>时间：7:00—7:25，早读 6:30—7:00</li>
      </ul>
    </div>
  </div>

  <div class="foot"><span>依据：民族团结班课表（8.25 版）＋ 萧山三中作息时间表</span><span>·</span><span>只显示政治课，其他学科已隐藏</span></div>
</div></body></html>"""

for key, c in THEMES.items():
    html = PAGE % dict(
        css=CSS, brand=c["brand"], brand2=c["brand2"], accent=c["accent"], ink=c["ink"],
        blush=c["blush"], bg=c["bg"], card=c["card"], soft=c["soft"], line=c["line"],
        muted=c["muted"], warn=c["warn"], warnbg=c["warnbg"],
        mascot=c["mascot"](c), deco="".join(c["deco"]),
        week=build_week_cards(c), timeline=build_timeline(c),
    )
    path = os.path.join(OUT, f"tt_{key}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)

with open(os.path.join(OUT, "themes.json"), "w", encoding="utf-8") as f:
    json.dump({k: v["file"] for k, v in THEMES.items()}, f, ensure_ascii=False)
print("总课数:", len(MY))
