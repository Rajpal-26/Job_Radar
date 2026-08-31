import requests
import lxml.html
import base64
import urllib.parse
import re

def decode_bing_u(u_val):
    if not u_val:
        return ""
    if u_val.startswith("a1"):
        b64_str = u_val[2:]
        # Add padding if needed
        padding = 4 - (len(b64_str) % 4)
        if padding and padding < 4:
            b64_str += "=" * padding
        try:
            return base64.b64decode(b64_str).decode("utf-8", errors="ignore")
        except Exception:
            return ""
    return u_val

def search_linkedin_people_bing(company="Razorpay", role="Technical Recruiter"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    query = f'site:linkedin.com/in/ "{company}" "{role}"'
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    
    r = requests.get(url, headers=headers, timeout=10)
    doc = lxml.html.fromstring(r.text)
    
    results = doc.xpath('//li[contains(@class, "b_algo")]')
    print("Found items:", len(results))
    
    people = []
    for item in results:
        title_el = item.xpath('.//h2/a')
        snippet_el = item.xpath('.//p')
        if not title_el:
            continue
            
        raw_href = title_el[0].get("href", "")
        raw_title = title_el[0].text_content().strip()
        snippet = snippet_el[0].text_content().strip() if snippet_el else ""
        
        # Check if href is Bing redirect
        actual_url = raw_href
        if "/ck/a?" in raw_href and "u=" in raw_href:
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query)
            u_param = parsed.get("u", [""])[0]
            decoded = decode_bing_u(u_param)
            if decoded:
                actual_url = decoded
                
        if "linkedin.com/in/" in actual_url:
            clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', raw_title, flags=re.IGNORECASE)
            parts = [p.strip() for p in re.split(r'[-–—|:]', clean_title) if p.strip()]
            name = parts[0] if parts else "Hiring Specialist"
            headline = " - ".join(parts[1:]) if len(parts) > 1 else snippet[:100]
            
            people.append({
                "name": name,
                "headline": headline,
                "company": company,
                "profile_url": actual_url.split("?")[0],
                "snippet": snippet
            })
            
    print("Parsed People:", len(people))
    for p in people:
        print(f"-> Name: {p['name']} | Headline: {p['headline']}")
        print(f"   URL: {p['profile_url']}\n")

if __name__ == "__main__":
    search_linkedin_people_bing("Razorpay", "Technical Recruiter")
