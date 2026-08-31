import sys, os
sys.path.insert(0, os.path.abspath("."))
from scrapers.recruiter_people_scraper import search_company_decision_makers

companies = [
    "supersourcing technologies pvt ltd",
    "Swiggy",
    "Razorpay",
    "Google",
    "DataHire Systems Pvt Ltd",
    "Acme Robotics"
]

for c in companies:
    res = search_company_decision_makers(c, "HR Manager", "India")
    print(f"\n==================== COMPANY: {res['company']} ====================")
    for m in res['members'][:3]:
        print(f"[Name] {m['name']} ({m['initials']})")
        print(f"  [Pos] {m['position']}")
        print(f"  [Exp] {m['company']} | {m['experience']}")
        print(f"  [URL] {m['profile_url']}")
