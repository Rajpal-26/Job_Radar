# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import asyncio
import urllib.parse
import re
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        q = 'site:linkedin.com/in/ "GammaStack"'
        url = f"https://search.yahoo.com/search?p={urllib.parse.quote(q)}"
        print("Navigating to:", url)
        await page.goto(url, wait_until="commit", timeout=15000)
        await page.wait_for_timeout(1500)
        
        # Print page HTML snippet or links
        all_links = await page.evaluate("""() => {
            const res = [];
            document.querySelectorAll('a').forEach(a => {
                res.push({ text: a.innerText.trim(), href: a.href });
            });
            return res;
        }""")
        print(f"Total links on page: {len(all_links)}")
        li_found = 0
        for l in all_links:
            href = l['href']
            text = l['text']
            match_ru = re.search(r'/RU=([^/]+)/', href)
            clean = urllib.parse.unquote(match_ru.group(1)) if match_ru else href
            if "linkedin.com/in" in clean:
                li_found += 1
                print(f"[{li_found}] Title: {text} | Clean URL: {clean}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
