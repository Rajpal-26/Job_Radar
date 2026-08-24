import time
import tempfile
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    user_dir = tempfile.mkdtemp(prefix="test_chrome_")
    try:
        context = p.chromium.launch_persistent_context(
            user_dir,
            channel="chrome",
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1366, "height": 768},
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en']});
            window.chrome = {runtime: {}};
        """)
        page = context.new_page()

        url = "https://in.indeed.com/jobs?q=DevOps&l=Bengaluru%2C+Karnataka&fromage=7"
        print("Fetching with channel='chrome':", url)
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(3)
        print("Page title:", page.title())
        cards = page.query_selector_all("div.job_seen_beacon, td.resultContent")
        print("Cards found with real Chrome:", len(cards))
        context.close()
    except Exception as e:
        print("Error with real Chrome:", e)
