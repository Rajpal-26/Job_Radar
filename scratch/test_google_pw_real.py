from playwright.sync_api import sync_playwright
import urllib.parse
import re

def scrape_google_profiles_pw(company="Swiggy", role="HR Manager"):
    query = f'site:linkedin.com/in/ "{company}" "{role}"'
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=en"
    
    print(f"Scraping Google for: {url}")
    
    people = []
    seen = set()
    
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
            page.goto(url, wait_until="domcontentloaded", timeout=12000)
            page.wait_for_timeout(2000)
            
            # Print page title
            print("Page Title:", page.title().encode("ascii", "replace").decode("ascii"))
            
            # Extract links
            anchors = page.query_selector_all('a')
            for a in anchors:
                href = a.get_attribute("href") or ""
                if "linkedin.com/in/" not in href:
                    continue
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                href = href.split("?")[0].rstrip("/")
                
                if href in seen or "translate.google" in href:
                    continue
                seen.add(href)
                
                text = a.inner_text().strip().encode("ascii", "replace").decode("ascii")
                h3 = a.query_selector("h3")
                if h3:
                    text = h3.inner_text().strip().encode("ascii", "replace").decode("ascii")
                    
                print(f"Found Profile -> Text: {text} | URL: {href}")
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_google_profiles_pw("Swiggy", "HR Manager")
    scrape_google_profiles_pw("Supersourcing", "HR Manager")
