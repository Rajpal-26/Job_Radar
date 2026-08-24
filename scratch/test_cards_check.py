from scrapers.indeed import scrape_indeed, _scrape_with
from playwright.sync_api import sync_playwright

print("Testing direct _scrape_with after removing false bot check...")

with sync_playwright() as p:
    browser, context = p.chromium.launch(headless=True), None
    page = browser.new_page()
    url = "https://in.indeed.com/jobs?q=associate+software+engineer&l=Bengaluru%2C+Karnataka&fromage=10&sort=date"
    page.goto(url)
    page.wait_for_timeout(3000)
    cards = page.query_selector_all("div.cardOutline, div.job_seen_beacon, td.resultContent")
    print(f"Direct page load Cards: {len(cards)}")
    browser.close()
