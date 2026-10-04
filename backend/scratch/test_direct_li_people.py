# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import sys, os
import asyncio, time
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.abspath('.'))
from scrapers.stealth_driver import STEALTH_JS, get_random_user_agent

async def test_direct_linkedin(company_slug):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ]
        )
        ctx = await browser.new_context(
            user_agent=get_random_user_agent(),
            locale="en-IN",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Sec-Ch-Ua": '"Chromium";v="126", "Not/A)Brand";v="24", "Google Chrome";v="126"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Upgrade-Insecure-Requests": "1"
            }
        )
        await ctx.add_init_script(STEALTH_JS)
        page = await ctx.new_page()

        url = f"https://www.linkedin.com/company/{company_slug}/people/"
        print("Navigating to LinkedIn Company People:", url)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(2000)
            print("Current URL:", page.url)
            print("Title:", await page.title())
            content = await page.content()
            print("Content length:", len(content))
            
            # Find people cards or links
            people_links = await page.evaluate("""() => {
                const res = [];
                document.querySelectorAll('a[href*="/in/"]').forEach(a => {
                    res.push({ href: a.href, text: a.innerText.trim() });
                });
                return res;
            }""")
            print(f"People links found: {len(people_links)}")
            for l in people_links[:5]:
                print(" -", l['text'].replace('\\n', ' '), "->", l['href'])
        except Exception as e:
            print("Error:", e)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_direct_linkedin("infosys"))
    asyncio.run(test_direct_linkedin("gammastack"))
