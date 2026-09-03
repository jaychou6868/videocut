# -*- coding: utf-8 -*-
"""单独出一份邱老师的政治课表（126 / 127 / 130 班）。

复用同一套版式和配色，只把「谁的课」换掉：邱老师的课变成主角（实心牌子），
玥y 的课和她的晚自修值班都不出现。跑完记得再跑一次正常的 build，
把 tt_*.html 和 themes*.json 还原成玥y的版本。
"""
import build, build_wide, build_lock

TITLE = "邱老师的政治课表"
SUBTITLE = "2026 学年第一学期 · 任教 126 / 127 / 130 班"
LOCK_SUB = "任教 126 / 127 / 130 班"
FILES = {"kuromi": "政治课表_邱老师版.png"}

# 邱老师的课升为主角；玥y 的课与值班不进这张表
build.MY = list(build.QIU)
build.QIU = []
build.DUTY = {}
build.MY_PRE = "邱"          # 每张牌子都标出是邱老师的课

for m in (build, build_wide, build_lock):
    if hasattr(m, "TITLE"):
        m.TITLE = TITLE
    if hasattr(m, "SUBTITLE"):
        m.SUBTITLE = SUBTITLE
    if hasattr(m, "LOCK_SUB"):
        m.LOCK_SUB = LOCK_SUB

theme = {k: v for k, v in build.THEMES.items() if k == "kuromi"}
theme["kuromi"] = dict(theme["kuromi"], file=FILES["kuromi"])
build.THEMES = build_wide.THEMES = build_lock.THEMES = theme
build_wide.WIDE_FILES = {k: v.replace(".png", "_横版.png") for k, v in FILES.items()}
build_lock.LOCK_FILES = {k: v.replace(".png", "_锁屏版.png") for k, v in FILES.items()}

if __name__ == "__main__":
    build.main()
    build_wide.main()
    build_lock.main()
    print("邱老师版：", [(d, p, k) for (d, p, k) in build.MY])
