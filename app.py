import streamlit as st

# ---------------------------
# ZAP Check Fraud Intake AI Agent (Demo)
# ---------------------------

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
