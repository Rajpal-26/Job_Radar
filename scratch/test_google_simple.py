import requests
import json
import urllib.parse
import re
import lxml.html

def search_people_multi(company="Razorpay", keyword="Technical Recruiter"):
    # Target exact LinkedIn query
    query = f"{company} {keyword} linkedin"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    
    r = requests.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=headers, timeout=10)
    print("DDG POST status:", r.status_code)
    
    doc = lxml.html.fromstring(r.text)
    links = doc.xpath('//a[contains(@class, "result__url")]/@href | //a[contains(@class, "result__snippet")]/@href | //a[contains(@class, "result__title")]/@href')
    print("Links count:", len(links))
    
    people = []
    seen = set()
    for res in doc.cssselect(".result"):
        t_el = res.cssselect(".result__title a")
        s_el = res.cssselect(".result__snippet")
        if not t_el:
            continue
        href = t_el[0].get("href", "")
        if "uddg=" in href:
            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
            
        if "linkedin.com/in/" in href:
            clean_url = href.split("?")[0].rstrip("/")
            if clean_url in seen:
                continue
            seen.add(clean_url)
            
            title_text = t_el[0].text_content().strip()
            snippet_text = s_el[0].text_content().strip() if s_el else ""
            
            # Clean title
            clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', title_text, flags=re.IGNORECASE)
            clean_title = re.sub(r'\s*-\s*LinkedIn.*$', '', clean_title, flags=re.IGNORECASE)
            parts = [pt.strip() for pt in re.split(r'[-–—|:]', clean_title) if pt.strip()]
            
            name = parts[0] if parts else "Hiring Specialist"
            headline = " - ".join(parts[1:]) if len(parts) > 1 else (snippet_text[:80] or f"{keyword} at {company}")
            
            people.append({
                "name": name,
                "headline": headline,
                "company": company,
                "profile_url": clean_url,
                "snippet": snippet_text
            })
            
    print("People extracted:", len(people))
    for p in people:
        print("->", p["name"], "||", p["headline"])
        print("   URL:", p["profile_url"])
        print()

if __name__ == "__main__":
    search_people_multi("Swiggy", "Technical Recruiter")
