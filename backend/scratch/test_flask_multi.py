# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import requests

def test_company(comp, kw):
    resp = requests.post("http://127.0.0.1:5000/api/search_recruiters", json={
        "company": comp,
        "recruiter_keyword": kw,
        "location": "India"
    })
    data = resp.json()
    members = data.get("data", {}).get("members", [])
    print(f"\n--- Flask API: {comp} ({kw}) -> {len(members)} Members ---")
    for m in members:
        print(f" * {m['name']} | {m['position']} | {m['location']} | {m['profile_url']}")

if __name__ == "__main__":
    test_company("Thoughtwin", "HR")
    test_company("GammaStack", "Talent Acquisition")
