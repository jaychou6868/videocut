import json, os, asyncio
from playwright.async_api import async_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
themes = json.load(open(os.path.join(OUT, "themes_wide.json"), encoding="utf-8"))

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        for key, fname in themes.items():
            await pg.goto("file://" + os.path.join(OUT, f"tt_wide_{key}.html"))
            await pg.wait_for_timeout(700)
            over = await pg.evaluate(
                "() => document.querySelector('.page').scrollHeight - 1080")
            # 说明框 overflow:hidden，文字被裁切时肉眼容易漏看，这里显式检查
            clipped = await pg.evaluate(
                "() => [...document.querySelectorAll('.note')]"
                "  .map((n,i) => n.scrollHeight > n.clientHeight + 1 ? i : -1)"
                "  .filter(i => i >= 0)")
            out = os.path.join(OUT, fname)
            await pg.screenshot(path=out)          # 只截视口 = 精确 16:9
            print(f"{fname} {os.path.getsize(out)//1024}KB  超出高度: {over}px  裁切的说明框: {clipped or '无'}")
        await b.close()

asyncio.run(main())
