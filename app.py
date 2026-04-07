import streamlit as st
import openai

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

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


def generate_ai_guidance(state):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are the ZAP Intake AI Agent."},
                {"role": "user", "content": str(state)},
            ],
            temperature=0.2,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"OpenAI error: {e}"


def generate_attorney_summary(state):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Prepare a neutral attorney summary."},
                {"role": "user", "content": str(state)},
            ],
            temperature=0.1,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"OpenAI error: {e}"


st.title("ZAP Check Fraud Intake AI Agent")

if "case_state" not in st.session_state:
    st.session_state.case_state = {
        "check_amount": 0,
        "check_number": "",
        "payee": "",
        "customer_affidavit": False,
        "check_image": False,
        "missing_items": [],
        "escalation_ready": False,
    }

st.subheader("Fraud Intake")

st.session_state.case_state["check_amount"] = st.number_input("Check Amount ($)", min_value=0)
st.session_state.case_state["check_number"] = st.text_input("Check Number")
st.session_state.case_state["payee"] = st.text_input("Payee Name")
st.session_state.case_state["customer_affidavit"] = st.checkbox("Customer Affidavit Received")
st.session_state.case_state["check_image"] = st.checkbox("Check Image Uploaded")

st.divider()

if st.button("Evaluate Intake"):
    st.session_state.case_state = evaluate_intake(st.session_state.case_state)

    if st.session_state.case_state["missing_items"]:
        st.error("Missing or incomplete intake items:")
        for item in st.session_state.case_state["missing_items"]:
            st.write(f"- {item}")
    else:
        st.success("Intake is complete.")

    st.subheader("AI Agent Guidance")
    st.write(generate_ai_guidance(st.session_state.case_state))

    if st.session_state.case_state["escalation_ready"]:
        st.divider()
        st.subheader("Attorney Escalation Package")
        st.write(generate_attorney_summary(st.session_state.case_state))
