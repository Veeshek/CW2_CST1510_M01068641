"""
Multi-Domain AI Assistant Page

This page demonstrates integration of all course concepts:
- Week 7: Authentication & session management
- Week 8: Database queries and data retrieval
- Week 9: Streamlit UI components and layout
- Week 10: OpenAI API integration with streaming responses
- Week 11: OOP design with Repository pattern and Entity classes

The AI assistant can provide domain-specific guidance for:
- Cybersecurity incident response
- Data science analytics and governance
- IT operations ticket management

Users can attach database context (incidents/datasets/tickets) to get
more accurate and relevant AI recommendations.
"""

import streamlit as st
import sys
from pathlib import Path

# Make sure project root is in Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# UI helpers (consistent style across all pages)
from app.ui import inject_global_css, topbar, auth_guard

# AI service (Week 10 - OpenAI integration)
from app.services.ai_assistant import stream_chat_completion

# Repository layer (Week 11 - OOP pattern for database access)
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

# Apply global CSS styling and show top navigation
inject_global_css()
auth_guard()  # Protect this page - must be logged in
topbar("AI")


# -------------------------------------------------
# Session state initialization
# -------------------------------------------------
# Chat history stores the conversation as a list of message dictionaries
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []

# Currently selected domain (Cybersecurity, Data Science, or IT Operations)
if "ai_domain" not in st.session_state:
    st.session_state.ai_domain = "Cybersecurity"

# Extra context from database (attached incident/dataset/ticket)
if "ai_context_text" not in st.session_state:
    st.session_state.ai_context_text = ""


# -------------------------------------------------
# Header section
# -------------------------------------------------
user = st.session_state.get("user_info", {"username": "user", "role": "user"})

st.title("🤖 Multi-Domain AI Assistant")
st.caption(
    f"Logged in as: **{user.get('username','user')}** "
    f"| Role: **{user.get('role','user')}**"
)
st.markdown("---")


# -------------------------------------------------
# Assistant Settings - Domain Selection
# -------------------------------------------------
st.subheader("🧠 Assistant Settings")

c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    # Domain selector - determines which AI system prompt to use
    st.session_state.ai_domain = st.selectbox(
        "Choose Domain Assistant",
        ["Cybersecurity", "Data Science", "IT Operations"],
        index=["Cybersecurity", "Data Science", "IT Operations"].index(
            st.session_state.ai_domain
        ),
    )

with c2:
    # Show how many messages in current conversation
    st.metric("💬 Messages", len(st.session_state.ai_chat_history))

with c3:
    # Clear conversation button
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.ai_chat_history = []
        st.session_state.ai_context_text = ""
        st.rerun()

st.markdown("---")


# -------------------------------------------------
# Database Context Picker (Week 8 + Week 11 OOP)
# -------------------------------------------------
st.subheader("📌 Optional: Attach Database Context")

st.write(
    "Select an item from the database to give the AI specific context. "
    "This helps the AI provide more accurate and relevant recommendations."
)

# Create repository instance (Week 11 OOP pattern)
repo = Repository()

context_text = ""
context_label = ""
domain = st.session_state.ai_domain

# -------------------------------------------------
# CYBERSECURITY DOMAIN
# -------------------------------------------------
if domain == "Cybersecurity":
    try:
        # Use repository to get SecurityIncident objects (not raw SQL)
        incidents = repo.get_latest_incidents(limit=50)

        if incidents:
            # Create dropdown labels using the entity's method
            labels = [inc.short_label() for inc in incidents]
            
            idx = st.selectbox(
                "Select an incident (latest 50)",
                range(len(labels)),
                format_func=lambda i: labels[i],
            )

            # Get the selected incident object
            selected_incident = incidents[idx]
            context_label = "Selected Incident (OOP Entity)"
            
            # Use the entity's method to format context for AI
            context_text = selected_incident.to_prompt_context()
            
        else:
            st.info("No incidents found in database")
            
    except Exception as e:
        st.error(f"Error loading incidents: {str(e)}")
        st.info("Make sure the database is initialized with data")


# -------------------------------------------------
# DATA SCIENCE DOMAIN
# -------------------------------------------------
elif domain == "Data Science":
    try:
        # Use repository to get Dataset objects
        datasets = repo.get_latest_datasets(limit=50)

        if datasets:
            # Create dropdown labels
            labels = [ds.short_label() for ds in datasets]
            
            idx = st.selectbox(
                "Select a dataset (latest 50)",
                range(len(labels)),
                format_func=lambda i: labels[i],
            )

            # Get selected dataset object
            selected_dataset = datasets[idx]
            context_label = "Selected Dataset (OOP Entity)"
            
            # Format for AI context
            context_text = selected_dataset.to_prompt_context()
            
        else:
            st.info("No datasets found in database")
            
    except Exception as e:
        st.error(f"Error loading datasets: {str(e)}")
        st.info("Make sure the database is initialized with data")


# -------------------------------------------------
# IT OPERATIONS DOMAIN
# -------------------------------------------------
else:  # IT Operations
    try:
        # Use repository to get ITTicket objects
        tickets = repo.get_latest_tickets(limit=50)

        if tickets:
            # Create dropdown labels
            labels = [t.short_label() for t in tickets]
            
            idx = st.selectbox(
                "Select a ticket (latest 50)",
                range(len(labels)),
                format_func=lambda i: labels[i],
            )

            # Get selected ticket object
            selected_ticket = tickets[idx]
            context_label = "Selected Ticket (OOP Entity)"
            
            # Format for AI context
            context_text = selected_ticket.to_prompt_context()
            
        else:
            st.info("No tickets found in database")
            
    except Exception as e:
        st.error(f"Error loading tickets: {str(e)}")
        st.info("Make sure the database is initialized with data")


# -------------------------------------------------
# Context Attachment Controls
# -------------------------------------------------
st.write("")

b1, b2 = st.columns(2)

with b1:
    # Attach button - saves context to session state
    if st.button("📎 Attach Context to Chat", use_container_width=True, type="primary"):
        st.session_state.ai_context_text = context_text
        st.success("Context attached! The AI will use this information in its responses.")
        st.rerun()

with b2:
    # Remove button - clears attached context
    if st.button("❌ Remove Context", use_container_width=True):
        st.session_state.ai_context_text = ""
        st.info("Context removed.")
        st.rerun()

# Display currently attached context if any
if st.session_state.ai_context_text:
    with st.expander(f"✅ {context_label} (currently attached)", expanded=False):
        st.code(st.session_state.ai_context_text, language="text")

st.markdown("---")


# -------------------------------------------------
# Chat Interface (Week 10 - Streaming AI)
# -------------------------------------------------
st.subheader("💬 Chat with AI Assistant")

# Display all previous messages from chat history
for msg in st.session_state.ai_chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input field (appears at bottom of chat)
user_input = st.chat_input(
    "Ask the AI assistant (e.g., 'Analyze this incident and recommend containment steps')"
)

# -------------------------------------------------
# Handle new user message
# -------------------------------------------------
if user_input:
    # Add user message to history
    st.session_state.ai_chat_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)
    
    # Display AI response with streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream AI response chunk by chunk (Week 10 feature)
            for chunk in stream_chat_completion(
                domain=st.session_state.ai_domain,
                chat_history=st.session_state.ai_chat_history,
                extra_context=st.session_state.ai_context_text,
            ):
                full_response += chunk
                # Update placeholder with accumulated response
                response_placeholder.markdown(full_response + "▌")
            
            # Final response without cursor
            response_placeholder.markdown(full_response)
            
        except Exception as e:
            # Graceful error handling - don't crash the app
            error_msg = f"⚠️ AI Error: {str(e)}\n\nPlease check your API key configuration."
            response_placeholder.error(error_msg)
            full_response = error_msg
    
    # Add AI response to history
    st.session_state.ai_chat_history.append({
        "role": "assistant",
        "content": full_response
    })
    
    # Rerun to update the interface
    st.rerun()


# -------------------------------------------------
# Help Section
# -------------------------------------------------
st.write("")
st.write("---")

with st.expander("ℹ️ How to use the AI Assistant"):
    st.markdown("""
    **Getting Started:**
    1. Select your domain (Cybersecurity, Data Science, or IT Operations)
    2. Optionally attach database context for more specific advice
    3. Ask questions in the chat box
    
    **Example Questions:**
    
    **Cybersecurity:**
    - "What are the recommended steps to contain this phishing incident?"
    - "How should I prioritize incidents based on severity?"
    - "What indicators of compromise should I look for?"
    
    **Data Science:**
    - "Should this dataset be archived based on its size and age?"
    - "What quality issues might cause a low quality score?"
    - "How can I improve data governance for this source?"
    
    **IT Operations:**
    - "Why is this ticket taking so long to resolve?"
    - "What's the recommended priority for this issue?"
    - "How can we reduce resolution times?"
    
    **Features:**
    - 🔄 Streaming responses (real-time text generation)
    - 🧠 Domain-specific AI behavior
    - 📎 Database context injection
    - 💬 Multi-turn conversations
    - 🧹 Clear chat to start fresh
    """)

st.caption("Week 10 + Week 11 - AI Integration with OOP Architecture")