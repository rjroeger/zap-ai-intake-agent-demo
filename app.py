import streamlit as st
import openai
from datetime import date

# ======================================================
# CONFIG
# ======================================================

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

st.set_page_config(
    page_title="Check Fraud Intake AI Agent",
    layout="centered",
)

# ======================================================
# SESSION STATE
# ======================================================

if "case" not in st.session_state:
    st.session_state.case = {
        "case_id": "",
        "open_date": date.today(),
        "customer_name": "",
        "account_number": "",
        "customer_contact": "",
        "original_check": {},
        "fraud_check": {},
        "fraud_type": "",
        "timeline": {},
        "attestation": {},
        "financials": {},
        "documents": {},
        "escalation_flags": {},
        "ai_followups": {},
    }

if "ai_step" not in st.session_state:
    st.session_state.ai_step = 0

if "human_decision" not in st.session_state:
    st.session_state.human_decision = None

# ======================================================
# AI FUNCTIONS
# ======================================================

def ai_followup_questions(case):
    prompt = f"""
You are a check fraud intake AI.

Based on the intake below, generate the MOST important follow‑up questions
needed to assess fraud liability and escalation.

Rules:
- 3–6 questions
- One per line
- No explanations

Intake:
{case}
"""
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message["content"]

def ai_reassess(case):
    prompt = f"""
You are a fraud risk analysis AI.

Using the intake and investigator answers, provide:

1. Short risk summary (2–3 sentences)
2. Key risk indicators (bullets)
3. Applicable warranty theory
4. Escalation should be considered? (yes/no)
5. Estimated fraud risk confidence (0–100%)

Case:
{case}
"""
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message["content"]

def ai_attorney_summary(case):
    prompt = f"""
Prepare a neutral, attorney‑ready check fraud escalation summary.

Rules:
- One page max
- Factual tone only
- No speculation
- Clear headings and bullets

Include:
- Case overview
- Banks involved
- Fraud type & applicable warranty
- Key risk indicators
- Outstanding items
- Financial exposure
- Recommended next action

Case:
{case}
"""
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return resp.choices[0].message["content"]

# ======================================================
# UI — INTAKE
# ======================================================

st.title("Check Fraud Intake AI Agent")

st.subheader("1. Case & Customer")

st.session_state.case["case_id"] = st.text_input("Internal Case / Claim ID")
st.session_state.case["open_date"] = st.date_input("Intake Open Date")
st.session_state.case["customer_name"] = st.text_input("Customer Name")
st.session_state.case["account_number"] = st.text_input("Customer Account Number")
st.session_state.case["customer_contact"] = st.text_input("Customer Contact (Email or Phone)")

st.subheader("2. Check at Issue — Original")

st.session_state.case["original_check"] = {
    "check_number": st.text_input("Check Number"),
    "issue_date": st.date_input("Issue Date"),
    "payee": st.text_input("Payee Name"),
    "amount": st.number_input("Amount", min_value=0.0),
}

st.subheader("3. Fraudulent Presentment")

st.session_state.case["fraud_check"] = {
    "date_negotiated": st.date_input("Date Negotiated"),
    "presented_payee": st.text_input("Fraudulent Payee (if different)"),
    "amount_presented": st.number_input("Amount Presented", min_value=0.0),
    "bofd": st.text_input("Bank of First Deposit (BOFD)"),
    "bofd_rtn": st.text_input("BOFD Routing Number"),
    "payor_bank": st.text_input("Payor Bank"),
    "deposit_method": st.selectbox(
        "Deposit Method",
        ["Branch", "ATM", "Mobile", "Remote Capture"]
    ),
}

st.subheader("4. Fraud Type")

st.session_state.case["fraud_type"] = st.radio(
    "Primary Fraud Classification",
    [
        "Altered Payee / Amount",
        "Forged Maker Signature",
        "Forged Endorsement",
        "Counterfeit Check",
        "Duplicate Presentment",
        "Other",
    ]
)

st.subheader("5. Timeline")

st.session_state.case["timeline"] = {
    "customer_notice_date": st.date_input("Date Customer Notified Bank"),
    "claim_sent_date": st.date_input("Date Claim Sent to BOFD"),
    "bofd_response": st.selectbox("BOFD Response", ["Pending", "Accepted", "Denied"]),
    "bofd_response_date": st.date_input("BOFD Response Date"),
}

st.subheader("6. Customer Attestation")

st.session_state.case["attestation"] = {
    "affidavit_received": st.checkbox("Customer Fraud Affidavit Received"),
    "date_received": st.date_input("Date Received"),
    "customer_statement": st.text_area(
        "Customer Statement (Brief Narrative)",
        height=80
    ),
}

st.subheader("7. Financial Exposure")

st.session_state.case["financials"] = {
    "total_fraud_amount": st.number_input("Total Fraud Amount", min_value=0.0),
    "provisional_credit": st.checkbox("Provisional Credit Issued"),
    "final_customer_impact": st.text_input("Final Customer Impact"),
}

st.subheader("8. Documentation Flags")

st.session_state.case["documents"] = {
    "check_images": st.checkbox("Check Image(s)"),
    "deposit_evidence": st.checkbox("Deposit Evidence"),
    "affidavit": st.checkbox("Customer Affidavit"),
    "signature_card": st.checkbox("Signature Card / Prior Signature"),
    "bofd_correspondence": st.checkbox("BOFD Correspondence"),
}

st.subheader("9. Escalation Signals")

st.session_state.case["escalation_flags"] = {
    "escalation_required": st.selectbox(
        "Escalation Required",
        ["None", "Legal", "Compliance"]
    ),
    "sar_flag": st.checkbox("SAR Filed or Required"),
}

st.divider()

# ======================================================
# AI AGENT FLOW
# ======================================================

if st.button("Run AI Intake Review"):
    st.session_state.ai_step = 1

if st.session_state.ai_step == 1:
    st.subheader("AI Follow‑Up Questions")

    qs = ai_followup_questions(st.session_state.case).split("\n")
    for i, q in enumerate(qs):
        if q.strip():
            st.session_state.case["ai_followups"][q] = st.radio(
                q, ["Unknown", "Yes", "No"], key=f"f_{i}"
            )

    if st.button("Submit Responses"):
        st.session_state.ai_step = 2

elif st.session_state.ai_step == 2:
    st.subheader("AI Risk Assessment")
    st.write(ai_reassess(st.session_state.case))

    st.subheader("Human Decision")
    st.session_state.human_decision = st.radio(
        "Next Action",
        ["Hold", "Escalate to Attorney", "Close"]
    )

    if st.button("Finalize"):
        st.session_state.ai_step = 3

elif st.session_state.ai_step == 3:
    st.subheader("Final Outcome")

    if st.session_state.human_decision == "Escalate to Attorney":
        st.subheader("Attorney Escalation Summary")
        st.write(ai_attorney_summary(st.session_state.case))
    else:
        st.info("No attorney escalation generated.")

    st.caption(
        "AI provides decision support only. All determinations are human‑made."
    )
