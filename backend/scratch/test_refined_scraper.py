# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import asyncio
import re
import urllib.parse
from playwright.async_api import async_playwright

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

HR_SYNONYMS = [
    "hr", "talent", "recruiter", "recruitment", "hiring", "people", 
    "human resources", "staffing", "talent acquisition", "hrbp", 
    "sourcing", "headhunter", "chro", "people operations"
]

NON_HR_NOISE = [
    "lawyer", "attorney", "doctor", "physician", "teacher", "underviser", 
    "counsel", "advocate", "student at", "high school", "intern at non"
]

def is_aligned_profile(title_raw: str, snippet_raw: str, clean_url: str, target_company: str, user_keywords: list) -> bool:
    combined = f"{title_raw} {snippet_raw}".lower()
    comp_clean = target_company.lower().strip()
    comp_tokens = [tok for tok in re.split(r'[^a-zA-Z0-9]+', comp_clean) if len(tok) >= 3]

    # 1. Company Conflict Check:
    # If the title explicitly says "at <OtherCompany>", ensure it's not a completely different company
    match_at_other = re.search(r'\b(?:at|@)\s+([A-Za-z0-9\s&.-]{3,30})', title_raw)
    if match_at_other:
        detected_comp = match_at_other.group(1).lower().strip()
        # If detected company doesn't match target company tokens
        if not any(tok in detected_comp for tok in comp_tokens) and len(detected_comp) > 3:
            # Check if snippet confirms current employment at target company
            if not any(tok in snippet_raw.lower() for tok in comp_tokens):
                return False

    # 2. Reject obvious non-HR professions
    if any(noise in combined for noise in NON_HR_NOISE):
        return False

    # 3. Keyword / HR Role Check
    user_kws = [k.lower().strip() for k in user_keywords if k.strip()]
    if user_kws:
        has_kw = any(k in combined for k in user_kws) or any(syn in combined for syn in HR_SYNONYMS)
        if not has_kw:
            return False
    else:
        has_syn = any(syn in combined for syn in HR_SYNONYMS)
        if not has_syn:
            return False

    return True

async def test_scrape(company, keywords, location="India"):
    print(f"\n================ Running Scraper for: {company} (Keywords: {keywords}) ================")
    user_kws = [k.strip() for k in keywords if k.strip()] or ["HR", "Talent Acquisition"]
    loc_str = f" {location.strip()}" if (location and location.strip().lower() != "any") else ""
    
    queries = []
    for kw in user_kws:
        if loc_str:
            queries.append(f'site:linkedin.com/in/ "{company}" "{kw}"{loc_str}')
        queries.append(f'site:linkedin.com/in/ "{company}" "{kw}"')
    
    queries.extend([
        f'site:linkedin.com/in/ "{company}" "Talent Acquisition"',
        f'site:linkedin.com/in/ "{company}" "HR"',
        f'site:linkedin.com/in/ "{company}" "Recruiter"',
        f'site:linkedin.com/in/ "{company}" "Human Resources"'
    ])

    # Deduplicate
    unique_queries = []
    for q in queries:
        if q not in unique_queries:
            unique_queries.append(q)

    discovered = []
    seen_urls = set()

    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await ctx.new_page()

        for q in unique_queries[:5]:
            url = f"https://search.yahoo.com/search?p={urllib.parse.quote(q)}"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=12000)
                items = await page.evaluate("""() => {
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
                    raw_href = it['href']
                    m = re.search(r'/RU=([^/]+)/', raw_href)
                    clean_url = urllib.parse.unquote(m.group(1)) if m else raw_href
                    if "linkedin.com/in/" not in clean_url:
                        continue
                    clean_url = re.sub(r'\?.*$', '', clean_url).rstrip('/')
                    if clean_url in seen_urls:
                        continue

                    title_raw = it['title']
                    snippet_raw = it['snippet']

                    if not is_aligned_profile(title_raw, snippet_raw, clean_url, company, user_kws):
                        continue

                    name, title = clean_serp_title(title_raw, company)
                    if not name or name.lower() in ["linkedin", "more", "anytime", "click here", "sign in", "view", "join"]:
                        continue

                    loc = extract_clean_location(snippet_raw, location)
                    seen_urls.add(clean_url)
                    discovered.append({
                        "name": name,
                        "title": title,
                        "company": company,
                        "location": loc,
                        "url": clean_url,
                        "snippet": snippet_raw[:120]
                    })
            except Exception as e:
                pass
            await asyncio.sleep(0.4)

        await b.close()

    print(f"Total Aligned Profiles Found: {len(discovered)}")
    for d in discovered:
        print(f" * {d['name']} | {d['title']} | {d['location']} | {d['url']}")
    return discovered

if __name__ == "__main__":
    asyncio.run(test_scrape("GammaStack", ["HR", "Talent Acquisition"]))
    asyncio.run(test_scrape("Thoughtwin", ["Talent Acquisition", "Technical Recruiter"]))
    asyncio.run(test_scrape("Infosys", ["Talent Acquisition Lead", "HR Manager"]))
