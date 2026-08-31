import requests
import lxml.html
import re
import urllib.parse

def test_engines(company="Razorpay", role="Technical Recruiter"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    # 1. Test Bing
    bing_query = f'site:linkedin.com/in/ "{company}" "{role}"'
    bing_url = f"https://www.bing.com/search?q={urllib.parse.quote(bing_query)}"
    print("Testing Bing:", bing_url)
    try:
        r = requests.get(bing_url, headers=headers, timeout=10)
        print("Bing status:", r.status_code, "Length:", len(r.text))
        doc = lxml.html.fromstring(r.text)
        links = doc.xpath('//a[contains(@href, "linkedin.com/in/")]/@href')
        print("Bing LinkedIn URLs found:", len(links), links[:3])
    except Exception as e:
        print("Bing error:", e)

    # 2. Test DuckDuckGo Lite
    ddg_url = f"https://lite.duckduckgo.com/lite/"
    try:
        r = requests.post(ddg_url, data={"q": bing_query}, headers=headers, timeout=10)
        print("DDG Lite status:", r.status_code, "Length:", len(r.text))
        doc = lxml.html.fromstring(r.text)
        links = doc.xpath('//a[contains(@href, "linkedin.com/in/")]/@href')
        print("DDG Lite LinkedIn URLs found:", len(links), links[:3])
    except Exception as e:
        print("DDG Lite error:", e)

if __name__ == "__main__":
    test_engines()
