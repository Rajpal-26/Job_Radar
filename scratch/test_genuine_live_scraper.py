import requests
import re
import urllib.parse
import lxml.html
import json
from playwright.sync_api import sync_playwright

def test_bing_html_direct(company="Razorpay", role="Technical Recruiter"):
    # Bing search with proper headers
    query = f'site:linkedin.com/in "{company}" "{role}"'
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&setlang=en-us"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "SRCHHPGUSR=ADLT=OFF&NRSLT=20",
    }
    
    print(f"--- 1. Testing Bing HTML for {company} ---")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        doc = lxml.html.fromstring(r.text)
        
        items = doc.xpath('//li[contains(@class, "b_algo")]')
        print(f"Bing returned {len(items)} items")
        
        for it in items:
            title_node = it.xpath('.//h2/a')
            snippet_node = it.xpath('.//p')
            cite_node = it.xpath('.//cite')
            if not title_node:
                continue
            title = title_node[0].text_content().strip()
            href = title_node[0].get("href", "")
            snippet = snippet_node[0].text_content().strip() if snippet_node else ""
            cite = cite_node[0].text_content().strip() if cite_node else ""
            
            # Decode Bing redirect URL
            actual_url = href
            if "/ck/a?" in href and "u=" in href:
                import base64
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                u_val = parsed.get("u", [""])[0]
                if u_val.startswith("a1"):
                    b64_str = u_val[2:]
                    padding = 4 - (len(b64_str) % 4)
                    if padding and padding < 4:
                        b64_str += "=" * padding
                    try:
                        actual_url = base64.b64decode(b64_str).decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                        
            print(f"Title: {title}")
            print(f"Cite: {cite}")
            print(f"URL: {actual_url}")
            print(f"Snippet: {snippet[:100]}\n")
    except Exception as e:
        print("Bing Error:", e)

def test_duckduckgo_html(company="Razorpay", role="Technical Recruiter"):
    query = f'site:linkedin.com/in/ "{company}" "{role}"'
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://html.duckduckgo.com/",
    }
    
    print(f"\n--- 2. Testing DuckDuckGo HTML for {company} ---")
    try:
        r = requests.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=headers, timeout=10)
        doc = lxml.html.fromstring(r.text)
        results = doc.xpath('//div[contains(@class, "result")]')
        print(f"DDG returned {len(results)} results")
        for res in results:
            t = res.xpath('.//a[contains(@class, "result__url")]/@href | .//h2/a/@href')
            title = res.xpath('.//h2/a/text()')
            if t:
                href = t[0]
                if "uddg=" in href:
                    href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                print(f"DDG Title: {title} | URL: {href}")
    except Exception as e:
        print("DDG Error:", e)

if __name__ == "__main__":
    test_bing_html_direct("Razorpay", "Technical Recruiter")
    test_duckduckgo_html("Razorpay", "Technical Recruiter")
