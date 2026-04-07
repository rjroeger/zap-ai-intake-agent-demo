import streamlit as st
import openai
``

# ---------------------------
# ZAP Check Fraud Intake AI Agent (Demo)
# ---------------------------

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

def evaluate_intake(state):
    """
    Evaluates intake completeness and determines escalation readiness.
    This logic is deterministic and demo-safe.
    """

    required_fields = {
        "check_amount": "Check amount is required",
        "check_number": "Check number is required",
        "payee": "Payee name is required",
        "customer_affidavit": "Customer affidavit has not been received",
        "check_image": "Check image has not been uploaded",
    }

    missing_items = []

    for field, message in required_fields.items():
        value = state.get(field)

        if value in [None, "", False]:
            missing_items.append(message)

    state["missing_items"] = missing_items

    # Escalation rule (business logic — adjust as needed)
    if not missing_items and state["check_amount"] >= 10000:
        state["escalation_ready"] = True
    else:
        state["escalation_ready"] = False

    return state

def generate_ai_guidance(state):
    """
    Uses AI to explain intake gaps, suggest follow-up questions,
    and assess escalation readiness in plain language.
    """

    prompt = f"""
You are the ZAP Intake AI Agent.

Your role is to assist an internal check fraud investigation team.

DO NOT:
- Provide legal advice
- Make legal conclusions
- Determine liability

DO:
- Identify missing or unclear intake details
- Suggest specific follow-up questions
- Explain risks of incomplete intake
- Comment on escalation readiness based on provided state

Current intake state:
{state}

Respond using the following structure:

1. Intake Completeness Assessment
2. Missing or Unclear Information
3. Suggested Follow-Up Questions
4. Escalation Readiness Commentary
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt}
        ],
        temperature=0.2,
    )

    return response.choices[0].message["content"]

st.success(
            "🔒 This case has met escalation criteria and is ready for attorney review."
        )
``

def generate_attorney_summary(state):
    """
    Produces a structured, attorney-ready case summary.
    No legal advice. Fact-based only.
    """

    prompt = f"""
You are the ZAP Attorney Preparation Agent.

You assist by organizing check fraud cases
for efficient attorney review.

DO NOT:
- Provide legal advice
- Suggest legal strategy
- Make liability determinations

DO:
- Summarize facts clearly and neutrally
- Organize information chronologically
- Identify evidence collected
- Call out remaining gaps or questions

Case intake and investigation state:
{state}

Respond using the following structure:

1. Case Overview
2. Key Facts (Chronological)
3. Parties Involved
4. Evidence Collected
5. Outstanding Gaps or Questions
6. Reason for Escalation
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt}
        ],
        temperature=0.1,
    )

    return response.choices[0].message["content"]

st.title("ZAP Check Fraud Intake AI Agent")

# Initialize case state (this makes it an AGENT, not a chatbot)
if "case_state" not in st.session_state:
    st.session_state.case_state = {
        "check_amount": None,
        "check_number": "",
        "payee": "",
        "customer_affidavit": False,
        "check_image": False,
        "missing_items": [],
        "escalation_ready": False,
    }

st.subheader("Fraud Intake")

# Intake fields
st.session_state.case_state["check_amount"] = st.number_input(
    "Check Amount ($)", min_value=0
)

st.session_state.case_state["check_number"] = st.text_input(
    "Check Number"
)

st.session_state.case_state["payee"] = st.text_input(
    "Payee Name"
)

st.session_state.case_state["customer_affidavit"] = st.checkbox(
    "Customer Affidavit Received"
)

st.session_state.case_state["check_image"] = st.checkbox(
    "Check Image Uploaded"
)

st.divider()

if st.button("Evaluate Intake"):
    st.session_state.case_state = evaluate_intake(
        st.session_state.case_state
    )


if st.session_state.case_state["missing_items"]:
        st.error("The following intake items are missing or incomplete:")

        for item in st.session_state.case_state["missing_items"]:
            st.write(f"- {item}")

        st.warning(
            "Proceeding without these details increases investigation and legal risk."
        )

if st.session_state.case_state["escalation_ready"]:
        st.success(
            "✅ Intake is complete and meets criteria for attorney escalation."
        )
    elif not st.session_state.case_state["missing_items"]:
        st.info(
            "ℹ️ Intake is complete but does not yet meet escalation thresholds."
        )

    st.subheader("Intake Assessment Results")

st.subheader("AI Agent Guidance")

    ai_response = generate_ai_guidance(
        st.session_state.case_state
    )

    with st.container(border=True):
    st.write(ai_response)

if st.session_state.case_state["escalation_ready"]:
        st.divider()
        st.subheader("Attorney Escalation Package")

        attorney_summary = generate_attorney_summary(
            st.session_state.case_state
        )

        with st.container(border=True):
            st.write(attorney_summary)
``
