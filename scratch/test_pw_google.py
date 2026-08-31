from playwright.sync_api import sync_playwright
import urllib.parse
import re

def scrape_linkedin_profiles_playwright(company="Razorpay", role="Technical Recruiter", location="India", limit=10):
    query = f'{company} {role} site:linkedin.com/in/'
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
            page.goto(google_url, wait_until="domcontentloaded", timeout=12000)
            page.wait_for_timeout(1500)
            
            # Find all search result headers & links
            result_nodes = page.query_selector_all('div.g')
            print("Found result divs:", len(result_nodes))
            
            for node in result_nodes:
                a_tag = node.query_selector('a[href*="linkedin.com/in/"]')
                if not a_tag:
                    # check all a tags in node
                    all_a = node.query_selector_all('a')
                    for a in all_a:
                        href = a.get_attribute("href") or ""
                        if "linkedin.com/in/" in href:
                            a_tag = a
                            break
                if not a_tag:
                    continue
                    
                href = a_tag.get_attribute("href") or ""
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                href = href.split("?")[0].rstrip("/")
                
                if "linkedin.com/in/" not in href or href in seen or "translate.google" in href:
                    continue
                seen.add(href)
                
                h3 = node.query_selector("h3")
                raw_title = h3.inner_text().strip() if h3 else href.split("/in/")[-1].replace("-", " ").title()
                
                snippet_el = node.query_selector('div[style*="-webkit-line-clamp"], div[data-snf], div.VwiC3b')
                snippet = snippet_el.inner_text().strip() if snippet_el else ""
                
                clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', raw_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
                parts = [pt.strip() for pt in re.split(r'[-–—|:]', clean_title) if pt.strip()]
                
                name = parts[0] if parts else "Hiring Specialist"
                headline = " - ".join(parts[1:]) if len(parts) > 1 else (snippet[:80] or f"{role} at {company}")
                
                initials = "".join([w[0].upper() for w in name.split()[:2] if w and w[0].isalpha()]) or "HR"
                
                people.append({
                    "name": name,
                    "headline": headline,
                    "company": company,
                    "location": location or "India",
                    "profile_url": href,
                    "snippet": snippet,
                    "initials": initials
                })
                
                if len(people) >= limit:
                    break
        except Exception as e:
            print("Error in scraper:", e)
        finally:
            browser.close()
            
    return people

if __name__ == "__main__":
    res = scrape_linkedin_profiles_playwright("Razorpay", "Technical Recruiter", "India", 6)
    print("TOTAL SCRAPED:", len(res))
    for p in res:
        print(f"[{p['name']}] ({p['initials']}) - {p['headline']}")
        print(f"  URL: {p['profile_url']}\n")
