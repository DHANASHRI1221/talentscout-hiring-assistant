import streamlit as st
from prompts import generate_question_prompt, evaluate_answer_prompt
from llm_handler import ask_llm
from utils import extract_questions, parse_evaluation
from utils import check_similarity

st.set_page_config(page_title="TalentScout AI Hiring Assistant", layout="wide")

st.title("🤖 TalentScout AI Hiring Assistant")
st.markdown("Automated Technical Screening System")

# ---------- UI Styling ----------
st.markdown("""
<style>

.profile-card {
    background-color: #1e1e1e;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #444;
}

.profile-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
}

.tech-badge {
    display: inline-block;
    background-color: #2b7cff;
    color: white;
    padding: 4px 10px;
    border-radius: 8px;
    margin: 3px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "step" not in st.session_state:
    st.session_state.step = 0

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "scores" not in st.session_state:
    st.session_state.scores = []

candidate_questions = [
    "What is your full name?",
    "What is your email address?",
    "What is your phone number?",
    "Years of experience?",
    "Desired position?",
    "Current location?",
    "Enter your tech stack (comma separated)"
]

# ---------- Sidebar UI ----------
with st.sidebar:

    st.header("TalentScout AI")
    st.write("AI-powered technical screening assistant")

    candidate = st.session_state.candidate

    if candidate:

        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown('<div class="profile-title">👤 Candidate Profile</div>', unsafe_allow_html=True)

        st.write(f"**Name:** {candidate.get('name','-')}")
        st.write(f"**Email:** {candidate.get('email','-')}")
        st.write(f"**Phone:** {candidate.get('phone','-')}")
        st.write(f"**Experience:** {candidate.get('experience','-')} years")
        st.write(f"**Position:** {candidate.get('position','-')}")
        st.write(f"**Location:** {candidate.get('location','-')}")

        st.write("**Tech Stack:**")

        tech_stack = candidate.get("tech_stack","").split(",")

        for tech in tech_stack:
            st.markdown(
                f'<span class="tech-badge">{tech.strip()}</span>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

# ---------- Display Chat ----------
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------- Greeting ----------
if st.session_state.step == 0 and not st.session_state.chat_history:

    greeting = "Hello 👋 Welcome to TalentScout AI hiring assistant."
    first_question = candidate_questions[0]

    st.session_state.chat_history.append({"role":"assistant","content":greeting})
    st.session_state.chat_history.append({"role":"assistant","content":first_question})

    st.rerun()

# ---------- User Input ----------
user_input = st.chat_input("Type your answer")

if user_input:

    st.session_state.chat_history.append({"role":"user","content":user_input})

    step = st.session_state.step

    # ---------- Candidate Info Collection ----------
    if step < 6:

        keys = ["name","email","phone","experience","position","location"]
        st.session_state.candidate[keys[step]] = user_input

        next_q = candidate_questions[step+1]

        st.session_state.chat_history.append({
            "role":"assistant",
            "content":next_q
        })

        st.session_state.step += 1
        st.rerun()

    # ---------- Tech Stack ----------
    elif step == 6:

        st.session_state.candidate["tech_stack"] = user_input

        prompt = generate_question_prompt(user_input)
        response = ask_llm(prompt)

        questions = extract_questions(response)

        st.session_state.questions = questions
        st.session_state.step = 7

        name = st.session_state.candidate["name"]

        st.session_state.chat_history.append({
            "role":"assistant",
            "content":f"Great {name}! Let's begin your technical interview."
        })

        st.session_state.chat_history.append({
            "role":"assistant",
            "content":f"Question 1 of {len(questions)}"
        })

        st.session_state.chat_history.append({
            "role":"assistant",
            "content":questions[0]
        })

        st.rerun()

    # ---------- Interview Phase ----------
    elif step == 7:

        q_index = st.session_state.current_q
        question = st.session_state.questions[q_index]

        eval_prompt = evaluate_answer_prompt(question, user_input)
        evaluation = ask_llm(eval_prompt)

        score, sentiment, feedback = parse_evaluation(evaluation)

        st.session_state.scores.append(int(score))
        # ---------- Originality Check ----------
        reference_answer = question   # simple reference (can improve later)

        originality_score = check_similarity(user_input, reference_answer)

        st.session_state.chat_history.append({
            "role":"assistant",
            "content":f"""
Score: {score}/10

Sentiment: {sentiment}

Feedback: {feedback}

Originality Score: {originality_score}%
"""
        })

        st.session_state.current_q += 1

        # ---------- Next Question ----------
        if st.session_state.current_q < len(st.session_state.questions):

            next_q = st.session_state.questions[st.session_state.current_q]

            st.session_state.chat_history.append({
                "role":"assistant",
                "content":f"Question {st.session_state.current_q+1} of {len(st.session_state.questions)}"
            })

            st.session_state.chat_history.append({
                "role":"assistant",
                "content":next_q
            })

        # ---------- Interview Finished ----------
        else:

            avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
            verdict = "PASS" if avg_score >= 6 else "FAIL"

            if verdict == "PASS":

                final_message = f"""
Interview Completed

Average Score: {avg_score:.1f}/10

Final Verdict: PASS

Congratulations! You have passed the initial technical screening.

Our recruitment team will contact you soon for the next stage of the interview process.
"""

            else:

                final_message = f"""
Interview Completed

Average Score: {avg_score:.1f}/10

Final Verdict: FAIL

Thank you for participating in the TalentScout screening.

At this time we will not be moving forward, but we encourage you to continue improving your skills and apply again in the future.
"""

            st.session_state.chat_history.append({
                "role":"assistant",
                "content":final_message
            })

        st.rerun()

# ---------- Progress ----------
if st.session_state.questions:

    progress = st.session_state.current_q / len(st.session_state.questions)
    st.progress(progress)