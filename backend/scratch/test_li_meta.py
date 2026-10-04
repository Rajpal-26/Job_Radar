# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import asyncio
from playwright.async_api import async_playwright

async def test_li_profile(urls):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            locale='en-US'
        )
        page = await ctx.new_page()
        for u in urls:
            print(f"\n--- Testing: {u} ---")
            try:
                await page.goto(u, wait_until='domcontentloaded', timeout=12000)
                title = await page.title()
                print("Page title:", title)
                og_desc = await page.evaluate("""() => {
                    const m = document.querySelector('meta[property="og:description"], meta[name="description"]');
                    return m ? m.content : '';
                }""")
                print("OG Description:", og_desc)
                # Also check heading / subline
                top_card = await page.evaluate("""() => {
                    const h1 = document.querySelector('h1');
                    const h2 = document.querySelector('h2, .top-card-layout__headline');
                    return {
                        name: h1 ? h1.innerText.trim() : '',
                        headline: h2 ? h2.innerText.trim() : ''
                    };
                }""")
                print("Top card:", top_card)
            except Exception as e:
                print("Error:", e)
        await b.close()

if __name__ == "__main__":
    urls = [
        "https://in.linkedin.com/in/shreeya-joshi-aa949116b",
        "https://in.linkedin.com/in/karishma-agrawal-79830715a",
        "https://in.linkedin.com/in/chandrika-mittal-47423a16a"
    ]
    asyncio.run(test_li_profile(urls))
