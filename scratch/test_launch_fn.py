from scrapers.indeed import _launch, _is_blocked
from playwright.sync_api import sync_playwright

url = "https://in.indeed.com/jobs?q=associate+software+engineer&l=Bengaluru%2C+Karnataka&fromage=10&radius=100&sort=date&start=0"

with sync_playwright() as p:
    browser, context = _launch(p, headless=True)
    page = context.new_page()
    page.goto(url)
    page.wait_for_timeout(3000)

    title = page.title()
    cards = page.query_selector_all("div.cardOutline, div.job_seen_beacon, td.resultContent")
    blocked = _is_blocked(page)
    print(f"Title: {title!r}")
    print(f"Cards: {len(cards)}")
    print(f"Is Blocked: {blocked}")
    browser.close()
