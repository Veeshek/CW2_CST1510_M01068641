"""
Authentication page for user login
Handles login/logout and session management
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.db import get_connection
from app.services.user_service import login, register_user

st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)

# Check if already logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# If user is already logged in, show logout option
if st.session_state.logged_in:
    st.title("Account")
    st.success(f"Logged in as: **{st.session_state.user_info['username']}**")
    st.write(f"Role: {st.session_state.user_info['role']}")
    
    st.write("")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Go to Dashboard", use_container_width=True):
            st.switch_page("main.py")
    
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()
    
    st.stop()

# Login form
st.title("🔐 Login")
st.write("")

# Create tabs for login and registration
tab1, tab2 = st.tabs(["Sign In", "Create Account"])

with tab1:
    st.write("### Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        submit_btn = st.form_submit_button("Login", use_container_width=True)
        
        if submit_btn:
            if not username or not password:
                st.error("Please fill in all fields")
            else:
                try:
                    conn = get_connection()
                    success, message, user_data = login(conn, username, password)
                    conn.close()
                    
                    if success:
                        # Login successful
                        st.session_state.logged_in = True
                        st.session_state.user_info = user_data
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    st.write("")
    st.info("""
    **Test Accounts:**
    - Username: admin, Password: admin123
    - Username: analyst, Password: analyst123
    - Username: user, Password: user123
    """)

with tab2:
    st.write("### Create a New Account")
    
    with st.form("register_form"):
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        user_role = st.selectbox("Select Role", ["user", "analyst", "admin"])
        
        register_btn = st.form_submit_button("Register", use_container_width=True)
        
        if register_btn:
            # Validation
            if not new_user or not new_pass:
                st.error("Please fill in all fields")
            elif new_pass != confirm_pass:
                st.error("Passwords don't match")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters")
            else:
                try:
                    conn = get_connection()
                    success, message = register_user(conn, new_user, new_pass, user_role)
                    conn.close()
                    
                    if success:
                        st.success(message)
                        st.info("You can now login using the Sign In tab")
                    else:
                        st.error(message)
                        
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")

st.write("")
st.write("---")
st.caption("CST1510 Coursework 2 - Multi-Domain Intelligence Platform")
