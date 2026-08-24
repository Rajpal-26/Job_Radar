import requests
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://in.indeed.com/",
}

session = requests.Session()
# 1. Homepage
r1 = session.get("https://in.indeed.com/", headers=headers, timeout=10)
print("Homepage status:", r1.status_code)

# 2. Search URL
search_url = "https://in.indeed.com/jobs?q=DevOps+Engineer&l=Bengaluru%2C+Karnataka&fromage=7"
r2 = session.get(search_url, headers=headers, timeout=10)
print("Search status:", r2.status_code)
print("Search title in HTML:", re.search(r'<title>(.*?)</title>', r2.text, re.I).group(1) if re.search(r'<title>(.*?)</title>', r2.text, re.I) else "No title")

# Check window._initialData or job cards in HTML
if "mosaic-provider-jobcards" in r2.text or "job_seen_beacon" in r2.text:
    print("SUCCESS: Found jobcards in HTML response!")
    # Parse window._initialData
    m = re.search(r'window\._initialData\s*=\s*({.*?});</script>', r2.text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            results = data.get("hostData", {}).get("getJobData", {}).get("results", [])
            print("Parsed jobs from initialData:", len(results))
        except Exception as e:
            print("JSON parse error:", e)
