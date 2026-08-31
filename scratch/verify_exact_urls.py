import requests

for comp in ["GammaStack", "ThoughtWin"]:
    r = requests.post("http://127.0.0.1:5000/api/search_recruiters", json={
        "company": comp,
        "recruiter_keyword": "HR Manager",
        "location": "Indore, India"
    })
    data = r.json()
    print(f"\n==================== {data['data']['company']} ====================")
    for m in data['data']['members']:
        print(f"[Name] {m['name']} | {m['position']}")
        print(f"  [Link] {m['profile_url']}")
