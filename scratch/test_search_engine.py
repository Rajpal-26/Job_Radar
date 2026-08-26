from utils.search_engine import (
    evaluate_keywords,
    extract_numeric_salary,
    calculate_match_score,
    deduplicate_jobs,
    filter_and_rank_jobs,
)

print("--- 1. Testing Keyword Evaluation ---")
job_text = "Associate Software Engineer working with Python, FastAPI, PostgreSQL, and AWS"
assert evaluate_keywords(job_text, include_kw="Python, FastAPI", exclude_kw="Senior, Lead") == True
assert evaluate_keywords(job_text, include_kw="Python", exclude_kw="FastAPI") == False
assert evaluate_keywords(job_text, include_kw="Java") == False
print("PASSED Keyword Evaluation Tests!")

print("\n--- 2. Testing Salary Parsing ---")
assert extract_numeric_salary("₹8 - 12 LPA") == 10.0
assert extract_numeric_salary("50,000/month") == 6.0
assert extract_numeric_salary("$100,000") == 85.0
print("PASSED Salary Parsing Tests!")

print("\n--- 3. Testing Resume Match Score ---")
job = {
    "Job Title": "Python Backend Developer",
    "Company": "TechCorp",
    "Description": "Building REST APIs with Python, Django, PostgreSQL, Docker, AWS",
    "Skills": "Python, Django, SQL",
}
score_high = calculate_match_score(job, "Python, Django, PostgreSQL, Docker, AWS, SQL")
score_low = calculate_match_score(job, "Java, Spring Boot, C++")
print(f"High Match Score: {score_high}%")
print(f"Low Match Score: {score_low}%")
assert score_high > score_low
print("PASSED Match Score Tests!")

print("\n--- 4. Testing Deduplication ---")
jobs = [
    {"Job Title": "Software Engineer", "Company": "Google", "Location": "Bengaluru", "Platform": "Indeed", "Link": "http://indeed.com/1"},
    {"Job Title": "Software Engineer", "Company": "Google", "Location": "Bengaluru, India", "Platform": "Naukri", "Link": "http://naukri.com/1"},
    {"Job Title": "Backend Engineer", "Company": "Amazon", "Location": "Pune", "Platform": "Glassdoor", "Link": "http://glassdoor.com/1"},
]
deduped = deduplicate_jobs(jobs)
print(f"Original Jobs: {len(jobs)}, Deduplicated: {len(deduped)}")
assert len(deduped) == 2
google_job = [j for j in deduped if j["Company"] == "Google"][0]
print(f"Google Job Platforms: {google_job['Platforms']}")
assert "Indeed" in google_job["Platforms"] and "Naukri" in google_job["Platforms"]
print("PASSED Deduplication Tests!")

print("\nALL SEARCH ENGINE UNIT TESTS PASSED!")
