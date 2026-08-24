import requests
import json
import re
from datetime import datetime

url = "https://www.shine.com/job-search/devops-jobs-in-bangalore?q=DevOps&loc=Bengaluru&sort=1"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
resp = requests.get(url, headers=headers)
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>([^<]+)</script>', resp.text)
if m:
    data = json.loads(m.group(1))
    results = data["props"]["pageProps"]["initialState"]["jsrp"]["searchresult"]["data"]["results"]
    print("Today is:", datetime.today().strftime("%Y-%m-%d"))
    print("First 5 Shine jobs:")
    for r in results[:5]:
        print("Title:", r.get("jJT"), "jPDate:", r.get("jPDate"))
else:
    print("No next data found")
