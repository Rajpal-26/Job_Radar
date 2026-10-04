# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

"""
Precision Job Matcher & Metadata Extractor for JobRadar.
Extracts salary/stipend, recruiter profile, work mode, skills, and enforces strict fresher/junior criteria.
"""

import re
from datetime import datetime

# Target Role Regex Patterns
ROLE_PATTERNS = {
    "Python Developer": [r"\bpython\b", r"\bdjango\b", r"\bfastapi\b", r"\bflask\b"],
    "Associate Software Engineer": [r"\bassociate\s+software\b", r"\base\b", r"\bgraduate\s+engineer\b", r"\btrainee\s+engineer\b"],
    "Software Engineer": [r"\bsoftware\s+engineer\b", r"\bsoftware\s+developer\b", r"\bsde\s*[-iI1]?\b", r"\bjunior\s+developer\b"],
    "AI/LLM Engineer": [r"\bllm\b", r"\blarge\s+language\b", r"\bgenai\b", r"\bgenerative\s+ai\b", r"\brag\b", r"\blangchain\b"],
    "AI Engineer": [r"\bai\s+engineer\b", r"\bartificial\s+intelligence\b", r"\bml\s+engineer\b", r"\bmachine\s+learning\b"]
}

# Negative Keywords (Seniority, Leadership, 3+ Years)
SENIOR_KEYWORDS = [
    r"\bsenior\b", r"\bsr\.\b", r"\bsr\b", r"\blead\b", r"\bprincipal\b",
    r"\bstaff\b", r"\barchitect\b", r"\bdirector\b", r"\bmanager\b",
    r"\bhead\s+of\b", r"\bvp\b", r"\bexpert\b", r"\b3\+\s*years?\b",
    r"\b4\+\s*years?\b", r"\b5\+\s*years?\b", r"\b7\+\s*years?\b",
    r"\b10\+\s*years?\b", r"\b8\+\s*years?\b"
]

# Fresh Graduate / Junior Positive Keywords
JUNIOR_POSITIVE_KEYWORDS = [
    r"\bfresher\b", r"\b0-1\s*years?\b", r"\b0-6\s*months?\b", r"\bentry\s*level\b",
    r"\bjunior\b", r"\bjr\.\b", r"\bgraduate\b", r"\bintern\b", r"\binternship\b",
    r"\btrainee\b", r"\b2024\s*batch\b", r"\b2025\s*batch\b", r"\b2026\s*batch\b",
    r"\bassociate\b"
]

# Salary Extraction Regexes
SALARY_PATTERNS = [
    r"(?:₹|INR|Rs\.?)\s*(\d+(?:\.\d+)?\s*(?:-|to)\s*\d+(?:\.\d+)?\s*(?:LPA|lpa|Lakhs?|Lacs?))",
    r"(?:₹|INR|Rs\.?)\s*(\d+(?:\.\d+)?\s*(?:LPA|lpa|Lakhs?|Lacs?))",
    r"(?:₹|INR|Rs\.?)\s*(\d{1,3}(?:,\d{2,3})*(?:\s*(?:-|to)\s*\d{1,3}(?:,\d{2,3})*)?\s*(?:\/\s*month|pm|per\s*month))",
    r"(\$\s*\d{2,3}k\s*(?:-|to)\s*\$\s*\d{2,3}k)",
    r"(\d+(?:\.\d+)?\s*(?:-|to)\s*\d+(?:\.\d+)?\s*LPA)"
]

# Key Skills to automatically detect
KEY_SKILLS_LIST = [
    "Python", "FastAPI", "Django", "Flask", "PostgreSQL", "MySQL", "MongoDB",
    "Docker", "Kubernetes", "AWS", "Git", "REST APIs", "GraphQL", "Redis",
    "LangChain", "LLMs", "LlamaIndex", "HuggingFace", "PyTorch", "TensorFlow",
    "OpenAI", "Prompt Engineering", "NLP", "Computer Vision", "Pandas", "NumPy"
]


def extract_salary(text):
    """Extracts salary/stipend information from job text."""
    if not text:
        return ""
    for pat in SALARY_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return ""


def extract_skills(text):
    """Detects technical skills present in the job description or title."""
    if not text:
        return []
    found = []
    text_lower = text.lower()
    for skill in KEY_SKILLS_LIST:
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", text_lower):
            found.append(skill)
    return found[:6]


def extract_workplace_mode(text, location=""):
    """Determines if the role is Remote, Hybrid, or On-site."""
    combined = (text + " " + location).lower()
    if "remote" in combined or "work from home" in combined or "wfh" in combined:
        return "Remote"
    if "hybrid" in combined or "flexible" in combined:
        return "Hybrid"
    return "On-site"


def score_job_match(title, description="", experience=""):
    """
    Computes a precision match score (0-100%) and returns boolean acceptance.
    Strictly filters out Senior/Lead positions and validates Junior/Fresher fit.
    """
    title_clean = title.lower()
    combined_clean = (title + " " + description + " " + experience).lower()
    
    # 1. Reject Senior/Lead/Manager titles immediately
    for sk in SENIOR_KEYWORDS:
        if re.search(sk, title_clean):
            return 0, False
            
    # Check experience field for senior flags
    if any(k in experience.lower() for k in ["senior", "lead", "3-5", "5-7", "7-10", "10+", "5+", "7+"]):
        return 0, False

    # 2. Check Role Matching
    role_matched = False
    matched_role_name = ""
    for r_name, patterns in ROLE_PATTERNS.items():
        if any(re.search(p, title_clean) for p in patterns):
            role_matched = True
            matched_role_name = r_name
            break
            
    if not role_matched:
        return 0, False

    # 3. Calculate Score
    score = 75  # Base score for passing role match and negative filter
    
    # Bonus for explicit junior positive keywords in title or description
    for jk in JUNIOR_POSITIVE_KEYWORDS:
        if re.search(jk, combined_clean):
            score += 10
            break
            
    # Bonus for entry-level experience values
    if any(e in experience.lower() for e in ["fresher", "0-1", "0-6", "entry", "intern"]):
        score += 10

    score = min(98, score)
    return score, True
