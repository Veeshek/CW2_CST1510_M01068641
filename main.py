# main.py
"""
Main entry point (Week 9 polish).

Goal:
- If NOT logged in => redirect to Login automatically
- If logged in => redirect to Dashboard (main menu after login)
"""

import streamlit as st
import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent))

from app.ui import inject_global_css

st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply global CSS for the whole app
inject_global_css()

# Initialize session state (auth)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_info" not in st.session_state:
    st.session_state.user_info = None

# -------------------------------
# Redirect logic (important!)
# -------------------------------
# If not logged in: always go to Login page first
if not st.session_state.logged_in:
    st.switch_page("pages/01_Login.py")

# If logged in: send user to the main “menu” page (Dashboard)
st.switch_page("pages/02_Dashboard.py")
