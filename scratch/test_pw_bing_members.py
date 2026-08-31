from playwright.sync_api import sync_playwright
import urllib.parse
import re

def scrape_bing_members_pw(company="Supersourcing", role="HR Manager"):
    query = f"{company} {role} linkedin"
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    
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
            page.goto(url, wait_until="domcontentloaded", timeout=12000)
            page.wait_for_timeout(2000)
            
            # Find all links containing linkedin.com/in
            links = page.query_selector_all('a[href*="linkedin.com/in"], li.b_algo a')
            print("Found total links:", len(links))
            
            for a in links:
                href = a.get_attribute("href") or ""
                # Check text
                text = a.inner_text().strip()
                
                # Check parent or li.b_algo
                parent = a.evaluate_handle("el => el.closest('li.b_algo')")
                snippet = ""
                if parent:
                    p_el = parent.as_element().query_selector('p')
                    if p_el:
                        snippet = p_el.inner_text().strip()
                        
                # Unpack bing href if needed
                if "/ck/a?" in href and "u=" in href:
                    import base64
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    u_val = parsed.get("u", [""])[0]
                    if u_val.startswith("a1"):
                        b64_str = u_val[2:]
                        padding = 4 - (len(b64_str) % 4)
                        if padding and padding < 4:
                            b64_str += "=" * padding
                        try:
                            href = base64.b64decode(b64_str).decode("utf-8", errors="ignore")
                        except Exception:
                            pass
                            
                if "linkedin.com/in/" not in href or href in seen:
                    continue
                seen.add(href)
                
                # Extract clean name and title
                clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', text, flags=re.IGNORECASE)
                clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
                parts = [pt.strip() for pt in re.split(r'[-–—|:]', clean_title) if pt.strip()]
                
                name = parts[0] if parts else href.split("/in/")[-1].replace("-", " ").title()
                position = " - ".join(parts[1:]) if len(parts) > 1 else (snippet[:80] or f"{role} at {company}")
                
                exp = "Senior (5+ yrs)" if any(k in position.lower() for k in ["lead", "senior", "head", "manager", "director", "vp"]) else "Mid-Level (2-5 yrs)"
                
                people.append({
                    "name": name,
                    "position": position,
                    "company": company,
                    "experience": exp,
                    "location": "India",
                    "profile_url": href,
                    "snippet": snippet
                })
        except Exception as e:
            print("Playwright error:", e)
        finally:
            browser.close()
            
    return people

if __name__ == "__main__":
    res = scrape_bing_members_pw("Supersourcing", "HR Manager")
    print(f"Scraped count: {len(res)}")
    for r in res:
        print(f"-> Name: {r['name']} | Pos: {r['position']}")
        print(f"   Exp: {r['experience']} | URL: {r['profile_url']}\n")
