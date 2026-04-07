import streamlit as st
import openai

# ======================================================
# CONFIGURATION
# ======================================================

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

st.set_page_config(
    page_title="ZAP Check Fraud Intake AI Agent",
    layout="centered",
)

# ======================================================
# SESSION STATE INITIALIZATION
# ======================================================

if "case_state" not in st.session_state:
    st.session_state.case_state = {
        "check_amount": 0,
        "check_number": "",
        "payee": "",
        "customer_affidavit": False,
        "check_image": False,
        "missing_items": [],
        "escalation_ready": False,
        "ai_followups": {},
    }

if "ai_step" not in st.session_state:
    st.session_state.ai_step = 0

if "human_decision" not in st.session_state:
    st.session_state.human_decision = None


# ======================================================
# CORE INTAKE LOGIC
# ======================================================

def evaluate_intake(state):
    required_fields = {
        "check_amount": "Check amount is required",
        "check_number": "Check number is required",
        "payee": "Payee name is required",
        "customer_affidavit": "Customer affidavit has not been received",
        "check_image": "Check image has not been uploaded",
    }

    missing_items = []
    for field, message in required_fields.items():
        if state.get(field) in [None, "", False]:
            missing_items.append(message)

    state["missing_items"] = missing_items
    state["escalation_ready"] = (not missing_items) and (state["check_amount"] >= 10000)
    return state


# ======================================================
# AI FUNCTIONS — STEP 1: FOLLOW-UP QUESTIONS
# ======================================================

def ai_generate_followups(state):
    try:
        prompt = f"""
You are a fraud intake AI assistant.

Based on the case below, identify the MOST important follow-up questions
a human investigator should answer next.

Rules:
- Return 3–6 questions
- One question per line
- No explanations
- No numbering

Case:
{state}
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message["content"]

    except Exception as e:
        return f"OpenAI error: {e}"


# ======================================================
# AI FUNCTIONS — STEP 2: REASSESSMENT
# ======================================================

def ai_reassess_risk(state):
    try:
        prompt = f"""
You are a fraud risk analysis AI.

Using the intake details and investigator responses below, provide:

1. A short risk summary (2–3 sentences)
2. Key remaining risk indicators (bullets)
3. Whether escalation SHOULD BE CONSIDERED (yes/no)
4. Estimated fraud risk confidence (0–100%)

Case:
{state}

Investigator responses:
{state.get("ai_followups", {})}
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message["content"]

    except Exception as e:
        return f"OpenAI error: {e}"


# ======================================================
# AI FUNCTIONS — STEP 3: ATTORNEY ESCALATION SUMMARY
# ======================================================

def ai_generate_attorney_summary(state):
    try:
        prompt = f"""
You are preparing a concise escalation summary for an attorney.

Rules:
- One page or less
- Neutral, factual tone
- No speculation
- Clear headings and bullets
- Assume attorney audience

Include:
- Case overview
- Key risk indicators
- Outstanding items
- AI risk assessment
- Human escalation decision

Case details:
{state}
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message["content"]

    except Exception as e:
        return f"OpenAI error: {e}"


# ======================================================
# UI — INTAKE FORM
# ======================================================

st.title("ZAP Check Fraud Intake AI Agent")
st.subheader("Fraud Intake")

st.session_state.case_state["check_amount"] = st.number_input(
    "Check Amount ($)", min_value=0
)
st.session_state.case_state["check_number"] = st.text_input("Check Number")
st.session_state.case_state["payee"] = st.text_input("Payee Name")
st.session_state.case_state["customer_affidavit"] = st.checkbox(
    "Customer Affidavit Received"
)
st.session_state.case_state["check_image"] = st.checkbox(
    "Check Image Uploaded"
)

st.divider()

# ======================================================
# INTAKE EVALUATION
# ======================================================

if st.button("Evaluate Intake"):
    st.session_state.case_state = evaluate_intake(
        st.session_state.case_state
    )
    st.session_state.ai_step = 1

if st.session_state.case_state.get("missing_items"):
    st.error("Missing or incomplete intake items:")
    for item in st.session_state.case_state["missing_items"]:
        st.write(f"- {item}")
elif st.session_state.ai_step > 0:
    st.success("Initial intake complete.")

# ======================================================
# AI AGENT — STEP 1: FOLLOW-UPS
# ======================================================

if st.session_state.ai_step == 1:
    st.divider()
    st.subheader("AI Agent Guidance — Follow-Up Questions")

    questions_text = ai_generate_followups(st.session_state.case_state)
    questions = questions_text.split("\n")

    for idx, q in enumerate(questions):
        if q.strip():
            st.session_state.case_state["ai_followups"][q] = st.radio(
                q,
                ["Unknown", "Yes", "No"],
                key=f"followup_{idx}"
            )

    if st.button("Submit Responses"):
        st.session_state.ai_step = 2

# ======================================================
# AI AGENT — STEP 2: REASSESSMENT + DECISION
# ======================================================

elif st.session_state.ai_step == 2:
    st.divider()
    st.subheader("AI Agent Assessment")

    assessment = ai_reassess_risk(st.session_state.case_state)
    st.write(assessment)

    with st.expander("Why the AI flagged this"):
        st.write(
            "The AI assessment reflects check amount, payee risk, documentation status, "
            "and investigator-confirmed responses."
        )

    st.divider()
    st.subheader("Human Decision Required")

    st.session_state.human_decision = st.radio(
        "Select next action",
        ["Hold for more information", "Escalate to attorney", "Close intake"]
    )

    if st.button("Finalize Decision"):
        st.session_state.ai_step = 3

# ======================================================
# AI AGENT — STEP 3: FINAL OUTCOME + ATTORNEY SUMMARY
# ======================================================

elif st.session_state.ai_step == 3:
    st.divider()
    st.subheader("Final Outcome")

    st.success("✅ Decision Recorded")
    st.write("**Final Determination:**")
    st.write(st.session_state.human_decision)

    if st.session_state.human_decision == "Escalate to attorney":
        st.divider()
        st.subheader("Attorney Escalation Summary")

        summary = ai_generate_attorney_summary(
            st.session_state.case_state
        )
        st.write(summary)

        st.caption(
            "This summary is AI‑generated for attorney review only. "
            "It is decision support and must be independently verified."
        )
    else:
        st.info("No attorney escalation summary generated.")

    st.caption(
        "Note: AI provides decision support only. Final determinations are human-made."
    )
