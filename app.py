import streamlit as st
import openai

# ---------------------------
# ZAP Check Fraud Intake AI Agent (Demo)
# ---------------------------

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")


# ---------------------------
# Phase 3: Intake Rules
# ---------------------------
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
    state["escalation_ready"] = not missing_items and state["check_amount"] >= 10000

    return state


# ---------------------------
# Phase 4: AI Intake Guidance
# ---------------------------
def generate_ai_guidance(state):
    prompt = f"""
You are the ZAP Intake AI Agent.

Current intake:
{state}

Explain missing information, risks, and next steps.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.2,
    )
