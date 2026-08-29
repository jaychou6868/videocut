import json, os, asyncio
from playwright.async_api import async_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
DEST = "/home/user/videocut/timetable"
os.makedirs(DEST, exist_ok=True)
themes = json.load(open(os.path.join(OUT, "themes.json"), encoding="utf-8"))

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page(viewport={"width": 1080, "height": 1400}, device_scale_factor=2)
        for key, fname in themes.items():
            await pg.goto("file://" + os.path.join(OUT, f"tt_{key}.html"))
            await pg.wait_for_timeout(700)
            out = os.path.join(DEST, fname)
            await pg.screenshot(path=out, full_page=True)
            print(out, os.path.getsize(out) // 1024, "KB")
        await b.close()

asyncio.run(main())
