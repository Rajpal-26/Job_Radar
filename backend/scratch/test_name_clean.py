# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================
import re

def parse_serp_title(raw_text: str, company: str) -> tuple[str, str]:
    # Clean non-ascii/bidi control characters
    text = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', raw_text)
    
    # Split by newlines in case breadcrumbs are on previous lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    target_line = lines[-1] if lines else text
    for line in lines:
        if (' - ' in line or ' | ' in line or ' – ' in line) and not line.lower().startswith(('linkedin', 'http')):
            target_line = line
            break
            
    clean = target_line
    # Strip leading breadcrumbs if all in one line
    clean = re.sub(r'^(?:Linkedin|LinkedIn)[^\n\r]*?(?=[A-Z][a-z]+|\b[A-Z]{2,}\b)', '', clean).strip()
    clean = re.sub(r'https?://\S+', '', clean).strip()
    clean = re.sub(r'\s*\|\s*LinkedIn.*$', '', clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r'\s*[-–—|]\s*LinkedIn.*$', '', clean, flags=re.IGNORECASE).strip()
    
    parts = [p.strip() for p in re.split(r'\s*[-–—|]\s*', clean) if p.strip()]
    if len(parts) >= 2:
        name = parts[0]
        # If first part is a breadcrumb artifact
        if name.lower() in ["linkedin", "more", "anytime", "in", "view"]:
            name = parts[1]
            title = " - ".join(parts[2:])
        else:
            title = " - ".join(parts[1:])
        title = re.sub(rf'\s*(?:at|@|-)\s*{re.escape(company)}.*$', '', title, flags=re.IGNORECASE).strip()
        return name, title or f"HR at {company}"
    elif len(parts) == 1:
        return parts[0], f"Talent Acquisition at {company}"
    return "LinkedIn Member", f"Recruiter at {company}"

samples = [
    "Linkedin\n › in › shreeya-joshi-aa949116b\nShreeya Joshi - Human Resource Business Partner",
    "Linkedin\n › in › khushi-malviya\nKhushi M - Talent Acquisition Specialist - IT Hiring - Full ...",
    "LinkedIn\n › in › karan-raj-srivastava-8123b91b6\nKaran Raj Srivastava - Head of Talent Acquisition",
    "Chandrika Mittal - Senior Lead - Talent Acquisition - Infosys | LinkedIn"
]

for s in samples:
    name, title = parse_serp_title(s, "GammaStack")
    print(f"NAME: '{name}' | TITLE: '{title}'")
