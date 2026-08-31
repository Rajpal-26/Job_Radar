import requests
import lxml.html
import re
import urllib.parse
import json

def test_google_xray(company="Razorpay", role="Technical Recruiter"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
    }
    
    # Let's test multiple query patterns on Google & Bing & DuckDuckGo
    queries = [
        f'site:linkedin.com/in/ "{company}" {role}',
        f'"{company}" "{role}" "linkedin.com/in"',
        f'site:in.linkedin.com/in/ "{company}" "{role}"',
    ]
    
    for q in queries:
        print(f"\n--- Testing Query: {q} ---")
        # 1. Bing
        bing_url = f"https://www.bing.com/search?q={urllib.parse.quote(q)}"
        try:
            r = requests.get(bing_url, headers=headers, timeout=10)
            doc = lxml.html.fromstring(r.text)
            links = doc.xpath('//li[contains(@class, "b_algo")]')
            print(f"Bing found {len(links)} items")
            for it in links[:3]:
                h2 = it.xpath('.//h2/a')
                if h2:
                    print("  Bing Title:", h2[0].text_content().strip())
                    print("  Bing Href:", h2[0].get("href"))
        except Exception as e:
            print("  Bing error:", e)

if __name__ == "__main__":
    test_google_xray()
