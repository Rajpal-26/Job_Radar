# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import asyncio
import urllib.parse
import re
from playwright.async_api import async_playwright

async def test_multi_engines(company, keyword):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await ctx.new_page()

        # 1. Bing
        bing_q = f'site:linkedin.com/in/ "{company}" "{keyword}"'
        bing_url = f"https://www.bing.com/search?q={urllib.parse.quote(bing_q)}"
        print(f"\n--- BING: {bing_q} ---")
        try:
            await page.goto(bing_url, wait_until="domcontentloaded", timeout=12000)
            items = await page.evaluate("""() => {
                const res = [];
                document.querySelectorAll('li.b_algo').forEach(el => {
                    const a = el.querySelector('h2 a');
                    const p = el.querySelector('div.b_caption p, p');
                    if (a && a.href) {
                        res.push({
                            title: a.innerText.trim(),
                            href: a.href,
                            snippet: p ? p.innerText.trim() : ''
                        });
                    }
                });
                return res;
            }""")
            print(f"Bing found {len(items)} items:")
            for it in items[:6]:
                print(" - Title:", it['title'])
                print("   Snippet:", it['snippet'][:80])
                print("   Href:", it['href'][:70])
        except Exception as e:
            print("Bing error:", e)

        # 2. DuckDuckGo HTML
        ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(bing_q)}"
        print(f"\n--- DUCKDUCKGO: {bing_q} ---")
        try:
            await page.goto(ddg_url, wait_until="domcontentloaded", timeout=12000)
            items_ddg = await page.evaluate("""() => {
                const res = [];
                document.querySelectorAll('.result').forEach(el => {
                    const a = el.querySelector('.result__title a');
                    const snip = el.querySelector('.result__snippet');
                    if (a && a.href) {
                        res.push({
                            title: a.innerText.trim(),
                            href: a.href,
                            snippet: snip ? snip.innerText.trim() : ''
                        });
                    }
                });
                return res;
            }""")
            print(f"DuckDuckGo found {len(items_ddg)} items:")
            for it in items_ddg[:6]:
                print(" - Title:", it['title'])
                print("   Snippet:", it['snippet'][:80])
                print("   Href:", it['href'][:70])
        except Exception as e:
            print("DDG error:", e)

        await b.close()

if __name__ == "__main__":
    asyncio.run(test_multi_engines("GammaStack", "HR"))
    asyncio.run(test_multi_engines("Thoughtwin", "HR"))
