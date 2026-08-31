from playwright.sync_api import sync_playwright
import urllib.parse
import re

def test_no_login_company_page(company_slug="supersourcing"):
    url = f"https://www.linkedin.com/company/{company_slug}/"
    print("Testing company URL:", url)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=12000)
            page.wait_for_timeout(2000)
            print("Title:", page.title())
            print("URL:", page.url)
            
            # Check public employees or leadership
            text = page.inner_text("body")
            print("Snippet:", text[:300].replace("\n", " "))
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test_no_login_company_page("supersourcing")
