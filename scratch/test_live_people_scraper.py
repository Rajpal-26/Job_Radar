import requests
import re
import urllib.parse
import lxml.html
import json

def scrape_linkedin_people_live(company="Supersourcing", role="HR Manager", location="India"):
    # Normalize company name (remove "pvt ltd", "technologies", etc. for broad matching if needed)
    short_company = re.sub(r'(?i)\s*(pvt|ltd|technologies|private|limited|inc|corp|services)\b', '', company).strip()
    if not short_company:
        short_company = company
        
    query = f"{short_company} {role} linkedin"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    people = []
    seen = set()
    
    # 1. Search via Yahoo
    try:
        y_url = f"https://search.yahoo.com/search?p={urllib.parse.quote(query)}"
        resp = requests.get(y_url, headers=headers, timeout=8)
        if resp.status_code == 200:
            doc = lxml.html.fromstring(resp.text)
            for item in doc.xpath('//div[contains(@class, "algo")]'):
                t_el = item.xpath('.//h3/a')
                s_el = item.xpath('.//div[contains(@class, "compText")]')
                if not t_el:
                    continue
                href = t_el[0].get("href", "")
                raw_title = t_el[0].text_content().strip()
                snippet = s_el[0].text_content().strip() if s_el else ""
                
                # Unpack yahoo URL
                if "/RU=" in href:
                    match = re.search(r'/RU=([^/]+)/', href)
                    if match:
                        href = urllib.parse.unquote(match.group(1))
                        
                if "linkedin.com/in/" not in href:
                    continue
                    
                clean_url = href.split("?")[0].rstrip("/")
                if clean_url in seen:
                    continue
                seen.add(clean_url)
                
                # Parse Name and Title
                clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', raw_title, flags=re.IGNORECASE)
                clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
                parts = [p.strip() for p in re.split(r'[-–—|:]', clean_title) if p.strip()]
                
                name = parts[0] if parts else "Member"
                position = " - ".join(parts[1:]) if len(parts) > 1 else (snippet[:80] or f"{role} at {company}")
                
                # Infer experience level
                exp = "Senior (5+ yrs)" if any(k in position.lower() for k in ["lead", "senior", "head", "manager", "director", "vp"]) else "Mid-Level (2-5 yrs)"
                
                people.append({
                    "name": name,
                    "position": position,
                    "company": company,
                    "experience": exp,
                    "location": location or "India",
                    "profile_url": clean_url,
                    "snippet": snippet
                })
    except Exception as e:
        print("Yahoo error:", e)
        
    print(f"Total live scraped: {len(people)}")
    return people

if __name__ == "__main__":
    res = scrape_linkedin_people_live("Supersourcing", "HR Manager", "India")
    for p in res:
        print(p)
