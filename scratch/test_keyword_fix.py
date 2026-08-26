import re

def evaluate_keywords_v2(job, include_kw=None, exclude_kw=None):
    title = (job.get("Job Title") or "").lower()
    desc = (job.get("Description") or "").lower()
    company = (job.get("Company") or "").lower()
    skills = (job.get("Skills") or "").lower()

    combo_text = f"{title} {skills} {desc} {company}"

    # 1. Exclude keywords check
    if exclude_kw:
        ex_terms = [k.strip().lower() for k in str(exclude_kw).split(",") if k.strip()]
        for term in ex_terms:
            if not term:
                continue
            # Regex for word boundary
            pattern = r"\b" + re.escape(term) + r"\b"
            # Exclude primarily if found in Title, or as distinct word in body
            if re.search(pattern, title):
                return False
            # Check body for high-priority exclusions (senior, lead, manager, qa)
            if term in ("senior", "sr", "lead", "manager", "qa", "architect") and re.search(pattern, title):
                return False

    # 2. Include keywords check
    if include_kw:
        # Check if user provided quotes for exact phrase, else split terms
        inc_raw = str(include_kw).strip()
        if '"' in inc_raw:
            inc_terms = [k.strip('"').strip().lower() for k in inc_raw.split('"') if k.strip()]
        else:
            # Split by comma or space
            inc_terms = [k.strip().lower() for k in re.split(r"[,]+", inc_raw) if k.strip()]

        for term in inc_terms:
            # Tokenize term if space separated
            sub_words = [w.strip() for w in term.split() if w.strip()]
            for word in sub_words:
                pattern = r"\b" + re.escape(word) + r"\b"
                if not re.search(pattern, combo_text):
                    return False

    return True

# Test cases
sample_job = {
    "Job Title": "Associate Software Engineer",
    "Company": "Tech Corp",
    "Description": "We are looking for a Python Developer to build APIs. Qualifications: Bachelor's degree in CS.",
    "Skills": "Python, Django, REST API"
}

print("Testing QA in qualifications with old logic vs new logic:")
print("Old substring check 'qa' in desc:", "qa" in sample_job["Description"].lower()) # True -> REJECTED!
print("New word boundary check evaluate_keywords_v2:", evaluate_keywords_v2(sample_job, include_kw="python developer", exclude_kw="senior,lead,QA"))
