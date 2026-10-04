# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import re
import os
import json
import urllib.parse
from utils.resume_parser import TECH_SKILLS, SKILL_TAXONOMY

def calculate_ats_match(job_title, job_description, candidate_skills):
    """
    Calculate ATS compatibility percentage based on candidate skills vs job requirements.
    Returns match_score (0-100), matched_skills, and missing_skills.
    """
    full_job_text = f"{job_title or ''} {job_description or ''}".lower()
    candidate_skills_set = set([s.lower() for s in candidate_skills])

    job_required_skills = []
    for skill in TECH_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, full_job_text, re.IGNORECASE):
            job_required_skills.append(skill)

    job_required_skills = sorted(list(set(job_required_skills)))

    if not job_required_skills:
        # Fallback baseline match if job has minimal text
        return {
            "match_score": 85,
            "matched_skills": candidate_skills[:4],
            "missing_skills": [],
            "job_required_skills": candidate_skills[:4]
        }

    matched = [s for s in job_required_skills if s.lower() in candidate_skills_set]
    missing = [s for s in job_required_skills if s.lower() not in candidate_skills_set]

    # Calculate match percentage
    raw_ratio = len(matched) / len(job_required_skills)
    match_score = int(min(98, max(45, (raw_ratio * 60) + 38)))

    return {
        "match_score": match_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "job_required_skills": job_required_skills
    }


def generate_tailored_cover_letter(candidate_profile, job_title, company_name, job_description=""):
    """
    Generate a compelling, company-specific cover letter customized with the candidate's skills.
    """
    name = candidate_profile.get("full_name") or "Applicant"
    email = candidate_profile.get("email") or ""
    phone = candidate_profile.get("phone") or ""
    skills = candidate_profile.get("skills") or ["Python", "FastAPI", "REST APIs", "SQL", "Docker"]
    exp_level = candidate_profile.get("experience_level") or "Fresher / Associate Engineer"
    
    top_skills_str = ", ".join(skills[:5])
    company = (company_name or "your engineering team").strip()
    role = (job_title or "Software Engineer").strip()

    cover_letter = (
        f"Dear Hiring Team at {company},\n\n"
        f"I am writing to express my strong enthusiasm for the {role} position at {company}. "
        f"With hands-on experience in {top_skills_str} and a strong foundation as a {exp_level}, "
        f"I am excited by {company}'s work and confident that my technical skills align with your engineering priorities.\n\n"
        f"Throughout my projects, I have focused on writing clean, maintainable code, developing robust RESTful APIs, "
        f"and optimizing performance across backend services. I thrive in agile environments where rapid problem-solving, "
        f"continuous learning, and collaboration are valued.\n\n"
        f"Key highlights I would bring to {company}:\n"
        f"• Practical proficiency in {', '.join(skills[:3])} for building scalable features\n"
        f"• Strong grasp of database design, API integrations, and modern version control workflows (Git)\n"
        f"• High adaptability and commitment to delivering high-quality, tested software\n\n"
        f"I would welcome the opportunity to discuss how my background and enthusiasm can contribute to {company}'s upcoming milestones.\n\n"
        f"Thank you for your time and consideration.\n\n"
        f"Sincerely,\n"
        f"{name}\n"
        f"Email: {email} | Phone: {phone}"
    )

    return cover_letter.strip()


def solve_screening_question(question_text, candidate_profile, job_title="", company=""):
    """
    AI Question Solver: Generates context-aware, tailored answers to job application screening questions.
    """
    q_lower = question_text.lower().strip()
    skills = candidate_profile.get("skills") or ["Python", "FastAPI", "SQL", "Docker", "Git"]
    skills_str = ", ".join(skills[:4])
    name = candidate_profile.get("full_name") or "the candidate"
    exp_level = candidate_profile.get("experience_level") or "0-1 Year / Fresher"
    notice = candidate_profile.get("notice_period") or "Immediate / 15 Days"
    expected_ctc = candidate_profile.get("expected_ctc") or "6-10 LPA"
    role = job_title or "Software Engineer"
    comp = company or "the company"

    # 1. Experience & Skills Questions
    if any(k in q_lower for k in ["years of experience", "how many years", "experience with python", "experience with"]):
        # Extract specific tech mentioned in question
        matched_tech = [s for s in TECH_SKILLS if s.lower() in q_lower]
        if matched_tech:
            tech = matched_tech[0]
            if tech.lower() in [s.lower() for s in skills]:
                return f"I have strong hands-on project and development experience with {tech}, building backend APIs and scalable features as part of my {exp_level} engineering background."
            else:
                return f"While my primary stack is in {skills_str}, I am a fast learner and have foundational familiarity with {tech}."
        return f"I have comprehensive hands-on engineering experience spanning {exp_level} with a focus on {skills_str}."

    # 2. Why do you want to work here / Motivation
    if any(k in q_lower for k in ["why do you want", "why join", "interest in", "why should we hire", "what makes you a good fit"]):
        return (
            f"I am excited by {comp}'s mission and engineering standards. "
            f"My background in {skills_str} and passion for writing clean, performant code directly match the requirements for the {role} role. "
            f"I am eager to contribute to your core products while continuously expanding my technical skills."
        )

    # 3. Notice Period / Availability
    if any(k in q_lower for k in ["notice period", "when can you start", "joining date", "available to start"]):
        return f"My notice period is {notice}, and I am available to join immediately or within short notice."

    # 4. Salary / Compensation Expectations
    if any(k in q_lower for k in ["salary", "ctc", "compensation", "expected ctc", "current ctc"]):
        return f"My expected CTC is {expected_ctc}, open to discussion based on role responsibilities and total compensation benefits."

    # 5. Relocation / Work Mode
    if any(k in q_lower for k in ["relocate", "relocation", "remote", "hybrid", "on-site", "office"]):
        return f"I am comfortable working in remote, hybrid, or on-site modes and open to relocation for the right opportunity."

    # 6. Challenging Project / Problem Solving
    if any(k in q_lower for k in ["project", "challenging", "difficult bug", "accomplishment", "describe a time"]):
        return (
            f"In a recent project utilizing {skills_str}, I engineered end-to-end backend services with optimized database queries and robust error handling, reducing latency and ensuring 99.9% uptime. "
            f"I enjoy debugging complex edge cases and delivering reliable user-facing features."
        )

    # 7. Default Contextual Response
    return (
        f"With a solid technical foundation in {skills_str} and experience as a {exp_level}, "
        f"I bring strong analytical problem-solving skills and dedication to building scalable software at {comp} for the {role} position."
    )


def generate_autofill_package(candidate_profile, job_title="", company="", job_url=""):
    """
    Generate complete JSON payload for 1-click form autofilling (Extension & UI Clipboard).
    """
    name = candidate_profile.get("full_name") or ""
    name_parts = name.split()
    first_name = name_parts[0] if name_parts else "Candidate"
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    cover_letter = generate_tailored_cover_letter(candidate_profile, job_title, company)

    return {
        "personal": {
            "full_name": name,
            "first_name": first_name,
            "last_name": last_name,
            "email": candidate_profile.get("email", ""),
            "phone": candidate_profile.get("phone", ""),
            "location": candidate_profile.get("location", "India"),
            "linkedin": candidate_profile.get("linkedin_url", ""),
            "github": candidate_profile.get("github_url", ""),
            "portfolio": candidate_profile.get("portfolio_url", "")
        },
        "employment": {
            "experience_level": candidate_profile.get("experience_level", "Fresher (0-1 Year)"),
            "notice_period": candidate_profile.get("notice_period", "Immediate"),
            "current_ctc": candidate_profile.get("current_ctc", ""),
            "expected_ctc": candidate_profile.get("expected_ctc", "6-10 LPA"),
            "work_authorization": candidate_profile.get("work_authorization", "Authorized to work in India")
        },
        "skills": candidate_profile.get("skills", []),
        "target_roles": candidate_profile.get("target_roles", []),
        "cover_letter": cover_letter,
        "job": {
            "title": job_title,
            "company": company,
            "url": job_url
        }
    }
