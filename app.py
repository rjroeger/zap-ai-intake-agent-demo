import streamlit as st

# ---------------------------
# ZAP Check Fraud Intake AI Agent (Demo)
# ---------------------------

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

st.write("✅ Intake fields captured. Assessment logic will run next.")
