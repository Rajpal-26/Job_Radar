from playwright.sync_api import sync_playwright
import urllib.parse
import re

def test_pw_bing(company="Razorpay", role="Technical Recruiter", location="India"):
    query = f'site:linkedin.com/in/ "{company}" {role}'
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        
        items = page.query_selector_all('li.b_algo')
        print("Bing b_algo items found:", len(items))
        
        people = []
        for it in items:
            title_el = it.query_selector('h2 a')
            snippet_el = it.query_selector('p')
            if not title_el:
                continue
            title = title_el.inner_text().strip()
            href = title_el.get_attribute("href") or ""
            snippet = snippet_el.inner_text().strip() if snippet_el else ""
            
            print("TITLE:", title)
            print("HREF:", href)
            print("SNIPPET:", snippet)
            print("-" * 40)
            
        browser.close()

if __name__ == "__main__":
    test_pw_bing()
