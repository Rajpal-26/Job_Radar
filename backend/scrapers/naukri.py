# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""Naukri.com public job search scraper (no login required).

Naukri uses Akamai Bot Manager and aggressively blocks anything that looks
like a headless browser. We get around that with two tricks:

1. **launch_persistent_context** — saves cookies + fingerprint between runs
   so Akamai treats us like a returning user (gives us a trust cookie on
   first warmup visit).
2. **`--headless=new` flag** + `headless=False` in Playwright — uses
   Chrome's "new" headless mode (no visible window) but Playwright doesn't
   add the `HeadlessChrome` token to the user-agent, so Akamai doesn't
   flag us. The window is never visible.

URL format:
    https://www.naukri.com/{role-slug}-jobs-in-{city-slug}[-{page}]
        ?k={role}&l={city}&jobAge={days}[&experience={years}]

Filters:
    jobAge      — days since posted: 1, 3, 7, 15, 30 (Naukri honors any int)
    experience  — exact years of experience (0..30)

We intentionally don't append `&sort=date` because that surfaces low-relevance
"just posted" agency listings. The default relevance sort combined with a
jobAge window gives the best balance of "fresh AND relevant".
"""

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import time
import random
import re
import os
from datetime import datetime, timedelta


# Display city -> Naukri slug (lowercase, in URL path AND l= param)
NAUKRI_CITIES = {
    "Bengaluru":  "bengaluru",
    "Hyderabad":  "hyderabad",
    "Mumbai":     "mumbai",
    "Pune":       "pune",
    "Chennai":    "chennai",
    "Delhi":      "delhi-ncr",
    "Noida":      "noida",
    "Gurugram":   "gurgaon",
    "Indore":     "indore",
    "Ahmedabad":  "ahmedabad",
    "Nagpur":     "nagpur",
    "Chandigarh": "chandigarh",
    "Mohali":     "mohali",
    "Kochi":      "kochi",
    "Kolkata":    "kolkata",
    "Surat":      "surat",
    "Jaipur":     "jaipur",
    "Coimbatore": "coimbatore",
}

# Profile directory — persisted between scraper invocations so Akamai keeps
# trusting us. Created on first run.
_PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "_naukri_profile")


def _slug(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _parse_naukri_date(text):
    if not text:
        return datetime.today().strftime("%Y-%m-%d")
    text = text.lower().strip()
    today = datetime.today()
    if "today" in text or "just" in text or "few hours" in text:
        return today.strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*day", text)
    if m:
        return (today - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*week", text)
    if m:
        return (today - timedelta(weeks=int(m.group(1)))).strftime("%Y-%m-%d")
    m = re.search(r"(\d+)\s*month", text)
    if m:
        return (today - timedelta(days=int(m.group(1)) * 30)).strftime("%Y-%m-%d")
    return today.strftime("%Y-%m-%d")


def _build_url(role, city_slug, city_query, job_age, experience, page=1):
    role_slug = _slug(role)
    path = f"{role_slug}-jobs-in-{city_slug}"
    if page > 1:
        path += f"-{page}"
    qs = [
        f"k={role.replace(' ', '%20')}",
        f"l={city_query}",
        f"jobAge={int(job_age)}",
    ]
    if experience is not None and experience != "":
        qs.append(f"experience={int(experience)}")
    return f"https://www.naukri.com/{path}?" + "&".join(qs)


def _normalize_locations(locations_input, valid_cities_dict):
    if not locations_input:
        return list(valid_cities_dict.keys())[:1]
    if isinstance(locations_input, str):
        raw = [c.strip() for c in locations_input.split(",") if c.strip()]
    else:
        raw = []
        for item in locations_input:
            for part in str(item).split(","):
                if part.strip():
                    raw.append(part.strip())
    valid = []
    for loc in raw:
        for k in valid_cities_dict:
            if loc.lower() == k.lower():
                if k not in valid:
                    valid.append(k)
                break
    return valid or [list(valid_cities_dict.keys())[0]]


def scrape_naukri(role, city="Bengaluru", job_age_days=7, limit=10, experience=None):
    """
    role:          free-text role (e.g. "devops engineer")
    city:          display city name, list of cities, or comma-separated cities
    job_age_days:  int (1, 3, 7, 15, 30)
    limit:         max results
    experience:    optional int years (0..30), or None for any
    """
    if not role.strip():
        raise ValueError("role is required")

    locations = _normalize_locations(city, NAUKRI_CITIES)

    import tempfile
    user_dir = tempfile.mkdtemp(prefix="naukri_ctx_")

    all_jobs = []
    seen_links = set()

    # Support multiple job roles separated by commas
    roles = [r.strip() for r in role.split(",") if r.strip()]
    if not roles:
        roles = [role]

    with sync_playwright() as p:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=AutomationControlled",
            "--headless=new",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        init_js = """
            Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
            Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3,4,5]});
            Object.defineProperty(navigator,'languages',{get:()=>['en-IN','en']});
            window.chrome = {runtime:{}, loadTimes:function(){}, csi:function(){}, app:{}};
        """
        browser = None
        try:
            ctx = p.chromium.launch_persistent_context(
                user_dir,
                headless=False,                  # Playwright doesn't add HeadlessChrome
                viewport={"width": 1366, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/132.0.0.0 Safari/537.36"
                ),
                locale="en-IN",
                timezone_id="Asia/Kolkata",
                args=args,
            )
            ctx.add_init_script(init_js)
        except Exception as e:
            print(f"[Naukri] Persistent context launch failed ({e}), falling back to non-persistent launch.")
            browser = p.chromium.launch(headless=True, args=args)
            ctx = browser.new_context(
                viewport={"width": 1366, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/132.0.0.0 Safari/537.36"
                ),
                locale="en-IN",
                timezone_id="Asia/Kolkata",
            )
            ctx.add_init_script(init_js)

        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # Warmup on homepage to establish Akamai trust cookies
        try:
            page.goto("https://www.naukri.com/", wait_until="domcontentloaded", timeout=20000)
            time.sleep(random.uniform(3.0, 4.5))
        except Exception:
            pass

        max_pages = 5
        active_combinations = [(c, r) for c in locations for r in roles]

        for page_idx in range(max_pages):
            if len(all_jobs) >= limit or not active_combinations:
                break

            page_num = page_idx + 1
            next_active = []

            for c, r in active_combinations:
                if len(all_jobs) >= limit:
                    break

                city_slug = NAUKRI_CITIES[c]
                url = _build_url(r, city_slug, city_slug, job_age_days, experience, page_num)
                print(f"[Naukri] Fetching: {url}")

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(random.uniform(3.5, 5.0))

                    # Quick block detection
                    title = page.title() or ""
                    if "Access Denied" in title or "Just a moment" in title:
                        print(f"[Naukri] BLOCKED on page {page_num} for role '{r}' (title={title!r}). Skipping role.")
                        continue

                    # Cards lazy-load on scroll
                    for _ in range(2):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(1.2)

                    cards = page.query_selector_all("div.srp-jobtuple-wrapper")
                    if not cards:
                        cards = page.query_selector_all("div.cust-job-tuple")
                    if not cards:
                        cards = page.query_selector_all("article.jobTuple")
                    if not cards:
                        cards = page.query_selector_all("div[data-job-id]")

                    if not cards:
                        print(f"[Naukri] No cards on page {page_num} for role '{r}'")
                        continue  # Exhausted

                    found_this_page = 0
                    for card in cards:
                        if len(all_jobs) >= limit:
                            break
                        try:
                            title_el = card.query_selector("a.title")
                            title_txt = title_el.inner_text().strip() if title_el else ""
                            if not title_txt:
                                continue
                            link = (title_el.get_attribute("href") or "").strip() if title_el else ""
                            if not link:
                                continue
                            if not link.startswith("http"):
                                link = "https://www.naukri.com" + link
                            if link in seen_links:
                                continue

                            comp_el = card.query_selector("a.comp-name")
                            company = comp_el.inner_text().strip() if comp_el else "N/A"

                            rating_el = card.query_selector("a.rating span.main-2")
                            rating = rating_el.inner_text().strip() if rating_el else ""

                            exp_el = card.query_selector("span.expwdth") or card.query_selector("span.exp")
                            exp_text = exp_el.inner_text().strip() if exp_el else ""

                            sal_el = (
                                card.query_selector("span.sal-wrap span")
                                or card.query_selector("span.sal")
                                or card.query_selector("[class*='sal-wrap']")
                            )
                            salary = sal_el.inner_text().strip() if sal_el else ""

                            loc_el = card.query_selector("span.locWdth") or card.query_selector("span.loc")
                            loc_text = loc_el.inner_text().strip() if loc_el else city

                            desc_el = card.query_selector("span.job-desc")
                            desc = desc_el.inner_text().strip() if desc_el else ""

                            skills = [li.inner_text().strip() for li in card.query_selector_all("ul.tags-gt li")]

                            age_el = card.query_selector("span.job-post-day")
                            posted_raw = age_el.inner_text().strip() if age_el else ""
                            posted = _parse_naukri_date(posted_raw)

                            # Infer workplace type
                            combo = (title_txt + " " + loc_text + " " + desc).lower()
                            if "remote" in combo or "work from home" in combo:
                                workplace = "Remote"
                            elif "hybrid" in combo:
                                workplace = "Hybrid"
                            else:
                                workplace = "On-site"

                            seen_links.add(link)
                            all_jobs.append({
                                "Job Title": title_txt,
                                "Company": company,
                                "Location": loc_text,
                                "Posted": posted,
                                "Link": link,
                                "Experience": exp_text,
                                "Salary": salary,
                                "Rating": rating,
                                "Skills": ", ".join(skills),
                                "Description": desc,
                                "Workplace": workplace,
                                "Easy Apply": False,
                                "Apply Type": "Naukri Apply",
                            })
                            found_this_page += 1
                        except Exception as e:
                            print(f"[Naukri] Card error: {e}")
                            continue

                    print(f"[Naukri] Got {found_this_page} jobs from page {page_num} for city '{c}' role '{r}'")
                    next_active.append((c, r))

                except Exception as e:
                    print(f"[Naukri] Error fetching page {page_num} for city '{c}' role '{r}': {e}")

            active_combinations = next_active

        try:
            ctx.close()
        except Exception:
            pass
        if browser:
            try:
                browser.close()
            except Exception:
                pass

    def sort_key(j):
        try:
            return datetime.strptime(j["Posted"][:10], "%Y-%m-%d")
        except Exception:
            return datetime.min

    all_jobs.sort(key=sort_key, reverse=True)
    return all_jobs[:limit]
