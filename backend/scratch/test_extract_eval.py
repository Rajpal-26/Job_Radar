# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import asyncio
import re
import urllib.parse
from playwright.async_api import async_playwright

def parse_serp_title(raw_text: str, company: str) -> tuple[str, str]:
    t = raw_text.strip()
    t = re.sub(r'^(?:Linkedin|LinkedIn)[^\n\r]*?(?=[A-Z][a-z]+|\b[A-Z]{2,}\b)', '', t).strip()
    t = re.sub(r'https?://\S+', '', t).strip()
    t = re.sub(r'\s*\|\s*LinkedIn.*$', '', t, flags=re.IGNORECASE).strip()
    t = re.sub(r'\s*[-–—|]\s*LinkedIn.*$', '', t, flags=re.IGNORECASE).strip()
    parts = [p.strip() for p in re.split(r'\s*[-–—|]\s*', t) if p.strip()]
    if len(parts) >= 2:
        name = parts[0]
        title = ' - '.join(parts[1:])
        title = re.sub(rf'\s*(?:at|@|-)\s*{re.escape(company)}.*$', '', title, flags=re.IGNORECASE).strip()
        return name, title or f'HR at {company}'
    elif len(parts) == 1:
        return parts[0], f'Professional at {company}'
    return 'LinkedIn Member', f'Recruiter at {company}'

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        page = await ctx.new_page()
        q = 'site:linkedin.com/in/ "GammaStack" HR'
        url = f'https://search.yahoo.com/search?p={urllib.parse.quote(q)}'
        print("Navigating to:", url)
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        
        items = await page.evaluate('''() => {
            const list = [];
            document.querySelectorAll('a').forEach(a => {
                const href = a.href || '';
                const text = a.innerText || a.getAttribute('aria-label') || '';
                if (href && (href.includes('linkedin.com/in') || href.includes('/RU='))) {
                    let snip = '';
                    const parent = a.closest('li, div.algo, div.dd');
                    if (parent) {
                        const snipEl = parent.querySelector('div.compText, p, .lh-16');
                        if (snipEl) snip = snipEl.innerText;
                    }
                    list.push({ title: text.trim(), href: href, snippet: snip.trim() });
                }
            });
            return list;
        }''')
        
        discovered = []
        seen = set()
        for it in items:
            raw_href = it['href']
            match_ru = re.search(r'/RU=([^/]+)/', raw_href)
            clean_url = urllib.parse.unquote(match_ru.group(1)) if match_ru else raw_href
            if 'linkedin.com/in/' not in clean_url:
                continue
            clean_url = re.sub(r'\?.*$', '', clean_url).rstrip('/')
            if clean_url in seen:
                continue
            name, title = parse_serp_title(it['title'], 'GammaStack')
            if not name or name.lower() in ['linkedin', 'more', 'anytime', 'click here']:
                continue
            seen.add(clean_url)
            discovered.append({'name': name, 'title': title, 'url': clean_url})

        print(f'Total discovered: {len(discovered)}')
        for d in discovered:
            print(' *', d['name'], '|', d['title'], '|', d['url'])
        await b.close()

if __name__ == '__main__':
    asyncio.run(run())
