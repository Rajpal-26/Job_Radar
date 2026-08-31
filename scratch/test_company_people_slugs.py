COMPANY_SLUG_MAP = {
    "gammastack": "gammastack",
    "thoughtwin": "thoughtwin-it-solutions-pvt-ltd",
    "thoughtwin it solutions": "thoughtwin-it-solutions-pvt-ltd",
    "supersourcing": "supersourcing",
    "supersourcing technologies pvt ltd": "supersourcing",
    "razorpay": "razorpay",
    "swiggy": "swiggy-in",
    "zomato": "zomato",
    "google": "google",
    "microsoft": "microsoft",
    "amazon": "amazon",
    "cred": "cred_club",
    "flipkart": "flipkart",
    "zepto": "zeptonow",
    "meesho": "meesho",
    "phonepe": "phonepe-internet",
    "zerodha": "zerodha",
    "groww": "groww-in",
    "infosys": "infosys",
    "tcs": "tata-consultancy-services",
    "wipro": "wipro"
}

def get_company_people_url(company_name, keyword="HR"):
    clean = company_name.lower().strip()
    slug = None
    for k, v in COMPANY_SLUG_MAP.items():
        if k in clean or clean in k:
            slug = v
            break
    if not slug:
        import re
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', clean).strip('-')
    
    if keyword:
        import urllib.parse
        return f"https://www.linkedin.com/company/{slug}/people/?keywords={urllib.parse.quote(keyword)}"
    return f"https://www.linkedin.com/company/{slug}/people/"

if __name__ == "__main__":
    for c in ["GammaStack", "ThoughtWin", "supersourcing technologies pvt ltd", "Razorpay", "Swiggy", "Acme Software"]:
        print(f"{c} -> {get_company_people_url(c, 'HR Manager')}")
