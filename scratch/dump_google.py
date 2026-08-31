from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.google.com/search?q=Razorpay+Technical+Recruiter+site:linkedin.com/in/&hl=en")
    print("Page title:", page.title())
    print("Page body start:", page.inner_text("body")[:300])
    browser.close()
