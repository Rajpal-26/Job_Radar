import requests
import lxml.html
import re
import urllib.parse

def inspect_bing(company="Razorpay", role="Technical Recruiter"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    query = f'site:linkedin.com/in/ "{company}" {role}'
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    
    r = requests.get(url, headers=headers, timeout=10)
    doc = lxml.html.fromstring(r.text)
    
    results = doc.xpath('//li[contains(@class, "b_algo")]')
    print("Found b_algo items:", len(results))
    
    for item in results[:5]:
        title_el = item.xpath('.//h2/a')
        snippet_el = item.xpath('.//p')
        if title_el:
            href = title_el[0].get("href", "")
            title = title_el[0].text_content().strip()
            snippet = snippet_el[0].text_content().strip() if snippet_el else ""
            print(f"Title: {title}")
            print(f"Link: {href}")
            print(f"Snippet: {snippet}\n")

if __name__ == "__main__":
    inspect_bing("Swiggy", "Technical Recruiter")
