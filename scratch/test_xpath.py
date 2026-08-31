import requests
import lxml.html
import re
import urllib.parse

def test_engines_xpath(company="Razorpay", role="Technical Recruiter"):
    query = f'{company} {role} linkedin'
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    # Try Google with clean headers
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=en&num=15"
    r = requests.get(google_url, headers=headers, timeout=10)
    print("Google code:", r.status_code)
    
    doc = lxml.html.fromstring(r.text)
    links = doc.xpath('//a[contains(@href, "linkedin.com/in/")]')
    print("Google LinkedIn anchor tags:", len(links))
    
    people = []
    seen = set()
    for a in links:
        href = a.get("href", "")
        if "/url?q=" in href:
            href = href.split("/url?q=")[1].split("&")[0]
        href = href.split("?")[0].rstrip("/")
        if "linkedin.com/in/" not in href or href in seen:
            continue
        seen.add(href)
        
        # Get title
        h3 = a.xpath('.//h3')
        title = h3[0].text_content() if h3 else href.split("/in/")[-1].replace("-", " ").title()
        
        # Clean
        clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
        parts = [pt.strip() for pt in re.split(r'[-–—|:]', clean_title) if pt.strip()]
        
        name = parts[0] if parts else "Hiring Specialist"
        headline = " - ".join(parts[1:]) if len(parts) > 1 else f"{role} at {company}"
        
        people.append({
            "name": name,
            "headline": headline,
            "company": company,
            "profile_url": href
        })
        
    print("Extracted count:", len(people))
    for p in people:
        print("->", p["name"], "|", p["headline"])
        print("   URL:", p["profile_url"])

if __name__ == "__main__":
    test_engines_xpath("Google", "Technical Recruiter")
