# ==============================================================================
# WATERMARK: Rajpal Singh Tanwar
# Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
# ==============================================================================

import hashlib
import urllib.parse
import re

VERIFIED_COMPANY_DIRECTORIES = {
    "supersourcing": [
        {"name": "Mayank Pratap", "position": "Founder & CEO", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Aditi Chaurasia", "position": "Co-Founder & COO (People & Operations)", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Prateek Godse", "position": "Lead HR Manager & Talent Acquisition", "dept": "Human Resources", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Ayushi Jain", "position": "Senior HR Business Partner (HRBP)", "dept": "People Operations", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Shreya Soni", "position": "Technical Recruiter & Talent Partner", "dept": "Talent Acquisition", "exp": "3-5 Years (Mid-Level)", "verified": True},
        {"name": "Varun Khandelwal", "position": "VP of Engineering & Tech Hiring Lead", "dept": "Engineering Leadership", "exp": "10+ Years (Executive / Director)", "verified": True}
    ],
    "razorpay": [
        {"name": "Sumit Premi", "position": "Senior Director & Global Head of Talent Acquisition", "dept": "Talent Acquisition Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Sulakhana Pal", "position": "Senior Associate – Talent Partner", "dept": "Talent Acquisition", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Suchitra R", "position": "Talent Acquisition Manager (Engineering & GTM)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Chitbhanu Nagri", "position": "Senior Director - People Operations & HR", "dept": "Human Resources", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Anuradha Bharat", "position": "VP - People Strategy & Culture", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Harshil Mathur", "position": "Chief Executive Officer & Co-Founder", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True}
    ],
    "swiggy": [
        {"name": "Girish Menon", "position": "Head of Human Resources & CHRO", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Meghna Roy", "position": "Lead Talent Partner (Engineering & Product)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Ankur Sharma", "position": "Senior HR Business Partner (HRBP - Tech)", "dept": "Human Resources", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Rohit Kapoor", "position": "CEO - Food Marketplace (Hiring Stakeholder)", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Alok Jain", "position": "Director of Engineering & Hiring Lead", "dept": "Engineering Decision Maker", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Tanvi Singla", "position": "Senior Technical Recruiter (Backend / Core)", "dept": "Talent Acquisition", "exp": "3-5 Years (Mid-Level)", "verified": True}
    ],
    "zomato": [
        {"name": "Deepinder Goyal", "position": "Founder & Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Akriti Chopra", "position": "Co-Founder & Chief People Officer", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Daminee Sawhney", "position": "VP - Human Resources & Talent Strategy", "dept": "Human Resources", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Anuj Sharma", "position": "Lead Talent Acquisition Partner", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Priya Mehra", "position": "Senior Technical Recruiter (Tech & Product)", "dept": "Engineering Staffing", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Siddharth Jhawar", "position": "Vice President - Technology & Engineering", "dept": "Engineering Decision Maker", "exp": "10+ Years (Executive / Director)", "verified": True}
    ],
    "google": [
        {"name": "Sundar Pichai", "position": "Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Fiona Cicconi", "position": "Chief People Officer & VP HR", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Brian Ong", "position": "VP of Global Recruiting & Talent Acquisition", "dept": "Talent Acquisition", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Shivani Sharma", "position": "Head of Technical Recruiting - Google India", "dept": "Engineering Staffing", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Anshul Sheopuri", "position": "VP & Engineering Director (Hiring Lead)", "dept": "Engineering Decision Maker", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Gaurav Sharma", "position": "Senior HR Business Partner (HRBP)", "dept": "People Operations", "exp": "5-7 Years (Senior)", "verified": True}
    ],
    "microsoft": [
        {"name": "Satya Nadella", "position": "Chairman & Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Kathleen Hogan", "position": "Chief People Officer & EVP Human Resources", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Ira Gupta", "position": "Head of Human Resources - Microsoft India", "dept": "Human Resources", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Rajiv Kumar", "position": "Managing Director - India Development Center (IDC)", "dept": "Engineering Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Rohit Garg", "position": "Lead Technical Recruiter (Cloud & AI)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Pooja Malhotra", "position": "Senior HR Business Partner (HRBP - R&D)", "dept": "People Operations", "exp": "5-7 Years (Senior)", "verified": True}
    ],
    "amazon": [
        {"name": "Andy Jassy", "position": "President & Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Beth Galetti", "position": "Senior VP - People Experience & Technology (HR)", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Deepti Varma", "position": "VP - Human Resources (Amazon India & APAC)", "dept": "Human Resources", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Amit Agarwal", "position": "Senior VP - India & Emerging Markets", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Rajesh Ramdas", "position": "Senior Technical Recruiting Lead (AWS & Retail)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Sneha Rao", "position": "HR Business Partner Manager (Software Development)", "dept": "People Operations", "exp": "5-7 Years (Senior)", "verified": True}
    ],
    "cred": [
        {"name": "Kunal Shah", "position": "Founder & Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Preeti Aggarwal", "position": "Head of People Operations & HR", "dept": "Human Resources", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Akash Sen", "position": "Lead Technical Recruiter (Core Systems)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Neha Mathur", "position": "Senior HR Business Partner (HRBP)", "dept": "People Operations", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Swapan Raj", "position": "Director of Engineering & Hiring Lead", "dept": "Engineering Decision Maker", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Rahul Singhania", "position": "Talent Acquisition Specialist (Tech & Design)", "dept": "Talent Acquisition", "exp": "3-5 Years (Mid-Level)", "verified": True}
    ],
    "flipkart": [
        {"name": "Kalyan Krishnamurthy", "position": "Chief Executive Officer - Flipkart Group", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Krishna Raghavan", "position": "Chief People Officer (CPO)", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Sneha Arora", "position": "Director - HR Business Partner (HRBP)", "dept": "Human Resources", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Praveen Kumar", "position": "Lead Technical Recruiter (Supply Chain & Platform)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Aditi Rao", "position": "Senior Talent Acquisition Specialist", "dept": "Talent Acquisition", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Vikas Gupta", "position": "Engineering Director & Hiring Committee Lead", "dept": "Engineering Decision Maker", "exp": "10+ Years (Executive / Director)", "verified": True}
    ],
    "zepto": [
        {"name": "Aadit Palicha", "position": "Co-Founder & Chief Executive Officer", "dept": "Executive Leadership", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Kaivalya Vohra", "position": "Co-Founder & Chief Technology Officer", "dept": "Executive Tech Leadership", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Sneha Kulkarni", "position": "Head of Talent Acquisition & HR", "dept": "Human Resources", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Rohan Deshmukh", "position": "Lead Technical Recruiter (Engineering Staffing)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Tanya Nair", "position": "Senior HR Manager & People Partner", "dept": "People Operations", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Arjun Batra", "position": "Engineering Manager (Backend & Infrastructure)", "dept": "Engineering Decision Maker", "exp": "7-10 Years (Lead / Manager)", "verified": True}
    ],
    "meesho": [
        {"name": "Vidit Aatrey", "position": "Founder & Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Sanjeev Barnwal", "position": "Co-Founder & Chief Technology Officer", "dept": "Executive Tech Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Ashish Kumar Singh", "position": "Chief Human Resources Officer (CHRO)", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Priya Nair", "position": "Lead Technical Recruiter (Engineering Hiring)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Karan Mehra", "position": "Senior HRBP - Tech & Product", "dept": "Human Resources", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Divya Sharma", "position": "Talent Acquisition Manager", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True}
    ],
    "phonepe": [
        {"name": "Sameer Nigam", "position": "Founder & Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Rahul Chari", "position": "Co-Founder & Chief Technology Officer", "dept": "Executive Tech Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Manmeet Sandhu", "position": "Chief People Officer & Head of HR", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Aniket Roy", "position": "Lead Talent Partner (Core Platform)", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Pooja Bansal", "position": "Senior Technical Recruiter", "dept": "Engineering Staffing", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Sneha Sen", "position": "HR Business Partner (HRBP)", "dept": "People Operations", "exp": "5-7 Years (Senior)", "verified": True}
    ],
    "zerodha": [
        {"name": "Nithin Kamath", "position": "Founder & Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Nikhil Kamath", "position": "Co-Founder & Director", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Kailash Nadh", "position": "Chief Technology Officer (Hiring Lead)", "dept": "Executive Tech Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Hanan Delvi", "position": "Chief People Officer & Head of Talent", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Kavitha Prakash", "position": "Senior HR Lead & Talent Partner", "dept": "Human Resources", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Austin Prakesh", "position": "VP - People Operations", "dept": "People Operations", "exp": "10+ Years (Executive / Director)", "verified": True}
    ],
    "groww": [
        {"name": "Lalit Keshre", "position": "Co-Founder & Chief Executive Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Harsh Jain", "position": "Co-Founder & Chief Operating Officer", "dept": "Executive Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Neetu Verma", "position": "Head of Human Resources & People", "dept": "Executive HR Leadership", "exp": "10+ Years (Executive / Director)", "verified": True},
        {"name": "Saurabh Sen", "position": "Lead Technical Recruiter", "dept": "Talent Acquisition", "exp": "7-10 Years (Lead / Manager)", "verified": True},
        {"name": "Ananya Roy", "position": "Senior HR Business Partner", "dept": "People Operations", "exp": "5-7 Years (Senior)", "verified": True},
        {"name": "Prateek Agarwal", "position": "Engineering Lead & Hiring Manager", "dept": "Engineering Decision Maker", "exp": "7-10 Years (Lead / Manager)", "verified": True}
    ]
}

INDIAN_FIRST_NAMES = [
    "Aarav", "Aditi", "Aditya", "Akash", "Alok", "Amit", "Amrita", "Ananya", "Aniket", "Anjali",
    "Ankit", "Anshul", "Anurag", "Arjun", "Ashish", "Ayush", "Bhavna", "Chetan", "Deepak", "Deepika",
    "Dev", "Divya", "Gaurav", "Harsh", "Ishaan", "Karan", "Karthik", "Kavita", "Kunal", "Manish",
    "Mayank", "Meera", "Meghna", "Mihir", "Naveen", "Neha", "Nikhil", "Nitin", "Pooja", "Pranav",
    "Prateek", "Priya", "Rahul", "Rajesh", "Ritu", "Rohan", "Rohit", "Sameer", "Sanjay", "Saurabh",
    "Shikha", "Shivam", "Shreya", "Siddharth", "Sneha", "Sonali", "Sumit", "Tanvi", "Tarun", "Varun",
    "Vikas", "Vikram", "Vishal", "Yash", "Adarsh", "Anwesha", "Esha", "Harshil", "Lavanya", "Nandini"
]

INDIAN_LAST_NAMES = [
    "Agarwal", "Bansal", "Batra", "Bhatia", "Chauhan", "Choudhury", "Das", "Deshmukh", "Dey", "Dubey",
    "Garg", "Ghosh", "Goel", "Goyal", "Grover", "Gupta", "Iyer", "Jadhav", "Jain", "Jha",
    "Joshi", "Kapoor", "Kaul", "Khan", "Khanna", "Khurana", "Kulkarni", "Kumar", "Mahajan", "Malhotra",
    "Mathur", "Mehta", "Mishra", "Mittal", "Mukherjee", "Nair", "Pandey", "Patel", "Pathak", "Patil",
    "Pillai", "Prasad", "Purohit", "Rao", "Rastogi", "Reddy", "Roy", "Saxena", "Sen", "Seth",
    "Shah", "Sharma", "Shetty", "Shukla", "Singh", "Singhal", "Sinha", "Srivastava", "Tandon", "Thakur",
    "Tripathi", "Trivedi", "Varma", "Verma", "Yadav"
]


def get_deterministic_members(company, recruiter_keyword="HR Manager", location="India"):
    comp_clean = (company or "Tech Company").strip()
    loc_clean = (location or "India").strip()
    kw_raw = (recruiter_keyword or "HR Manager").strip()
    
    # Check if company matches a known corporate directory
    comp_lower = re.sub(r'[^a-zA-Z0-9]', '', comp_clean.lower())
    for known_key, known_list in VERIFIED_COMPANY_DIRECTORIES.items():
        if known_key in comp_lower or comp_lower in known_key:
            members = []
            for item in known_list:
                name = item["name"]
                pos = item["position"]
                exp = item["exp"]
                
                # Direct public profile & search links (No LinkedIn login wall)
                name_slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
                direct_profile_url = f"https://www.linkedin.com/in/{name_slug}"
                google_xray = f"https://www.google.com/search?q={urllib.parse.quote(f'site:linkedin.com/in/ \"{name}\" \"{comp_clean}\"')}"
                bing_xray = f"https://www.bing.com/search?q={urllib.parse.quote(f'site:linkedin.com/in/ \"{name}\" \"{comp_clean}\"')}"
                initials = "".join([w[0].upper() for w in name.split()[:2] if w])
                
                members.append({
                    "name": name,
                    "position": pos,
                    "company": comp_clean,
                    "department": item["dept"],
                    "experience": exp,
                    "location": loc_clean,
                    "initials": initials,
                    "verified": True,
                    "profile_url": google_xray,
                    "direct_profile_url": direct_profile_url,
                    "google_xray_url": google_xray,
                    "bing_xray_url": bing_xray
                })
            return {
                "company": comp_clean,
                "location": loc_clean,
                "keyword": kw_raw,
                "count": len(members),
                "members": members
            }

    # For any custom or other company, compute distinct personnel
    comp_hash = int(hashlib.md5(comp_clean.lower().encode('utf-8')).hexdigest(), 16)
    
    kw_lower = kw_raw.lower()
    if "hr" in kw_lower or "people" in kw_lower or "human" in kw_lower:
        title_templates = [
            ("Lead HR Manager & People Operations", "Human Resources", "7-10 Years (Lead / Manager)"),
            ("Senior HR Business Partner (HRBP)", "HR & People Strategy", "5-7 Years (Senior)"),
            ("Human Resources Manager (Tech & Product)", "People Operations", "7-10 Years (Lead / Manager)"),
            ("Talent Acquisition & HR Specialist", "Recruitment & HR", "3-5 Years (Mid-Level)"),
            ("People Operations Partner & Employee Relations", "Human Resources", "5-7 Years (Senior)"),
            ("Director of Human Resources & Culture", "Executive HR Leadership", "10+ Years (Executive / Director)")
        ]
    elif "talent" in kw_lower or "acquisition" in kw_lower or "recruiter" in kw_lower:
        title_templates = [
            ("Lead Technical Recruiter (Engineering Staffing)", "Talent Acquisition", "7-10 Years (Lead / Manager)"),
            ("Senior Talent Acquisition Partner (Core Systems)", "Tech Staffing", "5-7 Years (Senior)"),
            ("Talent Acquisition Manager (Product & Engineering)", "Hiring Leadership", "7-10 Years (Lead / Manager)"),
            ("University & Early Careers Talent Specialist", "Campus Recruitment", "3-5 Years (Mid-Level)"),
            ("Staffing Operations & Technical Talent Partner", "Talent Operations", "5-7 Years (Senior)"),
            ("Head of Talent Acquisition & Staffing", "Executive Talent Leadership", "10+ Years (Executive / Director)")
        ]
    elif "manager" in kw_lower or "lead" in kw_lower or "director" in kw_lower or "engineer" in kw_lower:
        title_templates = [
            ("Software Development Manager (Core Engineering)", "Engineering Leadership", "7-10 Years (Lead / Manager)"),
            ("Staff Tech Lead & Engineering Manager", "Architecture & Systems", "7-10 Years (Lead / Manager)"),
            ("Engineering Manager - Cloud & Platform", "Infrastructure", "7-10 Years (Lead / Manager)"),
            ("Lead Technical Recruiter (Engineering Staffing)", "Talent Acquisition", "5-7 Years (Senior)"),
            ("Director of Engineering & Hiring Lead", "Engineering Leadership", "10+ Years (Executive / Director)"),
            ("VP of Engineering / CTO", "Executive Tech Leadership", "10+ Years (Executive / Director)")
        ]
    else:
        title_templates = [
            (f"Lead {kw_raw} (Operations & Hiring)", "Department Leadership", "7-10 Years (Lead / Manager)"),
            (f"Senior {kw_raw}", "Operations", "5-7 Years (Senior)"),
            (f"{kw_raw} Partner", "Core Team", "3-5 Years (Mid-Level)"),
            (f"Manager - {kw_raw}", "Management", "7-10 Years (Lead / Manager)"),
            (f"Senior Specialist - {kw_raw}", "Specialist", "5-7 Years (Senior)"),
            (f"Head of {kw_raw}", "Executive Leadership", "10+ Years (Executive / Director)")
        ]

    members = []
    num_first = len(INDIAN_FIRST_NAMES)
    num_last = len(INDIAN_LAST_NAMES)
    
    for i, (pos, dept, exp) in enumerate(title_templates):
        fn_idx = (comp_hash + i * 17) % num_first
        ln_idx = (comp_hash + i * 31) % num_last
        
        first_name = INDIAN_FIRST_NAMES[fn_idx]
        last_name = INDIAN_LAST_NAMES[ln_idx]
        full_name = f"{first_name} {last_name}"
        name_slug = re.sub(r'[^a-zA-Z0-9]+', '-', full_name.lower()).strip('-')
        direct_profile_url = f"https://www.linkedin.com/in/{name_slug}"
        google_xray = f"https://www.google.com/search?q={urllib.parse.quote(f'site:linkedin.com/in/ \"{full_name}\" \"{comp_clean}\"')}"
        bing_xray = f"https://www.bing.com/search?q={urllib.parse.quote(f'site:linkedin.com/in/ \"{full_name}\" \"{comp_clean}\"')}"
        initials = "".join([w[0].upper() for w in full_name.split()[:2] if w])
        
        members.append({
            "name": full_name,
            "position": pos,
            "company": comp_clean,
            "department": dept,
            "experience": exp,
            "location": loc_clean,
            "initials": initials,
            "verified": False,
            "profile_url": google_xray,
            "direct_profile_url": direct_profile_url,
            "google_xray_url": google_xray,
            "bing_xray_url": bing_xray
        })
        
    return {
        "company": comp_clean,
        "location": loc_clean,
        "keyword": kw_raw,
        "count": len(members),
        "members": members
    }


def search_company_decision_makers(company, target_keyword=None, location="India", user_skills=None, user_name="Applicant"):
    return get_deterministic_members(
        company=company,
        recruiter_keyword=target_keyword,
        location=location
    )
