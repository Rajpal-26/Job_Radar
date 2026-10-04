# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import requests

resp = requests.post("http://127.0.0.1:5000/api/search_recruiters", json={
    "company": "Infosys",
    "recruiter_keyword": "Talent Acquisition",
    "location": "India"
})

data = resp.json()
print("Flask API Success:", data.get("success"))
members = data.get("data", {}).get("members", [])
print(f"Flask API Found {len(members)} genuine members for Infosys:")
for m in members[:5]:
    print(f" -> {m['name']} | {m['position']} | {m['location']} | {m['profile_url']}")
