from playwright.sync_api import sync_playwright
import urllib.parse
import re

def test_pw_google_genuine(company="Razorpay", role="Technical Recruiter"):
    query = f'{company} {role} linkedin profile'
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=en"
    
    print(f"Testing Google Playwright for: {query}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            
            print("Google Page Title:", page.title())
            
            # Find all links
            links = page.query_selector_all('a[href*="linkedin.com/in/"]')
            print("Found LinkedIn links:", len(links))
            
            for a in links:
                href = a.get_attribute("href") or ""
                text = a.inner_text().strip()
                h3 = a.query_selector("h3")
                if h3:
                    text = h3.inner_text().strip()
                print(f"-> {text} | {href}")
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test_pw_google_genuine("Razorpay", "Technical Recruiter")
    test_pw_google_genuine("Supersourcing", "HR Manager")
