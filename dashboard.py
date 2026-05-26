import streamlit as st
import pandas as pd
import plotly.express as px
import pdfplumber
from docx import Document
# =========================
# CUSTOM STYLING
# =========================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1, h2, h3, h4 {
    color: white;
}

[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #333;
    padding: 15px;
    border-radius: 12px;
}

.stDataFrame {
    background-color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)
# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Job Market Intelligence",
    layout="wide"
)

st.markdown("""
# 🚀 AI Job Market Intelligence Platform

### Real-time AI-powered job analytics, resume matching, and market intelligence
""")

# =========================
# LOAD DATA
# =========================

jobs_df = pd.read_csv("data/jobs.csv")
skills_df = pd.read_csv("data/skills_analysis.csv")

# =========================
# SIDEBAR MENU
# =========================

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Resume Matcher",
        "Job Explorer"
    ]
)

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("Filters")

locations = jobs_df["location"].dropna().unique()

selected_location = st.sidebar.selectbox(
    "Select Location",
    ["All"] + list(locations)
)

skill_search = st.sidebar.text_input(
    "Search Skill"
)

# =========================
# FILTER LOGIC
# =========================

filtered_jobs = jobs_df.copy()

# Location filter
if selected_location != "All":

    filtered_jobs = filtered_jobs[
        filtered_jobs["location"] == selected_location
    ]

# Skill filter
if skill_search:

    filtered_jobs = filtered_jobs[
        filtered_jobs["description"].str.contains(
            skill_search,
            case=False,
            na=False
        )
    ]

# =========================
# DASHBOARD PAGE
# =========================

if page == "Dashboard":

    # =========================
    # METRICS
    # =========================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Jobs",
            len(jobs_df)
        )

    with col2:
        st.metric(
            "Unique Skills",
            len(skills_df)
        )
    with col3:
        st.metric(
            "Top Skill",
            skills_df.iloc[0]["Skill"]
        )

    # =========================
    # TOP SKILLS CHART
    # =========================

    st.subheader("🔥 Top Skills")

    fig = px.bar(
        skills_df.head(15),
        x="Skill",
        y="Count",
        title="Most In-Demand Skills",
        text="Count"
    )
    fig.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =========================
    # TOP LOCATIONS
    # =========================

    st.subheader("🌍 Top Hiring Locations")

    location_counts = (
        jobs_df["location"]
        .value_counts()
        .head(10)
    )

    location_fig = px.pie(
        names=location_counts.index,
        values=location_counts.values,
        title="Top Job Locations"
    )
    location_fig.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        location_fig,
        use_container_width=True
    )

    # =========================
    # TOP COMPANIES
    # =========================

    st.subheader("🏢 Companies Hiring Most")

    company_counts = (
        jobs_df["company"]
        .value_counts()
        .reset_index()
    )

    company_counts.columns = [
        "Company",
        "Open Roles"
    ]

    st.dataframe(
        company_counts.head(10),
        hide_index=True
    )

# =========================
# RESUME MATCHER PAGE
# =========================

if page == "Resume Matcher":

    st.subheader("🧠 AI Resume Matcher")

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx", "txt"]
    )

    resume_text = ""

    if uploaded_file is not None:

        # PDF
        if uploaded_file.name.endswith(".pdf"):

            with pdfplumber.open(uploaded_file) as pdf:

                for page_pdf in pdf.pages:
                    resume_text += page_pdf.extract_text() or ""

        # DOCX
        elif uploaded_file.name.endswith(".docx"):

            doc = Document(uploaded_file)

            for para in doc.paragraphs:
                resume_text += para.text + "\n"

        # TXT
        elif uploaded_file.name.endswith(".txt"):

            resume_text = str(
                uploaded_file.read(),
                "utf-8"
            )

        st.success("Resume uploaded successfully!")

    # =========================
    # MATCHING LOGIC
    # =========================

    if resume_text:

        match_scores = []

        for index, row in jobs_df.iterrows():

            description = str(
                row["description"]
            ).lower()

            score = 0

            matched_skills = []

            for skill in skills_df["Skill"]:

                if (
                    skill.lower() in resume_text.lower()
                    and skill.lower() in description
                ):

                    score += 1
                    matched_skills.append(skill)

            match_scores.append(score)

            jobs_df.loc[
                index,
                "matched_skills"
            ] = ", ".join(matched_skills)

        jobs_df["match_score"] = match_scores

        max_score = (
            max(match_scores)
            if max(match_scores) > 0
            else 1
        )

        jobs_df["match_percentage"] = (
            jobs_df["match_score"]
            / max_score * 100
        ).round(0)

        matched_jobs = jobs_df.sort_values(
            by="match_score",
            ascending=False
        )

        st.subheader("🎯 Best Matching Jobs")

        st.dataframe(
            matched_jobs[
                [
                    "title",
                    "company",
                    "location",
                    "match_percentage",
                    "matched_skills"
                ]
            ].head(10),
            hide_index=True
        )
        # =========================
        # SKILL GAP ANALYSIS
        # =========================

        st.subheader("📈 Skill Gap Analysis")

        resume_skills = []

        for skill in skills_df["Skill"]:

            if skill.lower() in resume_text.lower():
                resume_skills.append(skill)

        market_skills = skills_df["Skill"].head(15).tolist()

        missing_skills = [
            skill
            for skill in market_skills
            if skill not in resume_skills
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### ✅ Skills Found")

            for skill in resume_skills:
                st.success(skill)

        with col2:

            st.markdown("### ❌ Missing High-Demand Skills")

            for skill in missing_skills:
                st.warning(skill)

# =========================
# JOB EXPLORER PAGE
# =========================

if page == "Job Explorer":

    st.subheader("📋 Latest Jobs")

    st.dataframe(
        filtered_jobs[
            [
                "title",
                "company",
                "location",
                "tags"
            ]
        ],
        hide_index=True
    )

# =========================
# FOOTER
# =========================

st.markdown("---")

st.markdown(
    "Built with Python, APIs, NLP, AI Matching, and Streamlit"
)