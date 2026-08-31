import requests
import lxml.html
import re
import urllib.parse

def test_yahoo(company="Razorpay", role="Technical Recruiter"):
    query = f'site:linkedin.com/in/ "{company}" "{role}"'
    url = f"https://search.yahoo.com/search?p={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    r = requests.get(url, headers=headers, timeout=10)
    print("Yahoo status:", r.status_code, "Length:", len(r.text))
    doc = lxml.html.fromstring(r.text)
    
    results = doc.xpath('//div[contains(@class, "algo")]')
    print("Yahoo algo results:", len(results))
    
    people = []
    for item in results:
        title_el = item.xpath('.//h3/a')
        snippet_el = item.xpath('.//div[contains(@class, "compText")]')
        if not title_el:
            continue
            
        href = title_el[0].get("href", "")
        title = title_el[0].text_content().strip()
        snippet = snippet_el[0].text_content().strip() if snippet_el else ""
        
        # Yahoo redirect url unwrapping: /RU=https%3a%2f%2fin.linkedin.com%2fin%2f.../
        if "/RU=" in href:
            match = re.search(r'/RU=([^/]+)/', href)
            if match:
                href = urllib.parse.unquote(match.group(1))
                
        if "linkedin.com/in/" in href:
            clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', title, flags=re.IGNORECASE)
            clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
            parts = [p.strip() for p in re.split(r'[-–—|:]', clean_title) if p.strip()]
            name = parts[0] if parts else "Recruiter"
            headline = " - ".join(parts[1:]) if len(parts) > 1 else (snippet[:90] or f"{role} at {company}")
            
            people.append({
                "name": name,
                "headline": headline,
                "company": company,
                "profile_url": href.split("?")[0],
                "snippet": snippet
            })
            
    print("Parsed people count:", len(people))
    for p in people[:4]:
        print("->", p["name"], "||", p["headline"])
        print("   URL:", p["profile_url"])
        print()

if __name__ == "__main__":
    test_yahoo("Swiggy", "Technical Recruiter")
