# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import re
from utils.resume_parser import TECH_SKILLS

def analyze_skill_gaps(jobs, user_skills):
    """
    Compare user skills against all scraped job descriptions.
    Annotates each job with 'missing_skills' and returns overall market demand.
    """
    user_skills_set = set([s.lower() for s in user_skills])
    skill_market_counts = {}

    annotated_jobs = []
    for job in jobs:
        desc = (job.get("Description") or "") + " " + (job.get("Job Title") or "")
        job_skills = set()
        for skill in TECH_SKILLS:
            if re.search(r'\b' + re.escape(skill) + r'\b', desc, re.IGNORECASE):
                job_skills.add(skill)
                skill_market_counts[skill] = skill_market_counts.get(skill, 0) + 1

        missing = [s for s in job_skills if s.lower() not in user_skills_set]
        j_copy = dict(job)
        j_copy["Required_Skills"] = sorted(list(job_skills))
        j_copy["Missing_Skills"] = missing[:5]
        annotated_jobs.append(j_copy)

    # Sort market demand
    sorted_market_demand = sorted(
        [{"skill": k, "count": v} for k, v in skill_market_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )

    return annotated_jobs, sorted_market_demand

def generate_recruiter_dm(job_title, company, user_skills=None, user_name="Applicant"):
    """
    Generate a high-converting, personalized 2-sentence LinkedIn/Email recruiter outreach DM.
    """
    skills_str = ", ".join(user_skills[:4]) if user_skills else "software engineering and system design"
    
    dm = (
        f"Hi [Hiring Manager], I saw your opening for {job_title} at {company} and wanted to reach out. "
        f"With a strong background in {skills_str}, I’ve built scalable solutions that match what {company} is growing. "
        f"I’d love to connect for 5 minutes or share my resume. Best, {user_name}."
    )
    return dm
