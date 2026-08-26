import re

def smart_evaluate_keywords(job, include_kw=None, exclude_kw=None):
    title = (job.get("Job Title") or "").lower()
    comp = (job.get("Company") or "").lower()
    desc = (job.get("Description") or "").lower()
    skills = (job.get("Skills") or "").lower()
    combo_text = f"{title} {skills} {desc} {comp}"

    # 1. Exclude keywords
    if exclude_kw:
        ex_terms = [k.strip().lower() for k in str(exclude_kw).split(",") if k.strip()]
        for term in ex_terms:
            if not term:
                continue
            pattern = r"\b" + re.escape(term) + r"\b"
            # Title-level exclusions (senior, lead, qa, manager, etc.)
            if re.search(pattern, title):
                return False

    # 2. Include keywords
    if include_kw:
        raw_inc = str(include_kw).strip()
        if not raw_inc:
            return True

        # Check for quoted phrases vs word list
        phrases = re.findall(r'"([^"]+)"', raw_inc)
        unquoted = re.sub(r'"[^"]+"', '', raw_inc).strip()
        
        # Check quoted exact phrases
        for phrase in phrases:
            if phrase.lower() not in combo_text:
                return False
                
        # Check unquoted tokens (comma or space separated)
        if unquoted:
            tokens = [t.strip().lower() for t in re.split(r"[\s,]+", unquoted) if t.strip()]
            matched_any = False
            for tok in tokens:
                pattern = r"\b" + re.escape(tok) + r"\b"
                if re.search(pattern, combo_text):
                    matched_any = True
                    break
            if not matched_any:
                return False

    return True

# Test
job = {
    "Job Title": "Associate Software Engineer",
    "Company": "Diatoz Solutions",
    "Description": "We are seeking a Python developer to join our engineering team. You will report to senior tech lead.",
    "Skills": "Python, Django, MySQL"
}

print("Smart Keyword Evaluation Result:", smart_evaluate_keywords(job, include_kw="python developer", exclude_kw="senior,lead,QA"))
