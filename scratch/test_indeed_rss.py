import requests
import xml.etree.ElementTree as ET

url = "https://in.indeed.com/rss?q=DevOps+Engineer&l=Bengaluru"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

print("Fetching RSS feed from:", url)
try:
    resp = requests.get(url, headers=headers, timeout=10)
    print("RSS Status code:", resp.status_code)
    if resp.status_code == 200:
        root = ET.fromstring(resp.text)
        items = root.findall(".//item")
        print("RSS Items count:", len(items))
        if items:
            title = items[0].find("title")
            print("First RSS item title:", title.text if title is not None else "N/A")
    else:
        print("RSS response snippet:", resp.text[:200])
except Exception as e:
    print("RSS exception:", e)
