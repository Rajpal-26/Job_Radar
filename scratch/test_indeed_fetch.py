import urllib.request
import json
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

url = "https://in.indeed.com/jobs?q=associate+software+engineer&l=Bengaluru%2C+Karnataka&fromage=10&sort=date"

print("--- Testing urllib ---")
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8")
        print(f"urllib status: {resp.status}, HTML len: {len(html)}")
        if "job_seen_beacon" in html or "jobTitle" in html or "window.mosaic" in html:
            print("FOUND jobs in urllib HTML!")
        else:
            print("urllib blocked or no jobs.")
except Exception as e:
    print(f"urllib error: {e}")

print("\n--- Testing Playwright Headless=False ---")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_timeout(3000)
    title = page.title()
    cards = page.query_selector_all("div.job_seen_beacon, td.resultContent, div.cardOutline")
    print(f"Playwright title: {title!r}, cards found: {len(cards)}")
    browser.close()
