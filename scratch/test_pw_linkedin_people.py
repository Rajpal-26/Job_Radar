from playwright.sync_api import sync_playwright
import urllib.parse
import re

def test_pw_linkedin(company="Razorpay", role="Technical Recruiter"):
    query = f"{company} {role}"
    url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(query)}"
    print("Navigating to:", url)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(3000)
            print("Page title:", page.title())
            print("Current URL:", page.url)
            
            # Check for profile cards or sign in wall
            cards = page.query_selector_all('li.reusable-search__result-container, div.base-search-card, a[href*="/in/"]')
            print("Found cards/links:", len(cards))
            
            for c in cards[:5]:
                print("Text:", c.inner_text().replace("\n", " | ")[:120])
                if c.get_attribute("href"):
                    print("Href:", c.get_attribute("href"))
                print()
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test_pw_linkedin()
