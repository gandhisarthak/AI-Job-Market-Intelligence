import requests
import pandas as pd
from datetime import datetime

# API URL
url = "https://www.arbeitnow.com/api/job-board-api"

print("Fetching jobs from API...")

response = requests.get(url)

data = response.json()

jobs = data["data"]

print(f"Total jobs fetched: {len(jobs)}")

job_list = []

for job in jobs:

    title = job.get("title", "")
    company = job.get("company_name", "")
    location = job.get("location", "")
    description = job.get("description", "")
    tags = ", ".join(job.get("tags", []))
    url = job.get("url", "")

    job_list.append({
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "tags": tags,
        "job_link": url,
        "date_scraped": datetime.now()
    })

# Create DataFrame
df = pd.DataFrame(job_list)

print("\nFirst 5 Jobs:\n")
print(df.head())

# Save CSV
df.to_csv("data/jobs.csv", index=False)

print("\nJobs saved successfully!")