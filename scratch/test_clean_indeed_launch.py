from playwright.sync_api import sync_playwright

url = "https://in.indeed.com/jobs?q=associate+software+engineer&l=Bengaluru%2C+Karnataka&fromage=10&sort=date"

print("--- Testing clean p.chromium.launch(headless=True) ---")
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
    )
    page = context.new_page()
    page.goto(url)
    page.wait_for_timeout(4000)

    title = page.title()
    cards = page.query_selector_all("div.cardOutline, div.job_seen_beacon, td.resultContent")
    print(f"Headless=True Title: {title!r}, Cards: {len(cards)}")
    browser.close()

print("\n--- Testing clean p.chromium.launch(headless=False) ---")
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
    )
    page = context.new_page()
    page.goto(url)
    page.wait_for_timeout(4000)

    title = page.title()
    cards = page.query_selector_all("div.cardOutline, div.job_seen_beacon, td.resultContent")
    print(f"Headless=False Title: {title!r}, Cards: {len(cards)}")
    browser.close()
