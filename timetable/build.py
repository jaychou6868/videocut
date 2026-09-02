# -*- coding: utf-8 -*-
"""生成三个主题的个人政治课表 HTML（随后用 Chromium 截成 PNG）

版式：周一~周五 为列，作息时间点为行；只标政治课，其余学科隐藏。
"""
import os, json, base64

OUT = os.path.dirname(os.path.abspath(__file__))

TITLE = "玥y的政治课表"
SUBTITLE = "2026 学年第一学期 · 任教 125 / 128 / 129 班　·　虚线框＝邱老师的课"
SIGN = "凯凯"

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
    dict(t="16:10—16:50",  name="第9节",       kind="class", p=9),
    dict(t="16:50",        name="晚餐",        kind="meal",  icon="🍜"),
    dict(t="17:40—18:00",  name="课前活动",    kind="rest",  icon="🚶"),
    dict(t="18:00—18:30",  name="听力",        kind="rest",  icon="🎧"),
    dict(t="18:30—19:20",  name="晚一",        kind="night", icon="🌙", p=10, label="晚一"),
    dict(t="19:30—20:20",  name="晚二",        kind="night", icon="🌙"),
    dict(t="20:30—21:30",  name="晚三",        kind="night", icon="🌙"),
    dict(t="22:10",        name="就寝熄灯",    kind="night", icon="🛏️"),
]

PERIOD_TIME = {s["p"]: s["t"] for s in SCHEDULE if s.get("p")}
PERIOD_LABEL = {s["p"]: s.get("label", f'第{s["p"]}节') for s in SCHEDULE if s.get("p")}

# 我的政治课：(星期, 节次, 班级)
MY = [
    (1, 5, "125"),
    (2, 8, "129"), (2, 9, "128"),
    (3, 1, "125"), (3, 5, "129"),
    (4, 8, "128"), (4, 9, "129"),
    (5, 2, "125"), (5, 3, "128"),
]
# 邱老师的政治课：(星期, 节次, 班级)。不是我的课，用更深的紫色区分
QIU = [
    (1, 3, "130"), (1, 4, "126"),
    (2, 2, "126"), (2, 3, "127"),
    (3, 4, "126"),
    (4, 6, "127"), (4, 7, "130"),
]
# 固定值班：(星期, 节次) -> (主标, 副标)。跟上课一样排进表里，不单列
DUTY = {(4, 10): ("晚自修", "值班")}

DAYS = ["周一", "周二", "周三", "周四", "周五"]      # 周六周日无政治课，不入表
WARN_P = {s["p"] for s in SCHEDULE if s.get("warn") and s.get("p")}   # 待确认的节次
NOTE_CELL = {(1, 6): "全校会议"}                     # 非政治课，但影响作息的提示

def lesson_at(d, p):
    for (dd, pp, k) in MY:
        if dd == d and pp == p:
            return k
    return None

def item_at(d, p):
    """这一格要做什么：上课 -> 班级，值班 -> 值班。都算「要到场」"""
    k = lesson_at(d, p)
    if k:
        return dict(main=k, unit="班", sub="政治", duty=False)
    if (d, p) in DUTY:
        main, sub = DUTY[(d, p)]
        return dict(main=main, unit="", sub=sub, duty=True)
    for (dd, pp, k) in QIU:
        if dd == d and pp == p:
            return dict(main=k, unit="班", sub="", duty=False, qiu=True, pre="邱")
    return None

def day_items(d):
    """当天所有要到场的安排（我的课 + 值班），按节次先后排序；邱的课不算"""
    return [(p, it) for p in sorted(PERIOD_TIME)
            if (it := item_at(d, p)) and not it.get("qiu")]

def busy_periods():
    """任意一天有安排的节次，用于左侧时间栏高亮"""
    return {p for d in range(1, 6) for p, _ in day_items(d)}

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


def beaver_svg(c):
    return f'''
<svg viewBox="0 0 120 108" class="mascot" aria-hidden="true">
  <path d="M60 20 q3 -12 10 -16" fill="none" stroke="{c['ink']}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="26" cy="40" r="11" fill="{c['brand2']}" stroke="{c['ink']}" stroke-width="3"/>
  <circle cx="94" cy="40" r="11" fill="{c['brand2']}" stroke="{c['ink']}" stroke-width="3"/>
  <ellipse cx="60" cy="62" rx="42" ry="38" fill="{c['brand2']}" stroke="{c['ink']}" stroke-width="3"/>
  <circle cx="45" cy="54" r="5" fill="{c['ink']}"/>
  <circle cx="76" cy="54" r="5" fill="{c['ink']}"/>
  <ellipse cx="60" cy="70" rx="15" ry="12" fill="#4A1F3D"/>
  <ellipse cx="55" cy="66" rx="4" ry="3" fill="#fff" opacity=".35"/>
  <rect x="54" y="82" width="5.5" height="11" rx="2" fill="#fff" stroke="{c['ink']}" stroke-width="2"/>
  <rect x="60.5" y="82" width="5.5" height="11" rx="2" fill="#fff" stroke="{c['ink']}" stroke-width="2"/>
</svg>'''

# 淡紫配色：Loopy / 酷洛米 / 米菲 共用一套，放桌面不刺眼
LILAC = dict(
    brand="#8B79C0", brand2="#B3A2DE", accent="#F5A9C6", ink="#3B3348",
    qiu="#5A4A8C", qiu2="#8477BE", brandd="#6B57A6",
    bg="#F7F4FC", card="#FFFFFF", soft="#EFEAFA", line="#DFD6F1", dot="#E8E1F7",
    muted="#8B8296", warn="#D06D9E", warn2="#E99BC1", warnbg="#FBEFF5",
)

THEMES = {
    "kitty": dict(
        file="政治课表_Kitty版.png",
        brand="#E8455F", brand2="#FF7C9B", accent="#FFC93C", ink="#3A2B33",
        bg="#FFF3F6", card="#FFFFFF", soft="#FFE8EF", line="#F6D3DE", dot="#FADCE5",
        muted="#9A8791", warn="#F0862F", warn2="#FFA85C", warnbg="#FFF1E3",
        qiu="#9E2E48", qiu2="#D2647F", brandd="#C22A45",
        mascot=kitty_svg, deco="🎀 💗 🍓", hearts="🎀",
    ),
    "puppy": dict(
        file="政治课表_帕恰狗版.png",
        brand="#2E86DE", brand2="#63AEEF", accent="#FFD23F", ink="#25384D",
        bg="#EFF7FF", card="#FFFFFF", soft="#E1F0FF", line="#CCE4F8", dot="#D8EAFB",
        muted="#7E93A8", warn="#EF7C3C", warn2="#FFA36B", warnbg="#FFF0E6",
        qiu="#1B4F87", qiu2="#5A87C4", brandd="#1E63B4",
        mascot=puppy_svg, deco="☁️ 🐾 ⭐", hearts="🐾",
    ),
    "loopy": dict(
        file="政治课表_Loopy版.png", **LILAC,
        mascot=beaver_svg, deco="💜 🌸 ⭐", hearts="💜",
    ),
    # 酷洛米：淡紫为主，长时间放在桌面也不刺眼；值班用她身上的粉做区分色
    "kuromi": dict(
        file="政治课表_酷洛米版.png", **LILAC,
        mascot=bunny_svg, deco="💜 🖤 ⭐", hearts="💜",
    ),
    "bunny": dict(
        file="政治课表_米菲版.png", **LILAC,
        mascot=bunny_svg, deco="💜 🌼 ⭐", hearts="💜",
    ),
}

# ---------------- 自备贴纸 ----------------
# 把图片放到 timetable/assets/ 下，命名 mascot_kitty.* / mascot_puppy.* / mascot_bunny.*
ASSETS = os.path.join(OUT, "assets")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}

def mascot_uri(key, plain=False):
    """角色图的 data URI，用于表格中央的背景水印。
    优先用 prep_assets.py 生成的压暗版 wm_*，白色部分才不会隐形。"""
    if not os.path.isdir(ASSETS):
        return None
    names = ((f"icon_{key}", f"mascot_{key}") if plain == "icon" else
             (f"mascot_{key}",) if plain else (f"wm_{key}", f"mascot_{key}"))
    for want in names:
      for fn in sorted(os.listdir(ASSETS)):
        stem, ext = os.path.splitext(fn)
        if stem.lower() == want and ext.lower() in MIME:
            data = base64.b64encode(open(os.path.join(ASSETS, fn), "rb").read()).decode()
            return f"data:{MIME[ext.lower()]};base64,{data}"
    return None


def icon_css(key):
    """自己的课前面那个小角色图标（邱老师的课用「邱」标签，两边不会混）"""
    uri = mascot_uri(key, plain="icon")
    if not uri:
        return ""
    return ("\n.ico{display:inline-block;flex:none;vertical-align:-2px;"
            f"background:url('{uri}') center center / contain no-repeat}}")


def watermark_css(key, size, top=0, bottom=0, left=0, opacity=.16):
    """表格中央的角色水印。top/bottom 让它避开表头（周几）和表尾那一行，
    在真正的空白区域居中，而不是在含表头的整块里居中。"""
    uri = mascot_uri(key)
    if not uri:
        return ""
    return ("\n.grid{position:relative}"
            "\n.grid>*{position:relative;z-index:1}"
            f"\n.grid:before{{content:'';position:absolute;top:{top}px;bottom:{bottom}px;left:{left}px;right:0;"
            "z-index:0;pointer-events:none;"
            f"opacity:{opacity};background:url('{uri}') center center / {size} auto no-repeat}}")


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
def _mins(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)

def day_span(items):
    """当天从第一项开始到最后一项结束的跨度，以及是否连堂（间隔≤15分钟）"""
    ps = [p for p, _ in items]
    first = PERIOD_TIME[ps[0]].split("—")[0]
    last = PERIOD_TIME[ps[-1]].split("—")[-1]
    back2back = any(_mins(PERIOD_TIME[b].split("—")[0]) -
                    _mins(PERIOD_TIME[a].split("—")[-1]) <= 15
                    for a, b in zip(ps, ps[1:]))
    return f"{first}—{last}", back2back

def build_glance():
    out = []
    for d in range(1, 6):
        ls = day_items(d)
        items = "".join(
            f'<div class="gl__i{" gl__i--duty" if it["duty"] else ""}">'
            f'<span class="gl__p">{PERIOD_LABEL[p]}</span>'
            f'<b>{it["main"]}<em>{it["unit"] or it["sub"]}</em></b>'
            f'<span class="gl__t">{PERIOD_TIME[p]}</span></div>'
            for p, it in ls)
        n_class = sum(1 for _, it in ls if not it["duty"])
        n_duty = len(ls) - n_class
        cnt = f"{n_class} 节" + ("　+ 值班" if n_duty else "")
        out.append(f'''
      <div class="gl">
        <div class="gl__d">{DAYS[d-1]}</div>
        <div class="gl__n">{cnt}</div>
        {items}
      </div>''')
    return "\n".join(out)

def build_grid():
    BUSY = busy_periods()
    cells = ['<div class="hd hd--t">时间</div>']
    cells += [f'<div class="hd"><span>{d}</span></div>' for d in DAYS]

    for s in SCHEDULE:
        p = s.get("p")
        if not p:                                   # 作息条（每天相同）
            sub = f'<span class="bd__s">{s["sub"]}</span>' if s.get("sub") else ""
            tag = f'<span class="tag">{s["tag"]}</span>' if s.get("tag") else ""
            cells.append(f'<div class="tc tc--soft"><i>{s["t"]}</i></div>')
            cells.append(f'<div class="bd bd--{s["kind"]}">'
                         f'<span class="bd__n">{s.get("icon","")} {s["name"]}</span>{sub}{tag}</div>')
            continue

        mine = p in BUSY
        warn = s.get("warn")
        tcls = "tc" + (" tc--mine" if mine else "") + (" tc--warn" if warn else "")
        badge = ""
        sub = f'<em>{s["sub"]}</em>' if s.get("sub") else ""
        cells.append(f'<div class="{tcls}"><b>{PERIOD_LABEL[p]}</b>{badge}<i>{s["t"]}</i>{sub}</div>')

        for d in range(1, 6):
            it = item_at(d, p)
            note = NOTE_CELL.get((d, p))
            last = " c--last" if d == 5 else ""
            if it:
                chip = "pill" + (" pill--duty" if it["duty"] else
                                 " pill--qiu" if it.get("qiu") else "")
                pre = (f'<span class="pill__pre">{it["pre"]}</span>' if it.get("pre")
                       else '' if it["duty"] else '<span class="ico"></span>')
                cells.append(f'<div class="c c--on{last}"><div class="{chip}">'
                             f'<span class="pill__k">{pre}{it["main"]}<em>{it["unit"] or it["sub"]}</em></span>'
                             f'<span class="pill__u">{PERIOD_TIME[p]}</span></div></div>')
            elif note:
                cells.append(f'<div class="c c--note{last}"><span>{note}</span></div>')
            else:
                cells.append(f'<div class="c{last}"><span class="c__dot"></span></div>')
    return "\n      ".join(cells)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{color:var(--ink);background-color:var(--bg);
     background-image:radial-gradient(var(--dot) 2px, transparent 2.1px);
     background-size:26px 26px;
     font-family:'Noto Sans SC','WenQuanYi Zen Hei',sans-serif;-webkit-font-smoothing:antialiased}
.page{width:1080px;padding:36px 30px 40px}
h1,h2,.hd span,.gl__d,.sign b{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
.pill__k,.tc i,.gl__i span{font-family:'Fredoka','Noto Sans SC',sans-serif;font-variant-numeric:tabular-nums}

/* ---------- 头部 ---------- */
.hero{position:relative;border-radius:34px;padding:24px 30px;display:flex;align-items:center;gap:24px;
      overflow:hidden;background:var(--card);border:4px solid var(--ink);
      box-shadow:0 10px 0 var(--brand),0 10px 26px rgba(0,0,0,.10)}
.hero:before{content:"";position:absolute;right:-70px;top:-90px;width:340px;height:340px;
             border-radius:50%;background:linear-gradient(150deg,var(--soft),transparent 70%);z-index:0}
.hero:after{content:"";position:absolute;left:-50px;bottom:-90px;width:220px;height:220px;
            border-radius:50%;background:var(--soft);opacity:.6;z-index:0}
.hero>*{position:relative;z-index:1}
.mascot{width:150px;height:140px;flex:none}
.mascot--img{width:180px;height:180px;object-fit:contain;
             filter:drop-shadow(0 6px 9px rgba(0,0,0,.15))}
h1{font-size:52px;line-height:1.12;letter-spacing:1px}
h1 small{display:block;font-size:18px;color:var(--muted);margin-top:8px;letter-spacing:0;
         font-family:'Noto Sans SC',sans-serif}
.stats{display:flex;gap:9px;margin-top:15px;flex-wrap:wrap;max-width:640px}
.stat{background:var(--soft);border:2.5px solid var(--ink);border-radius:999px;
      padding:6px 15px;font-size:18px;font-weight:700}
.stat b{font-family:'Fredoka',sans-serif;color:var(--brand);font-size:21px}
.deco{position:absolute;right:26px;top:18px;font-size:21px;letter-spacing:5px;opacity:.8}
.by{position:absolute;right:26px;bottom:18px;font-size:16px;font-weight:700;color:var(--brand);
    background:var(--soft);border:2px solid var(--brand);border-radius:999px;padding:3px 13px}

/* ---------- 速览 ---------- */
.glance{display:grid;grid-template-columns:repeat(5,1fr);gap:13px;margin-top:22px}
.gl{background:var(--card);border:3px solid var(--ink);border-radius:22px;padding:0 10px 12px;
    text-align:center;box-shadow:0 6px 0 var(--line);overflow:hidden;
    display:flex;flex-direction:column}
.gl__d{font-size:26px;color:#fff;line-height:1.35;margin:0 -10px;
       background:linear-gradient(135deg,var(--brand),var(--brand2))}
.gl__n{font-size:13.5px;color:var(--muted);font-weight:700;margin:7px 0 4px}
.gl__i{background:var(--soft);border-radius:14px;padding:7px 4px 8px;margin-top:7px}
.gl__p{display:block;font-size:13px;font-weight:800;color:var(--brand);letter-spacing:.5px}
.gl__t{display:block;font-size:16px;color:var(--ink);opacity:.72;font-weight:700;margin-top:2px;
       font-family:'Fredoka','Noto Sans SC',sans-serif}
.gl__sp{margin-top:auto;padding-top:11px;font-size:15px;font-weight:700;color:var(--ink);opacity:.66;
        font-family:'Fredoka','Noto Sans SC',sans-serif;white-space:nowrap}
.gl__b2b{display:inline-block;font-style:normal;font-size:12.5px;font-weight:800;color:#fff;
         background:var(--brand);border-radius:99px;padding:1px 8px;margin-left:5px;
         font-family:'Noto Sans SC',sans-serif}
.gl__i b{display:block;font-size:26px;font-family:'Fredoka',sans-serif;line-height:1.05;color:var(--ink)}
.gl__i b em{font-size:14px;font-style:normal;font-weight:700;margin-left:1px;
            font-family:'Noto Sans SC',sans-serif}
.gl__i--duty{background:var(--warnbg);outline:2.5px solid var(--warn);outline-offset:-2px}

/* ---------- 主表 ---------- */
.sec__hd{display:flex;align-items:center;gap:12px;margin:26px 0 14px}
h2{font-size:30px}
.sec__hd .kicker{font-size:16px;color:var(--muted);font-weight:700}
.sec__hd .bar{flex:1;height:6px;border-radius:99px;
              background:linear-gradient(90deg,var(--line),transparent)}
.grid{display:grid;grid-template-columns:236px repeat(5,1fr);
      background:var(--card);border:4px solid var(--ink);border-radius:28px;overflow:hidden;
      box-shadow:0 9px 0 var(--line),0 12px 30px rgba(0,0,0,.07)}
.hd{background:linear-gradient(135deg,var(--brand),var(--brand2));color:#fff;font-size:27px;
    text-align:center;padding:14px 0 12px}
.hd--t{font-size:19px;font-weight:700;background:var(--ink);color:#fff;
       display:flex;align-items:center;justify-content:center;
       font-family:'Noto Sans SC',sans-serif;letter-spacing:3px}
.tc{padding:11px 8px 11px 18px;border-bottom:2px solid var(--line);border-right:2px solid var(--line)}
.tc b{display:block;font-size:23px;font-weight:800;line-height:1.2}
.tc i{display:block;font-style:normal;font-size:22px;color:var(--ink);opacity:.78;
      font-weight:700;margin-top:3px;letter-spacing:.3px}
.tc em{display:block;font-style:normal;font-size:12.5px;color:var(--muted);margin-top:3px;line-height:1.35}
.tc--soft{display:flex;align-items:center;background:color-mix(in srgb,var(--bg) 76%,transparent)}
.tc--soft i{font-size:20px;margin:0;opacity:.7;font-weight:700}
.tc--mine{background:color-mix(in srgb,var(--soft) 76%,transparent);box-shadow:inset 7px 0 0 var(--brand)}
.tc--mine b{color:var(--brand)}
.tc--warn{background:color-mix(in srgb,var(--warnbg) 76%,transparent);box-shadow:inset 7px 0 0 var(--warn)}
.tc--warn b{color:var(--warn)}
.tag{display:inline-block;font-size:12px;font-weight:800;border-radius:99px;padding:1px 8px;
     border:2px solid var(--line);color:var(--muted);margin-left:3px;vertical-align:2px}
.tag--warn{background:var(--warn);color:#fff;border-color:var(--warn)}
.c{border-bottom:2px solid var(--line);border-right:2px solid var(--line);min-height:78px;
   display:flex;align-items:center;justify-content:center;padding:7px 8px}
.c--last{border-right:none}
.c__dot{width:9px;height:9px;border-radius:50%;background:var(--line)}
.pill{width:100%;height:100%;border-radius:17px;display:flex;flex-direction:column;
      align-items:center;justify-content:center;gap:1px;color:#fff;
      background:linear-gradient(150deg,var(--brand),var(--brandd));
      box-shadow:0 4px 0 rgba(0,0,0,.13),0 5px 12px rgba(0,0,0,.14)}
.pill--duty{background:linear-gradient(150deg,var(--warn2),var(--warn))}
/* 邱老师的课：空心虚线牌子 + 深色字，和自己的实心牌子在「形状」上就分开 */
.pill--qiu{background:color-mix(in srgb,var(--qiu) 7%,#fff);color:var(--qiu);
           border:3px dashed color-mix(in srgb,var(--qiu) 45%,#fff);box-shadow:none}
.pill--qiu .pill__u{opacity:.8}
.pill__pre{display:inline-block;background:color-mix(in srgb,var(--qiu) 78%,#fff);
           color:#fff;border-radius:7px;
           font-size:17px;font-weight:800;padding:1px 7px;margin-right:5px;vertical-align:2px;
           font-family:'Noto Sans SC',sans-serif}
.pill__k{font-size:31px;font-weight:800;line-height:1.05;letter-spacing:.5px;
         display:flex;align-items:center;justify-content:center;gap:5px}
.pill .ico{width:26px;height:26px}
.pill__k em{font-size:16px;font-style:normal;font-weight:700;margin-left:2px;
            font-family:'Noto Sans SC',sans-serif}
.pill__u{font-size:15px;font-weight:700;opacity:.95;letter-spacing:.2px;margin-top:2px;
         font-family:'Fredoka','Noto Sans SC',sans-serif}
.c--note{background:color-mix(in srgb,var(--bg) 76%,transparent)}
.c--note span{font-size:14.5px;color:var(--ink);font-weight:700;opacity:.8;
              background:var(--soft);border-radius:12px;padding:6px 12px}
.bd{grid-column:2 / -1;border-bottom:2px solid var(--line);background:color-mix(in srgb,var(--bg) 76%,transparent);
    display:flex;align-items:center;gap:10px;padding:9px 18px;min-height:50px}
.bd__n{font-size:20px;font-weight:700;color:var(--ink);opacity:.72}
.bd__s{font-size:15px;color:var(--muted);opacity:.85}
.bd--night{opacity:.8}
.bd--meal .bd__n{color:var(--ink);opacity:.8}

/* ---------- 说明 ---------- */
.notes{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:20px}
.note{background:var(--card);border:3px solid var(--ink);border-radius:24px;padding:16px 20px;
      box-shadow:0 6px 0 var(--line)}
.note--warn{background:var(--warnbg);border-color:var(--warn);box-shadow:0 6px 0 var(--warn)}
.note h3{font-size:22px;margin-bottom:8px}
.note li,.note p{font-size:17px;line-height:1.7;font-weight:500}
.note ul{margin-left:20px}
.note b{color:var(--warn)}
.notes{display:block;margin-top:20px}
.note--sr{display:flex;align-items:center;gap:26px}
.note--sr h3{margin:0;white-space:nowrap}
.note--sr .sr{flex:1;margin:0}
.note--sr .sr__t{margin:0;white-space:nowrap}
.sr{display:flex;gap:12px;margin-top:4px}
.sr__i{flex:1;background:var(--soft);border:2.5px solid var(--ink);border-radius:16px;
       padding:9px 8px 10px;text-align:center}
.sr__d{display:block;font-size:14px;color:var(--muted);font-weight:700;margin-bottom:2px}
.sr__i b{font-size:26px;color:var(--brand);
         font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
.sr__i--b b{color:var(--warn)}
.sr__t{margin-top:10px;text-align:center;font-size:15px;font-weight:700;color:var(--ink);opacity:.7}


/* ---------- 署名 ---------- */
.sign{display:flex;align-items:center;justify-content:center;gap:14px;margin-top:30px}
.sign__l{height:3px;width:120px;border-radius:99px;background:var(--line)}
.sign__p{background:var(--card);border:2.5px solid var(--brand);border-radius:999px;
         padding:8px 22px;font-size:17px;font-weight:700;color:var(--muted);
         box-shadow:0 4px 0 var(--soft)}
.sign b{font-size:22px;color:var(--brand);margin:0 4px}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<style>:root{--brand:%(brand)s;--brand2:%(brand2)s;--accent:%(accent)s;--ink:%(ink)s;--bg:%(bg)s;
--card:%(card)s;--soft:%(soft)s;--line:%(line)s;--dot:%(dot)s;--muted:%(muted)s;
--warn:%(warn)s;--warn2:%(warn2)s;--warnbg:%(warnbg)s;--qiu:%(qiu)s;--qiu2:%(qiu2)s;
--brandd:%(brandd)s;}
%(css)s%(wm)s</style></head><body><div class="page">

  <div class="hero">
    %(mascot)s
    <div class="hero__txt">
      <h1>%(title)s<small>%(subtitle)s</small></h1>
      <div class="stats">
        <span class="stat">每周 <b>9</b> 节</span>
        <span class="stat">周一到周五 <b>每周相同</b></span>
        <span class="stat">最早 <b>7:40</b> 上课</span>
      </div>
    </div>
    <div class="by">%(sign)s 制</div>
  </div>

  <div class="glance">%(glance)s</div>

  <div class="sec__hd"><h2>作息 × 政治课</h2>
    <span class="kicker">实心＝我的课　虚线＝邱老师　小圆点＝没课</span><span class="bar"></span></div>
  <div class="grid">
      %(grid)s
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
        qiu=c["qiu"], qiu2=c["qiu2"], brandd=c["brandd"],
        mascot=(user_mascot(key) or c["mascot"](c)), deco=c["deco"], hearts=c["hearts"],
        title=TITLE, subtitle=SUBTITLE, sign=SIGN,
        glance=build_glance(), grid=build_grid(), wm=watermark_css(key, '640px', top=56, left=236) + icon_css(key),
    )
    path = os.path.join(OUT, f"tt_{key}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)

  with open(os.path.join(OUT, "themes.json"), "w", encoding="utf-8") as f:
    json.dump({k: v["file"] for k, v in THEMES.items()}, f, ensure_ascii=False)
  print("总课数:", len(MY))

if __name__ == "__main__":
    main()
