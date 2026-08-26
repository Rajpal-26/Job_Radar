from utils.tracker_db import (
    init_db,
    save_job,
    get_all_saved_jobs,
    update_job_status,
    delete_saved_job,
)

print("--- Testing Tracker DB CRUD ---")
init_db()

job = {
    "Job Title": "Full Stack Engineer",
    "Company": "InnovateTech",
    "Location": "Bengaluru",
    "Link": "https://test.jobradar.local/101",
    "Platform": "Unified",
    "Salary": "12 LPA",
    "Match_Score": 95,
}

# 1. Save Job
job_id, is_new = save_job(job)
print(f"Saved Job ID: {job_id}, Is New: {is_new}")
assert is_new == True

# Save duplicate check
_, is_new_dup = save_job(job)
assert is_new_dup == False

# 2. Get All Saved Jobs
jobs = get_all_saved_jobs()
assert len(jobs) >= 1
print(f"Total Saved Jobs: {len(jobs)}")

# 3. Update Status
update_job_status(job_id, status="Applied", notes="Submitted resume via portal")
updated_jobs = get_all_saved_jobs()
target = [j for j in updated_jobs if j["id"] == job_id][0]
assert target["status"] == "Applied"
assert target["notes"] == "Submitted resume via portal"
print("Status updated to Applied successfully!")

# 4. Clean up / Delete test job
delete_saved_job(job_id)
print("Deleted test job successfully!")

print("ALL TRACKER DB TESTS PASSED!")
