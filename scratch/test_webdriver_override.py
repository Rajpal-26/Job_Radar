from playwright.sync_api import sync_playwright

url = "https://in.indeed.com/jobs?q=associate+software+engineer&l=Bengaluru%2C+Karnataka&fromage=10&sort=date"

print("--- Test WITHOUT init_js ---")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
    )
    page = context.new_page()
    page.goto(url)
    page.wait_for_timeout(3000)
    cards = page.query_selector_all("div.cardOutline, div.job_seen_beacon, td.resultContent")
    print(f"WITHOUT init_js: Title={page.title()!r}, Cards={len(cards)}")
    browser.close()

print("\n--- Test WITH init_js (defineProperty) ---")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    page = context.new_page()
    page.goto(url)
    page.wait_for_timeout(3000)
    cards = page.query_selector_all("div.cardOutline, div.job_seen_beacon, td.resultContent")
    print(f"WITH init_js: Title={page.title()!r}, Cards={len(cards)}")
    browser.close()
