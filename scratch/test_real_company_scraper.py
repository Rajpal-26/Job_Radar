import urllib.parse
import re
import requests
import json
from playwright.sync_api import sync_playwright

def test_duckduckgo_lite(company="Swiggy", role="HR Manager"):
    # DuckDuckGo Lite / HTML endpoint with clean parameters
    query = f'site:linkedin.com/in/ "{company}" "{role}"'
    url = "https://html.duckduckgo.com/html/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://html.duckduckgo.com",
        "Referer": "https://html.duckduckgo.com/",
    }
    
    print(f"Testing DDG HTML for: {company} - {role}")
    try:
        r = requests.post(url, data={"q": query, "b": ""}, headers=headers, timeout=10)
        print("Status:", r.status_code, "Length:", len(r.text))
        
        # Look for linkedin links
        links = re.findall(r'href="([^"]*linkedin\.com/in/[^"]*)"', r.text)
        print("Found regex links in text:", len(links), links[:3])
    except Exception as e:
        print("Error:", e)

def test_playwright_stealth(company="Swiggy", role="HR Manager"):
    query = f'{company} {role} site:linkedin.com/in/'
    print(f"\nTesting Playwright Stealth for: {query}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        # Test Bing
        bing_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        page.goto(bing_url, wait_until="domcontentloaded", timeout=12000)
        page.wait_for_timeout(2000)
        
        results = []
        for item in page.query_selector_all("li.b_algo"):
            h2 = item.query_selector("h2 a")
            snippet = item.query_selector("p")
            cite = item.query_selector("cite")
            
            if not h2:
                continue
            title = h2.inner_text().strip()
            href = h2.get_attribute("href") or ""
            snip_text = snippet.inner_text().strip() if snippet else ""
            cite_text = cite.inner_text().strip() if cite else ""
            
            print(f"Title: {title}")
            print(f"Cite: {cite_text}")
            print(f"Href: {href}")
            print(f"Snippet: {snip_text[:100]}\n")
            
        browser.close()

if __name__ == "__main__":
    test_duckduckgo_lite("Swiggy", "HR Manager")
    test_playwright_stealth("Swiggy", "HR Manager")
