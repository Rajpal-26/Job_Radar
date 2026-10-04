# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import re
import os

# Categorized Skill Taxonomy
SKILL_TAXONOMY = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "Golang", "Go",
        "Rust", "PHP", "Ruby", "Kotlin", "Swift", "Dart", "R", "Scala", "SQL", "Bash", "Shell"
    ],
    "Frameworks & Backend": [
        "FastAPI", "Django", "Flask", "Spring Boot", "Express", "Node.js", "NestJS",
        "ASP.NET", ".NET", "Ruby on Rails", "Laravel", "Gin", "Echo", "Tornado", "Celery",
        "GraphQL", "gRPC", "REST API", "Microservices"
    ],
    "Frontend & Mobile": [
        "React", "React Native", "Next.js", "Vue.js", "Nuxt.js", "Angular", "Svelte",
        "HTML5", "HTML", "CSS3", "CSS", "TailwindCSS", "Bootstrap", "Redux", "Zustand", "Flutter"
    ],
    "AI, ML & Data Science": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "AI", "LLM", "NLP",
        "LangChain", "LlamaIndex", "Hugging Face", "OpenAI", "PyTorch", "TensorFlow",
        "Scikit-Learn", "Pandas", "NumPy", "OpenCV", "Transformers", "RAG", "Prompt Engineering",
        "Generative AI", "Vector Database", "ChromaDB", "Pinecone", "FAISS"
    ],
    "Databases & Caching": [
        "PostgreSQL", "Postgres", "MySQL", "MongoDB", "Redis", "SQLite", "Elasticsearch",
        "Cassandra", "DynamoDB", "Firebase", "Supabase", "Oracle", "MariaDB", "Snowflake"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
        "K8s", "CI/CD", "GitHub Actions", "GitLab CI", "Jenkins", "Terraform", "Linux",
        "Nginx", "Serverless", "Prometheus", "Grafana"
    ],
    "Testing & QA": [
        "Pytest", "Selenium", "Playwright", "Cypress", "Jest", "Mocha", "JUnit",
        "Postman", "QA Automation", "Unit Testing", "TDD"
    ],
    "Tools & Practices": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Agile", "Scrum",
        "System Design", "Data Structures", "Algorithms", "Object Oriented Programming", "OOP"
    ]
}

# Flattened list for quick matching
TECH_SKILLS = [skill for cat in SKILL_TAXONOMY.values() for skill in cat]


def extract_text_from_file(file_storage):
    """Extract raw text from PDF, DOCX, or text file object."""
    filename = getattr(file_storage, "filename", "").lower()
    text = ""

    try:
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
            text = "\n".join([para.text for para in doc.paragraphs if para.text])
        else:
            # Fallback raw read
            raw_bytes = file_storage.read()
            text = raw_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[ResumeParser] Error extracting text: {e}")
        try:
            file_storage.seek(0)
            text = file_storage.read().decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    return text.strip()


def extract_contact_info(text):
    """Extract email, phone, links, and candidate name heuristics."""
    info = {
        "email": "",
        "phone": "",
        "linkedin_url": "",
        "github_url": "",
        "portfolio_url": "",
        "full_name": ""
    }

    # 1. Email Regex
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    if email_match:
        info["email"] = email_match.group(0).strip()

    # 2. Phone Regex (Indian and International formats)
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+91[-.\s]?[6-9]\d{9}|[6-9]\d{9}', text)
    if phone_match:
        info["phone"] = phone_match.group(0).strip()

    # 3. LinkedIn
    linkedin_match = re.search(r'(https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin_url"] = linkedin_match.group(0).strip()
    elif "linkedin.com/in/" in text:
        m = re.search(r'linkedin\.com/in/([a-zA-Z0-9_-]+)', text)
        if m:
            info["linkedin_url"] = f"https://www.linkedin.com/in/{m.group(1)}"

    # 4. GitHub
    github_match = re.search(r'(https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if github_match:
        info["github_url"] = github_match.group(0).strip()
    elif "github.com/" in text:
        m = re.search(r'github\.com/([a-zA-Z0-9_-]+)', text)
        if m:
            info["github_url"] = f"https://github.com/{m.group(1)}"

    # 5. Portfolio / Personal Site
    portfolio_match = re.search(r'(https?://[a-zA-Z0-9.-]+\.(?:vercel\.app|netlify\.app|dev|io|me|tech)[^\s,]*)', text, re.IGNORECASE)
    if portfolio_match:
        info["portfolio_url"] = portfolio_match.group(0).strip()

    # 6. Name Heuristic (First 3 lines usually contain candidate name)
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) < 50]
    for line in lines[:4]:
        # Filter out obvious headers
        if not re.search(r'(resume|curriculum|vitae|contact|profile|email|phone|http|github|linkedin|summary)', line, re.IGNORECASE):
            # Check if looks like a name (2-4 capitalized words)
            words = line.split()
            if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                info["full_name"] = line
                break

    return info


def extract_skills_categorized(text):
    """Scan resume text against categorized skill taxonomy and return structured findings."""
    categorized = {}
    all_found = set()

    for category, skills in SKILL_TAXONOMY.items():
        found_in_cat = []
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_in_cat.append(skill)
                all_found.add(skill)
        if found_in_cat:
            categorized[category] = sorted(list(set(found_in_cat)))

    return categorized, sorted(list(all_found))


def deduce_roles_and_experience(text, skills_list):
    """Determine candidate seniority, target roles, and primary tech identity."""
    text_lower = text.lower()
    skills_lower = [s.lower() for s in skills_list]

    # Experience heuristic
    exp_level = "Fresher / 0-1 Year"
    if re.search(r'\b(fresher|entry level|graduate|intern|internship|trainee)\b', text_lower):
        exp_level = "Fresher (0-1 Year)"
    
    # Check for explicit year numbers
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)\s*(?:of)?\s*experience', text_lower)
    if exp_matches:
        try:
            years = max([float(y) for y in exp_matches])
            if years >= 5:
                exp_level = f"Senior Engineer ({int(years)}+ Years)"
            elif years >= 2:
                exp_level = f"Mid-Level ({int(years)} Years)"
            elif years >= 1:
                exp_level = f"Associate ({int(years)} Year)"
            else:
                exp_level = "Fresher (0-1 Year)"
        except Exception:
            pass

    # Target Roles
    target_roles = []
    
    # Python & AI
    if "python" in skills_lower:
        if any(ai_skill in skills_lower for ai_skill in ["machine learning", "deep learning", "langchain", "rag", "llm", "ai", "transformers"]):
            target_roles.append("AI / LLM Engineer")
            target_roles.append("Python AI Engineer")
        if any(be_skill in skills_lower for be_skill in ["fastapi", "django", "flask", "rest api", "sql"]):
            target_roles.append("Python Developer")
            target_roles.append("Backend Developer (Python)")
        target_roles.append("Software Engineer")

    # JavaScript / Web
    if any(fe_skill in skills_lower for fe_skill in ["react", "javascript", "typescript", "next.js", "node.js"]):
        if any(be_skill in skills_lower for be_skill in ["node.js", "express", "sql", "mongodb", "fastapi"]):
            target_roles.append("Full Stack Developer")
        else:
            target_roles.append("Frontend Developer (React)")

    # Cloud / DevOps
    if any(cloud_skill in skills_lower for cloud_skill in ["docker", "kubernetes", "aws", "ci/cd", "terraform"]):
        target_roles.append("DevOps / Cloud Engineer")

    # QA
    if any(qa_skill in skills_lower for qa_skill in ["selenium", "playwright", "pytest", "qa automation"]):
        target_roles.append("QA Automation Engineer")

    # Default fallback roles
    if not target_roles:
        target_roles = ["Software Engineer", "Associate Software Engineer", "Python Developer"]

    # Deduplicate while preserving order
    seen = set()
    cleaned_roles = []
    for r in target_roles:
        if r not in seen:
            seen.add(r)
            cleaned_roles.append(r)

    return exp_level, cleaned_roles[:5]


def parse_resume(file_storage):
    """
    Main parser: Accepts uploaded file, extracts text, contact info,
    categorized skills, target roles, and summary.
    """
    filename = getattr(file_storage, "filename", "resume.pdf")
    raw_text = extract_text_from_file(file_storage)

    contact_info = extract_contact_info(raw_text)
    skill_categories, skills_list = extract_skills_categorized(raw_text)
    exp_level, target_roles = deduce_roles_and_experience(raw_text, skills_list)

    # Clean short summary extraction (first paragraph or summary section)
    summary = ""
    summary_match = re.search(r'(?:summary|profile|about me|objective)[\s\:\-]+([^\n]+(?:\n[^\n]+){1,3})', raw_text, re.IGNORECASE)
    if summary_match:
        summary = summary_match.group(1).strip()
    elif raw_text:
        # First 200 characters of meaningful text
        lines = [l.strip() for l in raw_text.split('\n') if len(l.strip()) > 30]
        summary = lines[0] if lines else ""

    return {
        "filename": filename,
        "full_name": contact_info["full_name"] or "Software Engineer Candidate",
        "email": contact_info["email"],
        "phone": contact_info["phone"],
        "location": "India",
        "linkedin_url": contact_info["linkedin_url"],
        "github_url": contact_info["github_url"],
        "portfolio_url": contact_info["portfolio_url"],
        "experience_level": exp_level,
        "current_role": target_roles[0] if target_roles else "Software Engineer",
        "target_roles": target_roles,
        "skills": skills_list,
        "skill_categories": skill_categories,
        "summary": summary[:400],
        "raw_text": raw_text[:6000]
    }
