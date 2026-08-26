# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import re

TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Express", "FastAPI",
    "Django", "Flask", "Java", "Spring Boot", "C++", "C#", ".NET", "Golang", "Rust",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Docker",
    "Kubernetes", "AWS", "Azure", "GCP", "Git", "GitHub", "CI/CD", "REST API",
    "GraphQL", "Microservices", "System Design", "Data Structures", "Algorithms",
    "Machine Learning", "Deep Learning", "Pandas", "NumPy", "PyTorch", "TensorFlow",
    "HTML", "CSS", "TailwindCSS", "Bootstrap", "Selenium", "Playwright", "Pytest",
    "QA Automation", "DevOps", "Linux", "Bash", "Redux", "Vue.js", "Angular"
]

def extract_text_from_file(file_storage):
    """Extract raw text from PDF or DOCX file object."""
    filename = file_storage.filename.lower()
    text = ""

    if filename.endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(file_storage) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    elif filename.endswith(".docx"):
        import docx
        doc = docx.Document(file_storage)
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        # Fallback raw text read
        text = file_storage.read().decode("utf-8", errors="ignore")

    return text.strip()

def parse_resume(file_storage):
    """Parse uploaded resume and return structured metadata."""
    raw_text = extract_text_from_file(file_storage)
    found_skills = set()

    for skill in TECH_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, raw_text, re.IGNORECASE):
            found_skills.add(skill)

    # Infer target role recommendation based on top skills
    suggested_role = "Software Engineer"
    skills_lower = [s.lower() for s in found_skills]
    
    if "python" in skills_lower and ("fastapi" in skills_lower or "django" in skills_lower or "flask" in skills_lower):
        suggested_role = "Python Backend Developer"
    elif "react" in skills_lower or "javascript" in skills_lower or "typescript" in skills_lower:
        suggested_role = "Full Stack / Frontend Developer"
    elif "machine learning" in skills_lower or "pandas" in skills_lower:
        suggested_role = "Data Scientist / ML Engineer"
    elif "qa automation" in skills_lower or "selenium" in skills_lower or "pytest" in skills_lower:
        suggested_role = "QA Automation Engineer"
    elif "docker" in skills_lower or "kubernetes" in skills_lower or "aws" in skills_lower:
        suggested_role = "DevOps / Cloud Engineer"

    return {
        "raw_text": raw_text[:4000],  # Truncated for AI context
        "skills": sorted(list(found_skills)),
        "skill_count": len(found_skills),
        "suggested_role": suggested_role
    }
