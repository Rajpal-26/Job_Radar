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
        ]
    )
    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
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

    print("Step 1: Go to homepage...")
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)
    print("Homepage title:", page.title())

    print("Step 2: Fill search inputs...")
    try:
        what_input = page.query_selector("input[id*='what']") or page.query_selector("input[name='q']")
        if what_input:
            what_input.fill("DevOps Engineer")

        where_input = page.query_selector("input[id*='where']") or page.query_selector("input[name='l']")
        if where_input:
            where_input.fill("Bengaluru")

        submit_btn = page.query_selector("button[type='submit']") or page.query_selector("button.y945t")
        if submit_btn:
            submit_btn.click()
            print("Clicked submit!")
        else:
            page.keyboard.press("Enter")
            print("Pressed Enter!")

        time.sleep(5)
        print("After search title:", page.title())
        cards = page.query_selector_all("div.job_seen_beacon, td.resultContent, div[class*='jobCard']")
        print("Cards found via UI search:", len(cards))
        if cards:
            title_el = cards[0].query_selector("h2 a, a[class*='JobTitle']")
            if title_el:
                print("First job title:", title_el.inner_text().strip())
    except Exception as e:
        print("UI search error:", e)

    browser.close()
