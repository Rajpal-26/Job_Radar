import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    try:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )
        page = context.new_page()

        print("Testing Indeed with Firefox...")
        url = "https://in.indeed.com/jobs?q=DevOps&l=Bengaluru%2C+Karnataka&fromage=7"
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(3)
        print("Page title:", page.title())
        cards = page.query_selector_all("div.job_seen_beacon, td.resultContent")
        print("Firefox cards found:", len(cards))
        browser.close()
    except Exception as e:
        print("Firefox error:", e)
