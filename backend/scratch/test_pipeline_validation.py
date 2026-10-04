# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import time
import random
import re
import urllib.parse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from scrapers.stealth_driver import create_stealth_context

HR_KEYWORDS = [
    "hr", "talent", "recruiter", "recruitment", "hiring", "people", 
    "human resources", "staffing", "talent acquisition", "hrbp", 
    "sourcing", "headhunter", "chro", "people operations", "talent partner"
]

NON_HR_NOISE = [
    "lawyer", "attorney", "doctor", "physician", "teacher", "underviser", 
    "counsel", "advocate", "student at", "high school", "intern at non"
]

def clean_serp_title(raw_text: str, target_company: str) -> tuple[str, str]:
    text = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', raw_text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    target_line = lines[-1] if lines else text
    for l in lines:
        if (' - ' in l or ' | ' in l or ' – ' in l) and not l.lower().startswith(('linkedin', 'http')):
            target_line = l
            break

    clean = target_line
    clean = re.sub(r'^(?:Linkedin|LinkedIn)[^\n\r]*?(?=[A-Z][a-z]+|\b[A-Z]{2,}\b)', '', clean).strip()
    clean = re.sub(r'https?://\S+', '', clean).strip()
    clean = re.sub(r'\s*\|\s*LinkedIn.*$', '', clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r'\s*[-–—|]\s*LinkedIn.*$', '', clean, flags=re.IGNORECASE).strip()

    parts = [p.strip() for p in re.split(r'\s*[-–—|]\s*', clean) if p.strip()]
    if len(parts) >= 2:
        name = parts[0]
        if name.lower() in ["linkedin", "more", "anytime", "in", "view", "join", "sign in"]:
            name = parts[1]
            title = " - ".join(parts[2:])
        else:
            title = " - ".join(parts[1:])
        title = re.sub(rf'\s*(?:at|@|-)\s*{re.escape(target_company)}.*$', '', title, flags=re.IGNORECASE).strip()
        return name, title or f"Talent Acquisition at {target_company}"
    elif len(parts) == 1:
        return parts[0], f"HR at {target_company}"
    return "LinkedIn Member", f"Recruiter at {target_company}"

def extract_clean_location(snippet: str, default_loc: str = "India") -> str:
    if not snippet:
        return default_loc or "India"
    loc_match = re.search(r'(?:Location|Based in)[:\s]+([^·•\n,]+(?:,\s*[^·•\n,]+){1,2})', snippet, re.IGNORECASE)
    if loc_match:
        return loc_match.group(1).strip()
    city_match = re.search(r'\b(Bangalore|Bengaluru|Indore|Mumbai|Delhi|Hyderabad|Pune|Gurugram|Gurgaon|Noida|Chennai|Ahmedabad|Kolkata|Chandigarh|Jaipur|Kochi|San Francisco|New York|London|Singapore|Dubai|Berlin)\b(?:,\s*([A-Za-z\s]+))?', snippet, re.IGNORECASE)
    if city_match:
        city = city_match.group(1).strip()
        region = city_match.group(2).strip() if city_match.group(2) else ""
        return f"{city}, {region}".rstrip(', ')
    return default_loc or "India"

def is_valid_profile(title_raw: str, snippet_raw: str, clean_url: str, target_company: str, user_keywords: list) -> bool:
    combined = f"{title_raw} {snippet_raw}".lower()
    comp_clean = target_company.lower().strip()
    comp_tokens = [tok for tok in re.split(r'[^a-zA-Z0-9]+', comp_clean) if len(tok) >= 3]

    # Check for other company in title
    match_at_other = re.search(r'\b(?:at|@)\s+([A-Za-z0-9\s&.-]{3,30})', title_raw)
    if match_at_other:
        detected_comp = match_at_other.group(1).lower().strip()
        if not any(tok in detected_comp for tok in comp_tokens) and len(detected_comp) > 3:
            if not any(tok in snippet_raw.lower() for tok in comp_tokens):
                return False

    if any(noise in combined for noise in NON_HR_NOISE):
        return False

    user_kws = [k.lower().strip() for k in user_keywords if k.strip()]
    if user_kws:
        has_kw = any(k in combined for k in user_kws) or any(syn in combined for syn in HR_KEYWORDS)
        if not has_kw:
            return False
    else:
        if not any(syn in combined for syn in HR_KEYWORDS):
            return False

    return True

def scrape_linkedin_recruiters(company: str, keywords: list = None, location: str = "India", limit: int = 15):
    """
    LinkedIn Recruiter Scraper matching the architecture of scrapers/linkedin.py.
    """
    all_profiles = []
    seen_links = set()

    comp_clean = company.strip()
    user_kws = [k.strip() for k in (keywords or []) if k.strip()] or ["HR", "Talent Acquisition"]
    loc_str = f" {location.strip()}" if (location and location.strip().lower() != "any") else ""

    queries = []
    for kw in user_kws:
        if loc_str:
            queries.append(f'site:linkedin.com/in/ "{comp_clean}" "{kw}"{loc_str}')
        queries.append(f'site:linkedin.com/in/ "{comp_clean}" "{kw}"')
    queries.extend([
        f'site:linkedin.com/in/ "{comp_clean}" "Talent Acquisition"',
        f'site:linkedin.com/in/ "{comp_clean}" "Technical Recruiter"',
        f'site:linkedin.com/in/ "{comp_clean}" "HR Manager"'
    ])

    deduped_queries = []
    for q in queries:
        if q not in deduped_queries:
            deduped_queries.append(q)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ]
        )
        context = create_stealth_context(browser, locale="en-IN")
        page = context.new_page()

        for q in deduped_queries[:5]:
            if len(all_profiles) >= limit:
                break

            page_offsets = [0, 11] if len(all_profiles) < 5 else [0]
            for offset in page_offsets:
                if len(all_profiles) >= limit:
                    break

                search_url = f"https://search.yahoo.com/search?p={urllib.parse.quote(q)}" + (f"&b={offset}" if offset > 0 else "")
                try:
                    page.goto(search_url, wait_until="domcontentloaded", timeout=12000)
                    time.sleep(random.uniform(0.6, 1.0))

                    items = page.evaluate("""() => {
                        const results = [];
                        document.querySelectorAll('div.algo, li div.dd, #web ol li').forEach(el => {
                            const a = el.querySelector('h3 a, a.fz-20, a');
                            const snip = el.querySelector('div.compText, p.lh-16, .lh-16, div.lh-16');
                            if (a && a.href) {
                                results.push({
                                    title: (a.innerText || '').trim(),
                                    href: a.href,
                                    snippet: snip ? (snip.innerText || '').trim() : ''
                                });
                            }
                        });
                        return results;
                    }""")

                    for it in items:
                        if len(all_profiles) >= limit:
                            break

                        raw_href = it['href']
                        m = re.search(r'/RU=([^/]+)/', raw_href)
                        clean_url = urllib.parse.unquote(m.group(1)) if m else raw_href

                        if "linkedin.com/in/" not in clean_url:
                            continue

                        clean_url = re.sub(r'\?.*$', '', clean_url).rstrip('/')
                        if clean_url in seen_links:
                            continue

                        title_raw = it['title']
                        snippet_raw = it['snippet']

                        if not title_raw or len(title_raw) < 3:
                            continue

                        if not is_valid_profile(title_raw, snippet_raw, clean_url, comp_clean, user_kws):
                            continue

                        name, title = clean_serp_title(title_raw, comp_clean)
                        if not name or name.lower() in ["linkedin", "more", "anytime", "click here", "sign in", "view", "join"]:
                            continue

                        loc = extract_clean_location(snippet_raw, location or "India")
                        initials = "".join([w[0].upper() for w in name.split()[:2] if w])

                        seen_links.add(clean_url)
                        all_profiles.append({
                            "name": name,
                            "position": title,
                            "company": comp_clean,
                            "department": "Talent Acquisition / HR",
                            "experience": "Verified On LinkedIn",
                            "location": loc,
                            "initials": initials,
                            "verified": True,
                            "profile_url": clean_url,
                            "direct_profile_url": clean_url,
                            "snippet": snippet_raw[:250]
                        })

                except Exception as e:
                    pass

                time.sleep(random.uniform(0.3, 0.6))

        browser.close()

    return all_profiles

if __name__ == "__main__":
    test_companies = [
        ("GammaStack", ["HR", "Talent Acquisition"]),
        ("Thoughtwin", ["Talent Acquisition", "Technical Recruiter"]),
        ("Infosys", ["Talent Acquisition Lead", "HRBP"])
    ]
    for comp, kws in test_companies:
        print(f"\n================ TEST: {comp} (Keywords: {kws}) ================")
        res = scrape_linkedin_recruiters(comp, kws, "India", limit=6)
        print(f"Scraped {len(res)} verified profiles:")
        for r in res:
            print(f" * {r['name']} | {r['position']} | {r['location']} | {r['profile_url']}")
