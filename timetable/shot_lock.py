import json, os, asyncio
from playwright.async_api import async_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
themes = json.load(open(os.path.join(OUT, "themes_lock.json"), encoding="utf-8"))

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page(viewport={"width": 1080, "height": 2340}, device_scale_factor=2)
        for key, fname in themes.items():
            await pg.goto("file://" + os.path.join(OUT, f"tt_lock_{key}.html"))
            await pg.wait_for_timeout(600)
            over = await pg.evaluate("() => document.querySelector('.page').scrollHeight - 2340")
            # .grid 是 overflow:hidden，内容超出会被悄悄裁掉，必须单独查
            cut = await pg.evaluate(
                "() => {const g=document.querySelector('.grid');"
                " return g.scrollHeight - Math.round(g.getBoundingClientRect().height);}")
            out = os.path.join(OUT, fname)
            await pg.screenshot(path=out)
            print(f"{fname} {os.path.getsize(out)//1024}KB  页面超出: {over}px  表格被裁: {cut}px")
        await b.close()

asyncio.run(main())
