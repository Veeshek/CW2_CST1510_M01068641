
"""
Week 10 - AI Assistant (Multi-Domain)

This page:
- Auth protected
- Domain selection (Cybersecurity / Data Science / IT Ops)
- Can attach DB context (incident/dataset/ticket)
- Chat interface + streaming response
- Uses app/services/ai_assistant.py (safe + no crashes)
- Uses the SAME UI style + topbar (so you "have an AI tab")
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.db import connect_database
from app.services.ai_assistant import stream_chat_completion, safe_error_message
from app.ui import inject_global_css, topbar, auth_guard

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
auth_guard()
topbar("AI")

# -----------------------------
# Session state init
# -----------------------------
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []  # store only user/assistant messages

if "ai_domain" not in st.session_state:
    st.session_state.ai_domain = "Cybersecurity"

if "ai_context_text" not in st.session_state:
    st.session_state.ai_context_text = ""

# -----------------------------
# Header
# -----------------------------
user = st.session_state.get("user_info", {"username": "user", "role": "user"})
st.title("🤖 Multi-Domain AI Assistant")
st.caption(f"Logged in as: **{user.get('username','user')}** | Role: **{user.get('role','user')}**")
st.markdown("---")

# -----------------------------
# Controls (NOT Streamlit sidebar)
# Because we hide sidebar globally, we keep controls in the page.
# -----------------------------
st.subheader("🧠 Assistant Settings")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    st.session_state.ai_domain = st.selectbox(
        "Choose Domain Assistant",
        ["Cybersecurity", "Data Science", "IT Operations"],
        index=["Cybersecurity", "Data Science", "IT Operations"].index(st.session_state.ai_domain),
    )

with c2:
    st.metric("💬 Messages", len(st.session_state.ai_chat_history))

with c3:
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.ai_chat_history = []
        st.rerun()

st.markdown("---")

# -----------------------------
# DB Context Picker (Week 8 + Week 10 integration)
# -----------------------------
st.subheader("📌 Optional: Attach Database Context")

domain = st.session_state.ai_domain
conn = connect_database()

context_text = ""
context_label = ""

try:
    if domain == "Cybersecurity":
        df = pd.read_sql_query(
            "SELECT incident_id, timestamp, severity, category, status, description "
            "FROM cyber_incidents ORDER BY timestamp DESC LIMIT 50",
            conn,
        )

        if len(df) > 0:
            options = df.apply(
                lambda r: f"{r['incident_id']} | {r['severity']} | {r['category']} | {r['status']}",
                axis=1,
            ).tolist()

            idx = st.selectbox("Select an incident (latest 50)", range(len(options)), format_func=lambda i: options[i])

            row = df.iloc[idx].to_dict()
            context_label = "Selected Incident"
            context_text = (
                f"Incident ID: {row['incident_id']}\n"
                f"Timestamp: {row['timestamp']}\n"
                f"Severity: {row['severity']}\n"
                f"Category: {row['category']}\n"
                f"Status: {row['status']}\n"
                f"Description: {row['description']}\n"
            )

    elif domain == "Data Science":
        # NOTE: your DB might use different columns (source/size_mb/quality_score/status)
        # If your schema differs, update the SELECT to match your table columns.
        df = pd.read_sql_query(
            "SELECT * FROM datasets_metadata ORDER BY dataset_id DESC LIMIT 50",
            conn,
        )

        if len(df) > 0:
            # Build a readable label using columns that exist
            cols = df.columns.tolist()

            def label(r):
                base = f"{r.get('dataset_id','?')} | {r.get('name','dataset')}"
                if "uploaded_by" in cols:
                    base += f" | {r.get('uploaded_by','')}"
                return base

            options = df.apply(label, axis=1).tolist()
            idx = st.selectbox("Select a dataset (latest 50)", range(len(options)), format_func=lambda i: options[i])

            row = df.iloc[idx].to_dict()
            context_label = "Selected Dataset"
            # Dump selected row as context (simple & robust)
            context_text = "\n".join([f"{k}: {v}" for k, v in row.items()])

    else:  # IT Operations
        df = pd.read_sql_query(
            "SELECT * FROM it_tickets ORDER BY created_at DESC LIMIT 50",
            conn,
        )

        if len(df) > 0:
            cols = df.columns.tolist()

            def label(r):
                base = f"{r.get('ticket_id','?')} | {r.get('priority','')} | {r.get('status','')}"
                if "assigned_to" in cols:
                    base += f" | {r.get('assigned_to','')}"
                return base

            options = df.apply(label, axis=1).tolist()
            idx = st.selectbox("Select a ticket (latest 50)", range(len(options)), format_func=lambda i: options[i])

            row = df.iloc[idx].to_dict()
            context_label = "Selected Ticket"
            context_text = "\n".join([f"{k}: {v}" for k, v in row.items()])

finally:
    conn.close()

btn1, btn2 = st.columns(2)
with btn1:
    if st.button("📎 Attach Context to Chat", use_container_width=True, type="primary"):
        st.session_state.ai_context_text = context_text
        st.success("Context attached.")
        st.rerun()

with btn2:
    if st.button("❌ Remove Context", use_container_width=True):
        st.session_state.ai_context_text = ""
        st.info("Context removed.")
        st.rerun()

if st.session_state.ai_context_text:
    with st.expander(f"✅ {context_label} (attached)"):
        st.code(st.session_state.ai_context_text)

st.markdown("---")

# -----------------------------
# Chat UI
# -----------------------------
st.subheader("💬 Chat")

# Display history
for msg in st.session_state.ai_chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Ask the AI assistant...")

if user_input:
    # Add user message to history
    st.session_state.ai_chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Stream assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        try:
            for chunk in stream_chat_completion(
                domain=st.session_state.ai_domain,
                chat_history=st.session_state.ai_chat_history,
                extra_context=st.session_state.ai_context_text,
                model="gpt-4o-mini",
            ):
                full_reply += chunk
                placeholder.markdown(full_reply)

            if not full_reply.strip():
                full_reply = "I didn't receive any output. Please try again."
                placeholder.warning(full_reply)

        except Exception as e:
            full_reply = safe_error_message(e)
            placeholder.error(full_reply)

    # Save assistant reply
    st.session_state.ai_chat_history.append({"role": "assistant", "content": full_reply})
    st.rerun()

st.markdown("---")
st.caption("Week 10: AI Integration | Streamlit Chat UI | DB Context + Domain Prompts")
