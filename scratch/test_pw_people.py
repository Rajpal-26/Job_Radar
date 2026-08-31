from playwright.sync_api import sync_playwright
import urllib.parse
import re

def scrape_people_playwright(company="Razorpay", role="Technical Recruiter", location="India", limit=10):
    query = f'site:linkedin.com/in/ "{company}" "{role}"'
    if location:
        query += f' "{location}"'
        
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=en"
    
    people = []
    seen = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = context.new_page()
        try:
            print("Navigating to:", google_url)
            page.goto(google_url, timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            
            # Extract search items
            links = page.query_selector_all('a[href*="linkedin.com/in/"]')
            print("Found LinkedIn links:", len(links))
            
            for a in links:
                href = a.get_attribute("href") or ""
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                href = href.split("?")[0].rstrip("/")
                
                if "linkedin.com/in/" not in href or href in seen or "translate.google" in href:
                    continue
                seen.add(href)
                
                # Get title/name
                h3 = a.query_selector("h3")
                raw_title = h3.inner_text().strip() if h3 else href.split("/in/")[-1].replace("-", " ").title()
                
                # Clean up title
                clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', raw_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
                parts = [pt.strip() for pt in re.split(r'[-–—|:]', clean_title) if pt.strip()]
                
                name = parts[0] if parts else "Hiring Specialist"
                headline = " - ".join(parts[1:]) if len(parts) > 1 else f"{role} at {company}"
                
                # Avatar initial generator
                initials = "".join([w[0].upper() for w in name.split()[:2] if w])
                
                people.append({
                    "name": name,
                    "headline": headline,
                    "company": company,
                    "location": location or "India",
                    "profile_url": href,
                    "initials": initials or "HR"
                })
                
                if len(people) >= limit:
                    break
        except Exception as e:
            print("Playwright error:", e)
        finally:
            browser.close()
            
    return people

if __name__ == "__main__":
    res = scrape_people_playwright("Razorpay", "Technical Recruiter", "India", 6)
    print("PLAYWRIGHT SCRAPED:", len(res))
    for p in res:
        print(f"-> {p['name']} ({p['initials']}) | {p['headline']}")
        print(f"   URL: {p['profile_url']}\n")
