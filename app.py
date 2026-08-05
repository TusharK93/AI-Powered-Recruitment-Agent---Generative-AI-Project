import streamlit as st

from services.pdf_parser import extract_pdf_text
from services.resume_extractor import clean_resume_text

from core.llm import get_llm

from agents.ats_agent import ATSAgent
from agents.interviewer_agent import InterviewerAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.rewrite_agent import RewriteAgent

from chains.format_chain import format_resume_chain

# ---------------- INIT ---------------- #

llm = get_llm()

ats_agent = ATSAgent(llm)
interview_agent = InterviewerAgent(llm)
evaluator_agent = EvaluatorAgent(llm)
rewrite_agent = RewriteAgent(llm)

SECTIONS = ["ATS Analysis", "Skills", "Interview", "Rewrite Resume"]

# ---------------- SESSION STATE ---------------- #

for key in (
    "resume_text",
    "ats",
    "skills",
    "source_file",
    "current_question",
    "latest_evaluation",
    "rewritten_resume",
    "html_resume"
):
    st.session_state.setdefault(key, None)

for key in ("questions", "answers", "evaluations"):
    st.session_state.setdefault(key, [])

st.session_state.setdefault("total_score", 0)

# ---------------- ANALYSIS PIPELINE ---------------- #

def run_analysis(cleaned_text: str):
    ats_result = ats_agent.run(cleaned_text)

    # skills are usually embedded in ATS or separate chain
    from chains.skill_chain import extract_skills_from_resume_chain
    skill_chain = extract_skills_from_resume_chain(cleaned_text, llm)
    skills_result = skill_chain.invoke({})

    st.session_state.ats = ats_result
    st.session_state.skills = skills_result

# ---------------- UI: ATS ---------------- #

def render_ats(ats):
    st.header("ATS Analysis")

    st.metric("ATS Score", ats.ats_score)

    st.subheader("Strengths")
    for item in ats.strengths:
        st.write(f"✅ {item}")

    st.subheader("Weaknesses")
    for item in ats.weaknesses:
        st.write(f"❌ {item}")

    st.subheader("Missing Keywords")
    for item in ats.missing_keywords:
        st.write(f"⚠️ {item}")

    st.subheader("Improvements")
    for item in ats.improvements:
        st.write(f"💡 {item}")

    st.subheader("Summary")
    st.write(ats.summary)

# ---------------- UI: SKILLS ---------------- #

def render_skills(skills):
    st.header("Skills Overview")

    if skills.candidate_name:
        st.markdown(f"**Candidate:** {skills.candidate_name}")

    if skills.target_role:
        st.markdown(f"**Target Role:** {skills.target_role}")

    st.subheader("Summary")
    st.write(skills.extraction_summary)

    st.subheader("All Skills")
    st.markdown(" ".join([f"`{s}`" for s in skills.skills_flat_list]))

# ---------------- UI: INTERVIEW ---------------- #

def render_interview():
    st.header("Mock Interview")

    completed = len(st.session_state.answers)
    avg_score = (
        st.session_state.total_score / completed if completed > 0 else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Questions", completed)
    col2.metric("Avg Score", round(avg_score, 1))
    col3.metric("Total Score", st.session_state.total_score)

    st.progress(min(completed / 10, 1.0))

    # Start interview
    if st.button("Start Mock Interview"):
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.evaluations = []
        st.session_state.total_score = 0

        q = interview_agent.run(
            name=st.session_state.skills.candidate_name,
            role=st.session_state.skills.target_role,
            skills=st.session_state.skills.skills_flat_list,
            previous_questions=[]
        )

        st.session_state.current_question = q
        st.session_state.questions.append(q)

    # Question flow
    if st.session_state.current_question:
        q = st.session_state.current_question

        st.subheader(f"Question ({q.difficulty})")
        st.info(q.question)

        answer = st.text_area("Your Answer")

        if st.button("Submit Answer"):
            evaluation = evaluator_agent.run(
                question=q.question,
                answer=answer,
                difficulty=q.difficulty
            )

            st.session_state.answers.append(answer)
            st.session_state.evaluations.append(evaluation)
            st.session_state.total_score += evaluation.overall_score

            next_q = interview_agent.run(
                name=st.session_state.skills.candidate_name,
                role=st.session_state.skills.target_role,
                skills=st.session_state.skills.skills_flat_list,
                previous_questions=st.session_state.questions
            )

            st.session_state.questions.append(next_q)
            st.session_state.current_question = next_q
            st.session_state.latest_evaluation = evaluation

            st.rerun()

    # Show last evaluation
    if st.session_state.latest_evaluation:
        e = st.session_state.latest_evaluation

        st.divider()
        st.subheader("Evaluation")

        col1, col2, col3 = st.columns(3)
        col1.metric("Overall", f"{e.overall_score}/10")
        col2.metric("Tech", f"{e.technical_accuracy}/10")
        col3.metric("Clarity", f"{e.clarity}/10")

        st.write("### Strengths")
        for s in e.strengths:
            st.write(f"✅ {s}")

        st.write("### Weaknesses")
        for w in e.weaknesses:
            st.write(f"❌ {w}")

        st.write("### Ideal Answer")
        st.info(e.ideal_answer)

# ---------------- UI: REWRITE RESUME ---------------- #

def render_rewrite():
    st.header("Rewrite Resume")

    job_role = st.text_input("Job Role")
    job_description = st.text_area("Job Description")

    if st.button("Rewrite Resume"):
        if not job_role or not job_description:
            st.warning("Please fill both fields")
            return

        rewritten = rewrite_agent.run(
            resume=st.session_state.resume_text,
            ats=st.session_state.ats,
            skills=st.session_state.skills.skills_flat_list,
            job_role=job_role,
            job_description=job_description
        )

        st.session_state.rewritten_resume = rewritten
        st.session_state.html_resume = None

    if st.session_state.rewritten_resume:
        st.subheader("Rewritten Resume")
        st.json(st.session_state.rewritten_resume.model_dump())

        if st.button("Format Resume (HTML)"):
            html = format_resume_chain(st.session_state.rewritten_resume)
            st.session_state.html_resume = html

    if st.session_state.html_resume:
        st.components.v1.html(st.session_state.html_resume, height=1000, scrolling=True)

        st.download_button(
            "Download HTML Resume",
            data=st.session_state.html_resume,
            file_name="resume.html",
            mime="text/html"
        )

# ---------------- MAIN APP ---------------- #

def main():
    st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

    with st.sidebar:
        st.title("AI Resume Analyzer")

        uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

        if uploaded_file:
            if uploaded_file.name != st.session_state.source_file:
                raw = extract_pdf_text(uploaded_file)
                cleaned = clean_resume_text(raw)

                if not cleaned:
                    st.error("Could not extract text")
                    return

                st.session_state.resume_text = cleaned
                st.session_state.source_file = uploaded_file.name

                with st.spinner("Analyzing resume..."):
                    run_analysis(cleaned)

                st.success("Analysis complete")

        section = st.radio("Navigate", SECTIONS)

    if not st.session_state.ats:
        st.title("Upload a resume to begin")
        return

    if section == "ATS Analysis":
        render_ats(st.session_state.ats)

    elif section == "Skills":
        render_skills(st.session_state.skills)

    elif section == "Interview":
        render_interview()

    elif section == "Rewrite Resume":
        render_rewrite()


if __name__ == "__main__":
    main()