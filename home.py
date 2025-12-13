"""
Home - Multi-Domain Intelligence Platform
Renamed to Home.py to appear as "Home" in sidebar
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# Redirect to login if not logged in
if not st.session_state.logged_in:
    st.switch_page("pages/01_Login.py")
    st.stop()

# Main page content for logged in users
user = st.session_state.user_info

st.title(f"🏠 Welcome, {user['username']}!")
st.caption(f"Role: **{user['role'].title()}**")
st.markdown("---")

st.write("### 📊 System Overview")
st.write("")

try:
    from app.data.db import connect_database
    conn = connect_database()
    cursor = conn.cursor()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
        st.metric("🛡️ Security Incidents", cursor.fetchone()[0])
    
    with col2:
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents WHERE status != 'Resolved'")
        st.metric("⚠️ Active Incidents", cursor.fetchone()[0])
    
    with col3:
        cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
        st.metric("📁 Datasets", cursor.fetchone()[0])
    
    with col4:
        cursor.execute("SELECT COUNT(*) FROM it_tickets")
        st.metric("🎫 IT Tickets", cursor.fetchone()[0])
    
    conn.close()
    
except Exception as e:
    st.error(f"Error loading metrics: {str(e)}")

st.write("")
st.markdown("---")

st.write("### 🚀 Quick Access")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🛡️ Cybersecurity Dashboard")
    st.write("View security incidents and analyze threat patterns")
    if st.button("Open Dashboard", key="dash", use_container_width=True):
        st.switch_page("pages/02_Dashboard.py")

with col2:
    st.markdown("#### 📊 Analytics Center")
    st.write("Explore data science and IT operations metrics")
    if st.button("Open Analytics", key="analytics", use_container_width=True):
        st.switch_page("pages/03_Analytics.py")

with col3:
    st.markdown("#### 📝 Manage Data")
    st.write("Create, update, and delete records (CRUD)")
    if st.button("Open CRUD Panel", key="crud", use_container_width=True):
        st.switch_page("pages/04_Manage_Data.py")

st.write("")
st.markdown("---")
st.caption("CST1510 Coursework 2 - Multi-Domain Intelligence Platform")
