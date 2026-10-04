# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import asyncio
import re
import urllib.parse
from playwright.async_api import async_playwright

def parse_serp_title(raw_text: str, company: str) -> tuple[str, str]:
    text = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', raw_text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    target_line = lines[-1] if lines else text
    for line in lines:
        if (' - ' in line or ' | ' in line or ' – ' in line) and not line.lower().startswith(('linkedin', 'http')):
            target_line = line
            break
            
    clean = target_line
    clean = re.sub(r'^(?:Linkedin|LinkedIn)[^\n\r]*?(?=[A-Z][a-z]+|\b[A-Z]{2,}\b)', '', clean).strip()
    clean = re.sub(r'https?://\S+', '', clean).strip()
    clean = re.sub(r'\s*\|\s*LinkedIn.*$', '', clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r'\s*[-–—|]\s*LinkedIn.*$', '', clean, flags=re.IGNORECASE).strip()
    
    parts = [p.strip() for p in re.split(r'\s*[-–—|]\s*', clean) if p.strip()]
    if len(parts) >= 2:
        name = parts[0]
        if name.lower() in ["linkedin", "more", "anytime", "in", "view", "join"]:
            name = parts[1]
            title = " - ".join(parts[2:])
        else:
            title = " - ".join(parts[1:])
        title = re.sub(rf'\s*(?:at|@|-)\s*{re.escape(company)}.*$', '', title, flags=re.IGNORECASE).strip()
        return name, title or f"Talent Acquisition at {company}"
    elif len(parts) == 1:
        return parts[0], f"HR Professional at {company}"
    return "LinkedIn Member", f"Recruiter at {company}"

def extract_location(snippet: str, default_loc: str = "India") -> str:
    if not snippet:
        return default_loc or "India"
    # Look for Location patterns like "Location: Indore, Madhya Pradesh, India" or "Bengaluru, Karnataka, India"
    loc_match = re.search(r'(?:Location|Based in)[:\s]+([^·•\n,]+(?:,\s*[^·•\n,]+){1,2})', snippet, re.IGNORECASE)
    if loc_match:
        return loc_match.group(1).strip()
    # City patterns
    city_match = re.search(r'\b(Bangalore|Bengaluru|Indore|Mumbai|Delhi|Hyderabad|Pune|Gurugram|Noida|Chennai|Ahmedabad|Kolkata|San Francisco|New York|London|Singapore|Dubai)\b(?:,\s*([A-Za-z\s]+))?', snippet, re.IGNORECASE)
    if city_match:
        city = city_match.group(1).strip()
        state_country = city_match.group(2).strip() if city_match.group(2) else ""
        return f"{city}, {state_country}".rstrip(', ')
    return default_loc or "India"

def validate_profile(title_raw: str, snippet_raw: str, clean_url: str, target_company: str, keywords: list) -> bool:
    combined = f"{title_raw} {snippet_raw}".lower()
    comp_clean = target_company.lower().strip()
    comp_tokens = [tok for tok in re.split(r'[^a-zA-Z0-9]+', comp_clean) if len(tok) >= 3]
    
    # 1. Company match
    has_company = any(tok in combined or tok in clean_url.lower() for tok in comp_tokens)
    if not has_company:
        return False
        
    # Check for other company
    match_other = re.search(r'\b(?:at|@)\s+([A-Za-z0-9\s&.-]{3,30})', title_raw)
    if match_other:
        detected = match_other.group(1).lower().strip()
        if not any(tok in detected for tok in comp_tokens) and len(detected) > 3:
            if comp_clean not in snippet_raw.lower():
                return False
                
    # 2. Keyword / HR Role match
    kws = [k.lower().strip() for k in keywords if k.strip()]
    if not kws:
        kws = ["hr", "talent", "recruiter", "people", "hiring", "human resources"]
    has_kw = any(k in combined for k in kws) or any(syn in combined for syn in ["hr", "talent", "recruiter", "hiring", "people operations", "human resource", "staffing"])
    if not has_kw:
        return False
        
    # Discard non-HR noise
    if any(noise in combined for noise in ["lawyer", "medical doctor", "physician", "attorney at law", "school student"]):
        return False
        
    return True

async def scrape_accurate_people(company: str, keywords: list, location: str = "India", limit: int = 15):
    print(f"\n================ Accurate Scraper: {company} | Keywords: {keywords} ================")
    discovered = []
    seen_urls = set()
    
    loc_str = f" {location.strip()}" if (location and location.strip().lower() != "any") else ""
    user_kws = [k.strip() for k in keywords if k.strip()] or ["HR", "Talent Acquisition"]
    
    queries = []
    for kw in user_kws:
        if loc_str:
            queries.append(f'site:linkedin.com/in/ "{company}" "{kw}"{loc_str}')
        queries.append(f'site:linkedin.com/in/ "{company}" "{kw}"')
    queries.extend([
        f'site:linkedin.com/in/ "{company}" "Talent Acquisition"',
        f'site:linkedin.com/in/ "{company}" "HR"',
        f'site:linkedin.com/in/ "{company}" "Recruiter"'
    ])
    
    # Deduplicate queries
    clean_queries = []
    for q in queries:
        if q not in clean_queries:
            clean_queries.append(q)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await ctx.new_page()

        for q in clean_queries:
            if len(discovered) >= limit:
                break
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
                    
                    if not validate_profile(title_raw, snippet_raw, clean_url, company, user_kws):
                        continue
                        
                    name, title = parse_serp_title(title_raw, company)
                    if not name or name.lower() in ["linkedin", "more", "anytime", "click here", "sign in", "view"]:
                        continue
                        
                    loc = extract_location(snippet_raw, location)
                    seen_urls.add(clean_url)
                    discovered.append({
                        "name": name,
                        "title": title,
                        "company": company,
                        "location": loc,
                        "url": clean_url,
                        "snippet": snippet_raw
                    })
                    
                    if len(discovered) >= limit:
                        break
            except Exception as e:
                pass
            await asyncio.sleep(0.4)
            
        await browser.close()
        
    print(f"Discovered {len(discovered)} validated profiles:")
    for d in discovered:
        print(f" -> {d['name']} | {d['title']} | {d['location']} | {d['url']}")
    return discovered

if __name__ == "__main__":
    asyncio.run(scrape_accurate_people("GammaStack", ["HR", "Talent Acquisition"]))
    asyncio.run(scrape_accurate_people("Thoughtwin", ["Talent Acquisition", "Technical Recruiter"]))
    asyncio.run(scrape_accurate_people("Infosys", ["Talent Acquisition Lead", "HR Manager"]))
