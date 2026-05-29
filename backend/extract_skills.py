import pandas as pd
from collections import Counter
import re



df = pd.read_csv("data/jobs.csv")

print("\nLoaded dataset:", len(df))



skills = [

    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "scala",
    "php",
    "ruby",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "snowflake",
    "databricks",
    "bigquery",

    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "linux",
    "airflow",
    "jenkins",

    "machine learning",
    "deep learning",
    "artificial intelligence",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "matplotlib",
    "opencv",
    "xgboost",

    "fastapi",
    "flask",
    "django",
    "node.js",
    "express",
    "graphql",
    "rest api",

    "react",
    "next.js",
    "vue",
    "angular",
    "html",
    "css",
    "tailwind",

    "power bi",
    "tableau",
    "excel",
    "looker",
    "metabase",
    "dbt",

    "git",
    "github",
    "gitlab",
    "jira",

    "spark",
    "hadoop",
    "kafka",

    "llm",
    "langchain",
    "openai",
    "vector database",
    "prompt engineering",

]



all_skills = []

for description in df["description"]:
    text = str(description).lower()


    # remove noisy navigation text
    text = text.replace("ai auto-apply", "")
    text = text.replace("sign in", "")
    text = text.replace("find jobs", "")



    for skill in skills:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if (
                re.search(pattern, text, re.IGNORECASE)
                or skill.lower() in text.lower()
        ):
            all_skills.append(skill)



skill_counts = Counter(all_skills)


print("\nTOP SKILLS FOUND:\n")

for skill, count in sorted(
    skill_counts.items(),
    key=lambda x: x[1],
    reverse=True
)[:20]:
    print(f"{skill}: {count}")



results_df = pd.DataFrame(
    skill_counts.items(),
    columns=["Skill", "Count"]
)

results_df = results_df.sort_values(
    by="Count",
    ascending=False
)

results_df.to_csv(
    "data/skills_analysis.csv",
    index=False
)

print("\nSaved:")
print("data/skills_analysis.csv")