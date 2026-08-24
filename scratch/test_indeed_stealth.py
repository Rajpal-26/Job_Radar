import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        ]
    )
    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        locale="en-IN",
        timezone_id="Asia/Kolkata",
    )
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en']});
        window.chrome = {runtime: {}};
    """)
    page = context.new_page()

    # Step 1: Visit Indeed homepage
    print("Navigating to homepage...")
    try:
        page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=20000)
        time.sleep(3)
        print("Homepage title:", page.title())
    except Exception as e:
        print("Homepage error:", e)

    # Step 2: Search URL
    url = "https://in.indeed.com/jobs?q=DevOps&l=Bengaluru%2C+Karnataka&fromage=7"
    print("Navigating to search URL:", url)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(3)
        print("Search title:", page.title())
        cards = page.query_selector_all("div.job_seen_beacon, td.resultContent")
        print("Cards found:", len(cards))
    except Exception as e:
        print("Search error:", e)

    browser.close()
