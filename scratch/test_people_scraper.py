import requests
import lxml.html
import re
import urllib.parse

def scrape_linkedin_people(company, role="Technical Recruiter", location="India", limit=12):
    query = f'site:linkedin.com/in/ "{company}" "{role}"'
    if location:
        query += f' "{location}"'
    
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://html.duckduckgo.com/",
    }
    
    people = []
    seen_urls = set()
    
    try:
        resp = requests.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=headers, timeout=10)
        if resp.status_code == 200:
            doc = lxml.html.fromstring(resp.text)
            results = doc.cssselect(".result")
            for r in results:
                title_nodes = r.cssselect(".result__title a")
                snippet_nodes = r.cssselect(".result__snippet")
                
                if not title_nodes:
                    continue
                
                raw_title = title_nodes[0].text_content().strip()
                raw_link = title_nodes[0].get("href", "")
                raw_snippet = snippet_nodes[0].text_content().strip() if snippet_nodes else ""
                
                if "uddg=" in raw_link:
                    actual_url = urllib.parse.unquote(raw_link.split("uddg=")[1].split("&")[0])
                else:
                    actual_url = raw_link
                
                if "linkedin.com/in/" not in actual_url:
                    continue
                
                # Deduplicate by profile URL
                clean_url = actual_url.split("?")[0].rstrip("/")
                if clean_url in seen_urls:
                    continue
                seen_urls.add(clean_url)
                
                # Parse Name and Headline
                clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', raw_title, flags=re.IGNORECASE)
                parts = [p.strip() for p in re.split(r'[-–—|:]', clean_title) if p.strip()]
                
                name = parts[0] if parts else "Hiring Specialist"
                if len(parts) > 1:
                    headline = " - ".join(parts[1:])
                else:
                    headline = raw_snippet[:90] if raw_snippet else f"{role} at {company}"
                
                # Extract clean location if mentioned in snippet
                loc_match = re.search(r'(Bengaluru|Bangalore|Mumbai|Delhi|Noida|Gurgaon|Gurugram|Hyderabad|Pune|Chennai|Indore|San Francisco|New York|London|Remote)', raw_snippet, re.IGNORECASE)
                loc_str = loc_match.group(0).capitalize() if loc_match else (location or "India")
                
                people.append({
                    "name": name,
                    "headline": headline,
                    "company": company,
                    "location": loc_str,
                    "profile_url": clean_url,
                    "snippet": raw_snippet
                })
                
                if len(people) >= limit:
                    break
    except Exception as e:
        print("Scrape error:", e)
        
    return people

if __name__ == "__main__":
    results = scrape_linkedin_people("Swiggy", "Technical Recruiter", "India", 6)
    print("Found:", len(results))
    for p in results:
        print(f"[{p['name']}] - {p['headline']}")
        print(f"  Location: {p['location']}")
        print(f"  URL: {p['profile_url']}\n")
