import pandas as pd

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("data/jobs.csv",index=False)

# =========================
# SKILL DATABASE
# =========================

skills_database = [
    "Python",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "Power BI",
    "Tableau",
    "Excel",
    "Statistics",
    "Data Analysis",
    "Data Science",
    "AWS",
    "Azure",
    "Docker",
    "Kubernetes",
    "LLM",
    "LangChain",
    "NLP",
    "FastAPI",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Git",
    "Linux"
]

# =========================
# SKILL EXTRACTION
# =========================

def extract_skills(text):

    text = str(text).lower()

    found_skills = []

    for skill in skills_database:

        if skill.lower() in text:
            found_skills.append(skill)

    return found_skills

# =========================
# APPLY EXTRACTION
# =========================

df["combined_text"] = (
    df["title"].astype(str) + " " +
    df["company"].astype(str) + " " +
    df["location"].astype(str)
)

df["skills"] = df["combined_text"].apply(extract_skills)

# =========================
# SKILL COUNTS
# =========================

all_skills = []

for skills in df["skills"]:
    all_skills.extend(skills)

skill_counts = pd.Series(all_skills).value_counts()

print("\nTOP SKILLS:\n")
print(skill_counts)

# =========================
# SAVE
# =========================

df.to_csv("data/jobs_with_skills.csv", index=False)

skill_counts.to_csv("data/skill_counts.csv")

print("\nDone!")