import streamlit as st

# MUST BE FIRST
st.set_page_config(
    page_title="AI Job Market Intelligence",
    page_icon="🚀",
    layout="wide"
)

import pandas as pd
import plotly.express as px
import pdfplumber
import ollama
import json
import subprocess
from docx import Document



st.markdown("""
<style>
.main { background-color: #0E1117; }
h1, h2, h3, h4 { color: white; }
[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #333;
    padding: 15px;
    border-radius: 12px;
}
.stDataFrame { background-color: white; }
section[data-testid="stSidebar"] { background-color: #111827; }
</style>
""", unsafe_allow_html=True)



st.markdown("""
# 🚀 AI Job Market Intelligence Platform
### Real-time AI-powered job analytics, resume matching, and market intelligence
""")



try:
    jobs_df = pd.read_csv("data/jobs.csv")
except FileNotFoundError:
    st.error("No job data found. Please run the scraper first:")
    st.code("python scraper/scrape_jobs.py")
    st.stop()

try:
    skills_df = pd.read_csv("data/skills_analysis.csv")
except FileNotFoundError:
    st.error("No skills data found. Please run the skill extractor first:")
    st.code("python backend/extract_skills.py")
    st.stop()



page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Resume Matcher", "Job Explorer"]
)

st.sidebar.header("Filters")

locations = jobs_df["location"].dropna().unique()
selected_location = st.sidebar.selectbox(
    "Select Location",
    ["All"] + list(locations)
)

skill_search = st.sidebar.text_input("Search Skill")



filtered_jobs = jobs_df.copy()

if selected_location != "All":
    filtered_jobs = filtered_jobs[
        filtered_jobs["location"] == selected_location
    ]

if skill_search:
    filtered_jobs = filtered_jobs[
        filtered_jobs["description"].str.contains(
            skill_search, case=False, na=False
        )
    ]



if page == "Dashboard":

    if st.button("🔄 Refresh Job Data"):
        with st.spinner("Scraping latest jobs..."):
            subprocess.run(
                ["python", "scraper/scrape_jobs.py"],
                capture_output=True
            )
            subprocess.run(
                ["python", "backend/extract_skills.py"],
                capture_output=True
            )
            st.success("Data refreshed successfully!")
            st.rerun()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Jobs", len(jobs_df))

    with col2:
        st.metric("Unique Skills", len(skills_df))

    with col3:
        st.metric("Top Skill", skills_df.iloc[0]["Skill"])

    st.subheader("🔥 Top Skills in Demand")

    fig = px.bar(
        skills_df.head(15),
        x="Skill",
        y="Count",
        title="Most In-Demand Skills",
        text="Count"
    )
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌍 Top Hiring Locations")

    location_counts = jobs_df["location"].value_counts().head(10)

    location_fig = px.pie(
        names=location_counts.index,
        values=location_counts.values,
        title="Top Job Locations"
    )
    location_fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(location_fig, use_container_width=True)

    st.subheader("🏢 Companies Hiring Most")

    company_counts = (
        jobs_df["company"]
        .value_counts()
        .reset_index()
    )
    company_counts.columns = ["Company", "Open Roles"]
    st.dataframe(company_counts.head(10), hide_index=True)



if page == "Resume Matcher":

    st.subheader("🧠 AI Resume Matcher")
    st.markdown("Upload your resume and paste a job description to get an AI-powered match analysis.")
    st.info("💡 Powered by a free local AI model — no API key or cost required.")

    uploaded_file = st.file_uploader(
        "Upload Your Resume",
        type=["pdf", "docx", "txt"]
    )

    resume_text = ""

    if uploaded_file is not None:

        if uploaded_file.name.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                for page_pdf in pdf.pages:
                    resume_text += page_pdf.extract_text() or ""

        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                resume_text += para.text + "\n"

        elif uploaded_file.name.endswith(".txt"):
            resume_text = str(uploaded_file.read(), "utf-8")

        st.success("Resume uploaded successfully!")

    st.markdown("### Paste a Job Description")
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the job description here..."
    )

    if resume_text and job_description:

        if st.button("🤖 Analyse with AI", type="primary"):

            with st.spinner("AI is analysing your resume... may take 30-60 seconds..."):

                try:
                    response = ollama.chat(
                        model="llama3.2",
                        messages=[{
                            "role": "user",
                            "content": f"""<INSTRUCTION>
        You are a JSON generator. Respond with ONLY a JSON object.
        No introduction. No explanation. No markdown. No code blocks.
        Start your response with {{ and end with }}.
        </INSTRUCTION>

        Compare this resume against this job description.

        RESUME:
        {resume_text[:3000]}

        JOB DESCRIPTION:
        {job_description[:2000]}

        Respond with ONLY this exact JSON structure:
        {{
          "match_score": <integer 0-100>,
          "matching_skills": ["skill1", "skill2"],
          "missing_skills": ["skill1", "skill2"],
          "strengths": ["point1", "point2", "point3"],
          "recommendation": "one sentence honest assessment"
        }}"""
                        }]
                    )

                    raw = response['message']['content'].strip()


                    if "```json" in raw:
                        raw = raw.split("```json")[1].split("```")[0].strip()
                    elif "```" in raw:
                        raw = raw.split("```")[1].split("```")[0].strip()

                    # Step 2: Extract just the JSON object
                    if "{" in raw:
                        start = raw.index("{")
                        # If closing brace exists use it, otherwise add it
                        if "}" in raw:
                            end = raw.rindex("}") + 1
                            raw = raw[start:end]
                        else:
                            raw = raw[start:] + "}"

                    # Step 3: Parse
                    result = json.loads(raw)


                    st.markdown("---")

                    score = result.get("match_score", 0)
                    color = (
                        "green" if score >= 70
                        else "orange" if score >= 50
                        else "red"
                    )

                    st.markdown(
                        f"## Match Score: <span style='color:{color}'>{score}%</span>",
                        unsafe_allow_html=True
                    )

                    st.info(f"💬 {result.get('recommendation', '')}")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### ✅ Matching Skills")
                        for skill in result.get("matching_skills", []):
                            st.success(skill)

                        st.markdown("### 💪 Your Strengths")
                        for strength in result.get("strengths", []):
                            st.info(strength)

                    with col2:
                        st.markdown("### ❌ Missing Skills")
                        for skill in result.get("missing_skills", []):
                            st.warning(skill)

                except json.JSONDecodeError as e:
                    st.error("AI returned unexpected format. Click Analyse again.")
                    with st.expander("Debug info"):
                        st.code(raw)

                except ollama.ResponseError as e:
                    st.error(f"Ollama error: {e}")
                    st.info("Make sure Ollama is running: `ollama serve`")

                except Exception as e:
                    if "connection" in str(e).lower():
                        st.error("Cannot connect to Ollama.")
                        st.info("Run: `ollama serve`")
                    else:
                        st.error(f"Unexpected error: {e}")

    elif resume_text and not job_description:
        st.info("Resume uploaded. Now paste a job description above and click Analyse.")

    elif not resume_text:
        st.info("Upload your resume to get started.")



if page == "Job Explorer":

    st.subheader("📋 Latest Jobs")
    st.write(f"Showing **{len(filtered_jobs)}** jobs")

    for _, row in filtered_jobs.iterrows():

        with st.container():

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {row['title']}")
                st.markdown(
                    f"🏢 **{row['company']}**  |  📍 {row['location']}"
                )
                if row.get("tags"):
                    st.markdown(f"🏷️ `{row['tags']}`")

            with col2:
                if row.get("job_link"):
                    st.markdown(
                        f"[Apply →]({row['job_link']})",
                        unsafe_allow_html=True
                    )

            st.markdown("---")



st.markdown("---")
st.markdown("Built with Python · Ollama LLaMA 3.2 · NLP · Streamlit · Zero Cost")