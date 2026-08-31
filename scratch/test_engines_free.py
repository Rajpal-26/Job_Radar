import requests
import lxml.html
import urllib.parse
import re

def test_searches(company="Razorpay", role="Technical Recruiter"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    # 1. Mojeek
    q = f'site:linkedin.com/in/ "{company}" "{role}"'
    try:
        r = requests.get(f"https://www.mojeek.com/search?q={urllib.parse.quote(q)}", headers=headers, timeout=10)
        print("Mojeek status:", r.status_code)
        doc = lxml.html.fromstring(r.text)
        links = doc.xpath('//a[contains(@href, "linkedin.com/in/")]')
        print("Mojeek LinkedIn links:", len(links))
        for l in links[:3]:
            print("Mojeek URL:", l.get("href"), "Title:", l.text_content())
    except Exception as e:
        print("Mojeek error:", e)

    # 2. Qwant / Swisscows / Ecosia
    try:
        r = requests.get(f"https://www.ecosia.org/search?q={urllib.parse.quote(q)}", headers=headers, timeout=10)
        print("Ecosia status:", r.status_code)
        doc = lxml.html.fromstring(r.text)
        links = doc.xpath('//a[contains(@href, "linkedin.com/in/")]')
        print("Ecosia LinkedIn links:", len(links))
        for l in links[:3]:
            print("Ecosia URL:", l.get("href"), "Title:", l.text_content())
    except Exception as e:
        print("Ecosia error:", e)

if __name__ == "__main__":
    test_searches()
