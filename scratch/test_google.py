import requests
import lxml.html
import re
import urllib.parse

def test_google(company="Razorpay", role="Technical Recruiter"):
    query = f'site:linkedin.com/in/ "{company}" "{role}"'
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=15&hl=en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    r = requests.get(url, headers=headers, timeout=10)
    print("Google status:", r.status_code, "Length:", len(r.text))
    doc = lxml.html.fromstring(r.text)
    
    # Check for search result links containing linkedin.com/in/
    links = doc.xpath('//a[contains(@href, "linkedin.com/in/")]')
    print("Google LinkedIn link elements found:", len(links))
    
    people = []
    seen = set()
    for a in links:
        href = a.get("href", "")
        # Google wrap: /url?q=https://in.linkedin.com/in/...&sa=...
        if "/url?q=" in href:
            href = href.split("/url?q=")[1].split("&")[0]
        
        href = href.split("?")[0].rstrip("/")
        if "linkedin.com/in/" not in href or href in seen:
            continue
        seen.add(href)
        
        # Look for h3 inside or near
        h3 = a.xpath('.//h3')
        if not h3:
            h3 = a.xpath('ancestor::div[contains(@class, "g")]//h3')
        
        raw_title = h3[0].text_content().strip() if h3 else href.split("/in/")[-1].replace("-", " ").title()
        
        # Snippet
        snippet_node = a.xpath('ancestor::div[contains(@class, "g")]//div[contains(@style, "-webkit-line-clamp")] | ancestor::div[contains(@class, "g")]//div[@data-snf]')
        snippet = snippet_node[0].text_content().strip() if snippet_node else ""
        
        clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', raw_title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
        parts = [p.strip() for p in re.split(r'[-–—|:]', clean_title) if p.strip()]
        
        name = parts[0] if parts else "Recruiter"
        headline = " - ".join(parts[1:]) if len(parts) > 1 else (snippet[:90] or f"{role} at {company}")
        
        people.append({
            "name": name,
            "headline": headline,
            "company": company,
            "profile_url": href,
            "snippet": snippet
        })
        
    print("Parsed Google people:", len(people))
    for p in people[:5]:
        print("->", p["name"], "||", p["headline"])
        print("   URL:", p["profile_url"])
        print()

if __name__ == "__main__":
    test_google("Razorpay", "Technical Recruiter")
