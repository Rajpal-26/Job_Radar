from playwright.sync_api import sync_playwright
import urllib.parse
import re

def scrape_ddg_profiles(company="Supersourcing", role="HR Manager"):
    query = f"{company} {role} site:linkedin.com/in/"
    url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
    
    people = []
    seen = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(3000)
            
            # Extract results
            articles = page.query_selector_all('article[data-testid="result"]')
            print("Found DDG articles:", len(articles))
            
            for art in articles:
                title_el = art.query_selector('h2 a')
                snippet_el = art.query_selector('div[data-result="snippet"]')
                if not title_el:
                    continue
                    
                title = title_el.inner_text().strip()
                href = title_el.get_attribute("href") or ""
                snippet = snippet_el.inner_text().strip() if snippet_el else ""
                
                if "linkedin.com/in/" not in href:
                    continue
                clean_url = href.split("?")[0].rstrip("/")
                if clean_url in seen:
                    continue
                seen.add(clean_url)
                
                # Parse Name and Title: e.g. "Prateek Godse - Lead HR Manager - Supersourcing | LinkedIn"
                clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', title, flags=re.IGNORECASE)
                clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
                parts = [pt.strip() for pt in re.split(r'[-–—|:]', clean_title) if pt.strip()]
                
                name = parts[0] if parts else clean_url.split("/in/")[-1].replace("-", " ").title()
                position = " - ".join(parts[1:]) if len(parts) > 1 else (snippet[:80] or f"{role} at {company}")
                
                exp = "Lead / Manager (7-10 yrs)" if any(k in position.lower() for k in ["lead", "head", "manager", "director", "vp"]) else "Senior (3-5 yrs)"
                
                people.append({
                    "name": name,
                    "position": position,
                    "company": company,
                    "experience": exp,
                    "location": "India",
                    "profile_url": clean_url,
                    "snippet": snippet
                })
        except Exception as e:
            print("DDG Error:", e)
        finally:
            browser.close()
            
    return people

if __name__ == "__main__":
    res = scrape_ddg_profiles("Supersourcing", "HR Manager")
    print(f"Scraped count: {len(res)}")
    for r in res:
        print(f"-> Name: {r['name']} | Pos: {r['position']}")
        print(f"   Exp: {r['experience']} | URL: {r['profile_url']}\n")
