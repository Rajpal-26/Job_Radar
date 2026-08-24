from scrapers.indeed import _launch, _is_blocked
from playwright.sync_api import sync_playwright
import time

cities = ["Bengaluru", "Pune", "Noida", "Gurugram", "Indore", "Ahmedabad"]

with sync_playwright() as p:
    for city in cities:
        browser, context = _launch(p, headless=True)
        page = context.new_page()
        url = f"https://in.indeed.com/jobs?q=associate+software+engineer&l={city}%2C+India&fromage=10&sort=date"
        print(f"\nFetching {city} in fresh browser...")
        page.goto(url)
        page.wait_for_timeout(3000)

        cards = page.query_selector_all("div.cardOutline, div.job_seen_beacon, td.resultContent")
        print(f"{city}: Title={page.title()!r}, Cards={len(cards)}, Blocked={_is_blocked(page)}")
        browser.close()
        time.sleep(0.5)
