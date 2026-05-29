import requests
import pandas as pd
from datetime import datetime
import os



API_URL = "https://www.arbeitnow.com/api/job-board-api"
OUTPUT_PATH = "data/jobs.csv"

os.makedirs("data", exist_ok=True)



print("Fetching jobs from API...")

try:
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    jobs = data.get("data", [])
    print(f"Total jobs fetched: {len(jobs)}")

except requests.exceptions.ConnectionError:
    print("Error: No internet connection.")
    exit()

except requests.exceptions.Timeout:
    print("Error: Request timed out.")
    exit()

except requests.exceptions.HTTPError as e:
    print(f"Error: API returned error: {e}")
    exit()

except Exception as e:
    print(f"Unexpected error: {e}")
    exit()



job_list = []

for job in jobs:

    title       = job.get("title", "")
    company     = job.get("company_name", "")
    location    = job.get("location", "")
    description = job.get("description", "")
    tags        = ", ".join(job.get("tags", []))
    job_url     = job.get("url", "")

    if title or description:
        job_list.append({
            "title":        title,
            "company":      company,
            "location":     location,
            "description":  description,
            "tags":         tags,
            "job_link":     job_url,
            "date_scraped": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })




new_df = pd.DataFrame(job_list)


if os.path.exists(OUTPUT_PATH):
    existing_df = pd.read_csv(OUTPUT_PATH)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["job_link"], keep="first")
    combined_df.to_csv(OUTPUT_PATH, index=False)
    new_count = len(combined_df) - len(existing_df)
    print(f"Added {new_count} new jobs. Total: {len(combined_df)}")
else:
    new_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(new_df)} jobs to {OUTPUT_PATH}")


df = pd.read_csv(OUTPUT_PATH)
print(f"\nSample jobs:")
print(df[["title", "company", "location"]].head())
print(f"\nTotal in database: {len(df)}")