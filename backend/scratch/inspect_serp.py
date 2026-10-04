# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import asyncio
import urllib.parse
import re
from playwright.async_api import async_playwright

async def inspect_search(company: str, keyword: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await context.new_page()

        # Try Yahoo and Bing
        queries = [
            f'site:linkedin.com/in/ "{company}" "{keyword}"',
            f'site:linkedin.com/in/ "{company}" "Talent Acquisition"',
            f'site:linkedin.com/in/ "{company}" "Human Resources"',
            f'site:linkedin.com/in/ "{company}" "Recruiter"'
        ]

        for q in queries:
            print(f"\n================ QUERY: {q} ================")
            url = f"https://search.yahoo.com/search?p={urllib.parse.quote(q)}"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=12000)
                await page.wait_for_timeout(1000)

                items = await page.evaluate("""() => {
                    const results = [];
                    document.querySelectorAll('div.algo, li div.dd, #web ol li').forEach(el => {
                        const a = el.querySelector('h3 a, a.fz-20, a');
                        const snip = el.querySelector('div.compText, p.lh-16, .lh-16, div.lh-16');
                        if (a && a.href) {
                            results.push({
                                raw_title: (a.innerText || '').trim(),
                                href: a.href,
                                raw_snippet: snip ? (snip.innerText || '').trim() : ''
                            });
                        }
                    });
                    return results;
                }""")

                for it in items:
                    raw_href = it['href']
                    m = re.search(r'/RU=([^/]+)/', raw_href)
                    clean_url = urllib.parse.unquote(m.group(1)) if m else raw_href
                    if "linkedin.com/in/" not in clean_url:
                        continue
                    clean_url = re.sub(r'\?.*$', '', clean_url).rstrip('/')

                    print(f"TITLE  : {it['raw_title']}")
                    print(f"SNIPPET: {it['raw_snippet']}")
                    print(f"URL    : {clean_url}")
                    print("-" * 50)
            except Exception as e:
                print("Error:", e)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_search("GammaStack", "HR"))
