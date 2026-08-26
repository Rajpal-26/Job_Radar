# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import re
import hashlib
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_numeric_salary(sal_str):
    """
    Parse annual salary string into estimated float in INR (LPA).
    Examples: '₹8 - 12 LPA' -> 8.0, '$80,000' -> 64.0 (converted), '50,000/month' -> 6.0
    """
    if not sal_str:
        return 0.0
    s = sal_str.lower().strip()
    
    # Check for LPA / Lakhs
    lpa_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)?\s*(\d+(?:\.\d+)?)?\s*(?:lpa|lakh|lacs|l)", s)
    if lpa_match:
        val1 = float(lpa_match.group(1))
        val2 = float(lpa_match.group(2)) if lpa_match.group(2) else val1
        return (val1 + val2) / 2.0
        
    # Check for monthly salaries (e.g. 30k/month, 40000 pm)
    pm_match = re.search(r"(\d+(?:,\d+)?)\s*(?:k|thousand)?\s*(?:/month|pm|per month)", s)
    if pm_match:
        raw_val = pm_match.group(1).replace(",", "")
        val = float(raw_val)
        if val < 1000 and "k" in s:
            val *= 1000
        return (val * 12) / 100000.0  # Convert to LPA
        
    # Check USD / $
    usd_match = re.search(r"\$\s*(\d+(?:,\d+)?)", s)
    if usd_match:
        usd = float(usd_match.group(1).replace(",", ""))
        inr_lpa = (usd * 85) / 100000.0  # Approx USD to INR LPA
        return inr_lpa

    return 0.0


def evaluate_keywords(job_or_text, include_kw=None, exclude_kw=None):
    """
    Smart evaluation of include and exclude keywords.
    - Exclude keywords are checked against the Job Title (with word boundaries) to prevent false positives.
    """
    if isinstance(job_or_text, dict):
        job = job_or_text
        title = (job.get("Job Title") or "").lower()
    else:
        title = (str(job_or_text) or "").lower()

    # 1. Exclude keywords check (Title level with word boundary)
    if exclude_kw:
        ex_terms = [k.strip().lower() for k in str(exclude_kw).split(",") if k.strip()]
        for term in ex_terms:
            if not term:
                continue
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, title):
                return False

    return True


def calculate_match_score(job, resume_text_or_skills, include_kw=None):
    """
    Calculate 0-100% Match Score based on skill/token overlap and keyword bonus.
    """
    base_score = 70

    job_text = f"{job.get('Job Title', '')} {job.get('Company', '')} {job.get('Description', '')} {job.get('Skills', '')} {job.get('Location', '')}".lower()
    job_tokens = set(re.findall(r"\b[a-zA-Z0-9+#\.\-]{2,}\b", job_text))

    stopwords = {"and", "the", "with", "for", "you", "that", "this", "from", "are", "have", "will", "our", "all", "your", "can", "work", "job", "about", "looking"}

    # Include Keyword Bonus
    kw_bonus = 0
    if include_kw:
        inc_tokens = [k.strip().lower() for k in re.split(r"[\s,]+", str(include_kw)) if k.strip()]
        matched_kw = [t for t in inc_tokens if re.search(r"\b" + re.escape(t) + r"\b", job_text)]
        if matched_kw:
            kw_bonus = min(25, len(matched_kw) * 15)

    if not resume_text_or_skills or not str(resume_text_or_skills).strip():
        return min(99, max(40, base_score + kw_bonus))

    resume_tokens = set(re.findall(r"\b[a-zA-Z0-9+#\.\-]{2,}\b", resume_text_or_skills.lower())) - stopwords
    if not resume_tokens or not job_tokens:
        return min(99, max(40, base_score + kw_bonus))

    matched = resume_tokens.intersection(job_tokens - stopwords)
    overlap_ratio = len(matched) / max(1, len(resume_tokens))

    # Title bonus match
    title_words = set(re.findall(r"\b[a-zA-Z0-9+#\.\-]{2,}\b", job.get('Job Title', '').lower())) - stopwords
    title_bonus = 0.2 if matched.intersection(title_words) else 0.0

    final_score = int(min(99, max(35, (overlap_ratio + title_bonus) * 80 + kw_bonus)))
    return final_score


def deduplicate_jobs(job_list):
    """
    Deduplicate jobs by MD5 hash of (company + title + primary city).
    Combines duplicate entries into one master job with combined Platforms list.
    """
    dedup_map = {}
    
    for job in job_list:
        comp = re.sub(r"[^\w]", "", (job.get("Company") or "").lower())
        title = re.sub(r"[^\w]", "", (job.get("Job Title") or "").lower())
        loc = (job.get("Location") or "").split(",")[0].strip().lower()
        loc = re.sub(r"[^\w]", "", loc)

        key_raw = f"{comp}_{title}_{loc}"
        key = hashlib.md5(key_raw.encode("utf-8")).hexdigest()

        platform = job.get("Platform") or job.get("Source") or "JobRadar"
        link = job.get("Link") or "#"

        if key in dedup_map:
            master = dedup_map[key]
            if platform not in master["Platforms"]:
                master["Platforms"].append(platform)
            if platform not in master["Platform_Links"]:
                master["Platform_Links"][platform] = link
            if not master.get("Salary") and job.get("Salary"):
                master["Salary"] = job["Salary"]
            if not master.get("Description") and job.get("Description"):
                master["Description"] = job["Description"]
        else:
            job_copy = dict(job)
            job_copy["Platforms"] = [platform]
            job_copy["Platform_Links"] = {platform: link}
            dedup_map[key] = job_copy

    return list(dedup_map.values())


def filter_and_rank_jobs(jobs, include_kw=None, exclude_kw=None, min_salary=0, workplace_mode=None, resume_text=None):
    """
    Filter jobs by exclusions, min salary, and workplace mode, then assign Match Score & rank.
    """
    processed = []
    min_sal_val = float(min_salary) if min_salary else 0.0

    for j in jobs:
        # 1. Exclude keyword check
        if not evaluate_keywords(j, include_kw=None, exclude_kw=exclude_kw):
            continue

        # 2. Min salary filter
        if min_sal_val > 0:
            sal_num = extract_numeric_salary(j.get("Salary", ""))
            if sal_num > 0 and sal_num < min_sal_val:
                continue

        # 3. Workplace mode filter
        if workplace_mode and workplace_mode.lower() != "all":
            wp = (j.get("Workplace") or j.get("Location") or "").lower()
            target_wp = workplace_mode.lower()
            if target_wp == "remote" and ("remote" not in wp and "work from home" not in wp):
                continue
            elif target_wp == "hybrid" and ("hybrid" not in wp):
                continue
            elif target_wp == "on-site" and ("remote" in wp or "hybrid" in wp or "work from home" in wp):
                continue

        # 4. Calculate Match Score with keyword bonus
        j["Match_Score"] = calculate_match_score(j, resume_text, include_kw=include_kw)
        processed.append(j)

    # Sort by Match Score descending
    processed.sort(key=lambda item: item.get("Match_Score", 0), reverse=True)
    return processed


def execute_parallel_search(scrapers_map, role, fromage_days, limit, locations, apply_mode, experience, selected_portals=None):
    """
    Execute multiple scrapers in parallel threads safely with exact per-scraper kwarg mapping.
    """
    if not selected_portals:
        selected_portals = list(scrapers_map.keys())

    all_raw_jobs = []

    def _run_scraper(portal_name, fn):
        try:
            print(f"[Aggregator] Starting parallel scrape for: {portal_name}")
            portal_limit = max(10, limit // max(1, len(selected_portals)))
            loc_input = locations if isinstance(locations, list) else [locations]
            
            exp_int = 0 if str(experience).lower() in ("fresher", "entry") else (int(experience) if str(experience).isdigit() else None)

            # Map role to Hirist category slug
            hirist_cat = "backend-development-jobs"
            r_low = role.lower()
            if "devops" in r_low or "sre" in r_low: hirist_cat = "devops-sre-jobs"
            elif "front" in r_low or "react" in r_low: hirist_cat = "frontend-development-jobs"
            elif "full" in r_low or "stack" in r_low: hirist_cat = "full-stack-jobs"
            elif "qa" in r_low or "test" in r_low: hirist_cat = "quality-assurance-jobs"
            elif "mobile" in r_low or "android" in r_low or "ios" in r_low: hirist_cat = "mobile-applications-jobs"

            if portal_name == "indeed":
                res = fn(role=role, fromage_days=fromage_days, limit=portal_limit, locations=loc_input, apply_mode=apply_mode, experience=experience)
            elif portal_name == "naukri":
                res = fn(role=role, city=loc_input, job_age_days=fromage_days, limit=portal_limit, experience=exp_int)
            elif portal_name == "glassdoor":
                res = fn(role=role, from_age_days=fromage_days, limit=portal_limit, locations=loc_input, apply_mode=apply_mode, experience=experience)
            elif portal_name == "foundit":
                res = fn(role=role, city=loc_input, job_freshness_days=fromage_days, limit=portal_limit, experience=experience)
            elif portal_name == "apna":
                res = fn(role=role, city=loc_input, posted_in_days=fromage_days, limit=portal_limit)
            elif portal_name == "shine":
                res = fn(role=role, city=loc_input, posting_days=fromage_days, limit=portal_limit)
            elif portal_name == "hirist":
                res = fn(category=hirist_cat, city=loc_input, posting_days=fromage_days, limit=portal_limit)
            elif portal_name == "linkedin":
                res = fn(role=role, time_filter=fromage_days, limit=portal_limit, locations=loc_input, apply_mode=apply_mode, experience=experience)
            else:
                res = []

            for j in (res or []):
                j["Platform"] = portal_name.capitalize()
            print(f"[Aggregator] {portal_name} returned {len(res or [])} jobs")
            return res or []
        except Exception as e:
            print(f"[Aggregator] Error in {portal_name} scraper: {e}")
            return []

    with ThreadPoolExecutor(max_workers=min(6, len(selected_portals))) as executor:
        futures = {
            executor.submit(_run_scraper, p_name, scrapers_map[p_name]): p_name
            for p_name in selected_portals if p_name in scrapers_map
        }
        for future in as_completed(futures):
            portal_name = futures[future]
            try:
                jobs = future.result(timeout=45)
                all_raw_jobs.extend(jobs)
            except Exception as exc:
                print(f"[Aggregator] Task for {portal_name} generated exception: {exc}")

    return all_raw_jobs


def generate_cover_letter_text(job, resume_text=None):
    """
    Generate a clean 3-paragraph professional cover letter tailored to the job.
    """
    title = job.get("Job Title", "Software Engineer")
    company = job.get("Company", "Target Company")
    location = job.get("Location", "India")
    skills = job.get("Skills") or "software development, problem solving, and backend architecture"

    resume_summary = resume_text.strip() if resume_text else "a passionate developer with a strong track record of delivering clean, scalable software solutions"

    letter = f"""Dear Hiring Team at {company},

I am writing to express my strong enthusiasm for the {title} position in {location}. With a solid technical background and experience in {skills}, I am confident in my ability to immediately contribute to {company}'s engineering goals.

Having reviewed the requirements for this role, my background aligns closely with your needs. Based on my profile ({resume_summary[:180]}...), I bring a disciplined approach to code quality, system performance, and collaborative execution.

I would welcome the opportunity to discuss how my skills and experience can support {company}'s ongoing success. Thank you for your time and consideration.

Sincerely,
Applicant
    """.strip()
    return letter
