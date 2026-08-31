from playwright.sync_api import sync_playwright
import urllib.parse
import re

def test_pw_bing3(company="Razorpay", role="Technical Recruiter"):
    query = f'site:linkedin.com "{company}" ("{role}" OR "Recruiter" OR "Talent Acquisition")'
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        
        items = page.query_selector_all('li.b_algo')
        print("Bing items count:", len(items))
        
        for it in items:
            title_el = it.query_selector('h2 a')
            snippet_el = it.query_selector('p')
            cite_el = it.query_selector('cite')
            if not title_el:
                continue
            title = title_el.inner_text().strip().encode('ascii', 'replace').decode('ascii')
            href = title_el.get_attribute("href") or ""
            cite = cite_el.inner_text().strip().encode('ascii', 'replace').decode('ascii') if cite_el else ""
            snippet = snippet_el.inner_text().strip().encode('ascii', 'replace').decode('ascii') if snippet_el else ""
            
            print("TITLE:", title)
            print("CITE:", cite)
            print("SNIPPET:", snippet[:120])
            print("-" * 40)
            
        browser.close()

if __name__ == "__main__":
    test_pw_bing3("Razorpay", "Technical Recruiter")
