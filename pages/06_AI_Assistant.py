"""
Week 10 + Week 11 - AI Assistant (Multi-Domain)

This page demonstrates:
- Week 10: AI integration with Streamlit chat (streaming responses)
- Week 9: authentication guard + consistent UI
- Week 8: database usage (incidents, datasets, tickets)
- Week 11: Object-Oriented Programming (OOP) refactoring

Key OOP concept (Week 11):
- We no longer manipulate raw SQL rows or dictionaries in the UI.
- We use:
    * Entity classes (SecurityIncident, Dataset, ITTicket)
    * Repository pattern to load objects from the database
- Each entity encapsulates both DATA and BEHAVIOUR.

.
"""

import streamlit as st
import sys
from pathlib import Path

# Make sure project root is in Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# UI helpers (same style as other pages)
from app.ui import inject_global_css, topbar, auth_guard

# AI service (Week 10)
from app.services.ai_assistant import stream_chat_completion, safe_error_message

# Repository layer (Week 11 - OOP)
from app.services.repository import Repository

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject global CSS and top navigation bar
inject_global_css()
auth_guard()
topbar("AI")

# -------------------------------------------------
# Session state initialization
# -------------------------------------------------
# Chat history: list of dicts -> {"role": "user"/"assistant", "content": "..."}
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []

# Selected AI domain
if "ai_domain" not in st.session_state:
    st.session_state.ai_domain = "Cybersecurity"

# Extra context injected into the AI prompt
if "ai_context_text" not in st.session_state:
    st.session_state.ai_context_text = ""

# -------------------------------------------------
# Header
# -------------------------------------------------
user = st.session_state.get("user_info", {"username": "user", "role": "user"})

st.title("🤖 Multi-Domain AI Assistant")
st.caption(
    f"Logged in as: **{user.get('username','user')}** "
    f"| Role: **{user.get('role','user')}**"
)
st.markdown("---")

# -------------------------------------------------
# Assistant controls (no Streamlit sidebar)
# -------------------------------------------------
st.subheader("🧠 Assistant Settings")

c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    st.session_state.ai_domain = st.selectbox(
        "Choose Domain Assistant",
        ["Cybersecurity", "Data Science", "IT Operations"],
        index=["Cybersecurity", "Data Science", "IT Operations"].index(
            st.session_state.ai_domain
        ),
    )

with c2:
    st.metric("💬 Messages", len(st.session_state.ai_chat_history))

with c3:
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.ai_chat_history = []
        st.rerun()

st.markdown("---")

# -------------------------------------------------
# Database Context Picker (Week 8 + Week 11 OOP)
# -------------------------------------------------
st.subheader("📌 Optional: Attach Database Context")

# Create repository instance (Week 11)
repo = Repository()

context_text = ""
context_label = ""
domain = st.session_state.ai_domain

# ---- Cybersecurity domain ----
if domain == "Cybersecurity":
    incidents = repo.get_latest_incidents(limit=50)

    if incidents:
        labels = [inc.short_label() for inc in incidents]
        idx = st.selectbox(
            "Select an incident (latest 50)",
            range(len(labels)),
            format_func=lambda i: labels[i],
        )

        selected_incident = incidents[idx]
        context_label = "Selected Incident (OOP Entity)"
        context_text = selected_incident.to_prompt_context()

# ---- Data Science domain ----
elif domain == "Data Science":
    datasets = repo.get_latest_datasets(limit=50)

    if datasets:
        labels = [ds.short_label() for ds in datasets]
        idx = st.selectbox(
            "Select a dataset (latest 50)",
            range(len(labels)),
            format_func=lambda i: labels[i],
        )

        selected_dataset = datasets[idx]
        context_label = "Selected Dataset (OOP Entity)"
        context_text = selected_dataset.to_prompt_context()

# ---- IT Operations domain ----
else:
    tickets = repo.get_latest_tickets(limit=50)

    if tickets:
        labels = [t.short_label() for t in tickets]
        idx = st.selectbox(
            "Select a ticket (latest 50)",
            range(len(labels)),
            format_func=lambda i: labels[i],
        )

        selected_ticket = tickets[idx]
        context_label = "Selected Ticket (OOP Entity)"
        context_text = selected_ticket.to_prompt_context()

# Context buttons
b1, b2 = st.columns(2)

with b1:
    if st.button("📎 Attach Context to Chat", use_container_width=True, type="primary"):
        st.session_state.ai_context_text = context_text
        st.success("Context attached to AI chat.")
        st.rerun()

with b2:
    if st.button("❌ Remove Context", use_container_width=True):
        st.session_state.ai_context_text = ""
        st.info("Context removed.")
        st.rerun()

# Display attached context
if st.session_state.ai_context_text:
    with st.expander(f"✅ {context_label} (attached)"):
        st.code(st.session_state.ai_context_text)

st.markdown("---")

# -------------------------------------------------
# Chat Interface (Week 10)
# -------------------------------------------------
st.subheader("💬 Chat")

# Display previous messages
for msg in st.session_state.ai_chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input field
user_input = st.chat_input(
    "Ask the AI assistant (e.g. 'Analyze this incident and recommend actions')"
)

if user_input:
    # 1) Save user message
    st.session_state.ai_chat_history.append(
        {"role": "user", "content": user_input}
    )

    # 2) Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # 3) Stream assistant response
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
                full_reply = "No response generated. Please try again."
                placeholder.warning(full_reply)

        except Exception as e:
            full_reply = safe_error_message(e)
            placeholder.error(full_reply)

    # 4) Save assistant reply
    st.session_state.ai_chat_history.append(
        {"role": "assistant", "content": full_reply}
    )

    # 5) Rerun to refresh UI
    st.rerun()

st.markdown("---")
st.caption(
    "Week 10: AI Integration | "
    "Week 11: OOP Entities + Repository Pattern | "
    "Secure & Modular Design"
)
