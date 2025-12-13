"""
Main router - Multi-Domain Intelligence Platform
Login direct + sidebar Streamlit hidden
"""
import streamlit as st

st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Global CSS (hide multipage sidebar + hamburger + reduce padding)
st.markdown("""
<style>
/* Hide multipage navigation */
[data-testid="stSidebarNav"] {display: none !important;}

/* Hide entire sidebar */
section[data-testid="stSidebar"] {display: none !important;}

/* Hide the hamburger / collapsed control */
[data-testid="collapsedControl"] {display: none !important;}

/* Reduce top padding */
.block-container {padding-top: 1.6rem !important; padding-bottom: 2.2rem !important;}
</style>
""", unsafe_allow_html=True)

# Ensure session state keys exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# Route user
if not st.session_state.logged_in:
    st.switch_page("pages/01_Login.py")
else:
    st.switch_page("pages/02_Dashboard.py")
