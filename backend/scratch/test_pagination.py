# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import asyncio
import urllib.parse
import re
from playwright.async_api import async_playwright

async def test_pagination(company, keyword):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = await ctx.new_page()
        
        q = f'site:linkedin.com/in/ "{company}" "{keyword}"'
        # Page 2
        url = f'https://search.yahoo.com/search?p={urllib.parse.quote(q)}&b=11'
        print('Page 2 URL:', url)
        await page.goto(url, wait_until='domcontentloaded', timeout=12000)
        items = await page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('div.algo, li div.dd, #web ol li').forEach(el => {
                const a = el.querySelector('h3 a, a.fz-20, a');
                const snip = el.querySelector('div.compText, p.lh-16, .lh-16, div.lh-16');
                if (a && a.href) {
                    results.push({
                        title: (a.innerText || '').trim(),
                        href: a.href,
                        snippet: snip ? (snip.innerText || '').trim() : ''
                    });
                }
            });
            return results;
        }""")
        print('Page 2 items found:', len(items))
        for it in items:
            raw_href = it['href']
            m = re.search(r'/RU=([^/]+)/', raw_href)
            clean_url = urllib.parse.unquote(m.group(1)) if m else raw_href
            if 'linkedin.com/in/' in clean_url:
                print(' -', it['title'].replace('\n', ' ')[:60], '-->', clean_url)
        await b.close()

if __name__ == '__main__':
    asyncio.run(test_pagination('Infosys', 'Talent Acquisition'))
