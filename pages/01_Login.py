"""
Login Page - Week 7 Authentication System
Full implementation: lockouts, sessions, password strength
"""

import streamlit as st
import sys
from pathlib import Path
import re
import bcrypt
from datetime import datetime, timedelta
import secrets
import os

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.data.db import connect_database

st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Global CSS
st.markdown("""
<style>
/* Hide Streamlit stuff */
[data-testid="stSidebarNav"] {display: none !important;}
section[data-testid="stSidebar"] {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}
header[data-testid="stHeader"] {display: none !important;}   /* ✅ IMPORTANT: hides the top header space */

/* Clean spacing */
.block-container {padding-top: 1.2rem !important; padding-bottom: 2.2rem !important;}
</style>
""", unsafe_allow_html=True)


LOCKOUT_FILE = "DATA/lockouts.txt"
SESSION_FILE = "DATA/sessions.txt"


def ensure_file_exists(filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        open(filepath, "a").close()


def is_account_locked(username: str):
    """Week 7 Challenge 3"""
    ensure_file_exists(LOCKOUT_FILE)

    with open(LOCKOUT_FILE, "r") as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    stored_user, attempts, lockout_time = parts[0], int(parts[1]), parts[2]
                    if stored_user == username and attempts >= 3:
                        lockout_dt = datetime.fromisoformat(lockout_time)
                        if datetime.now() < lockout_dt:
                            return True, lockout_dt
    return False, None


def record_failed_attempt(username: str) -> int:
    """Week 7 Challenge 3"""
    ensure_file_exists(LOCKOUT_FILE)

    attempts = 1
    with open(LOCKOUT_FILE, "r") as f:
        lines = f.readlines()

    found = False
    new_lines = []
    for line in lines:
        if line.strip():
            parts = line.strip().split(",")
            if parts[0] == username:
                attempts = int(parts[1]) + 1
                lockout_time = (datetime.now() + timedelta(minutes=5)).isoformat()
                new_lines.append(f"{username},{attempts},{lockout_time}\n")
                found = True
            else:
                new_lines.append(line)

    if not found:
        lockout_time = (datetime.now() + timedelta(minutes=5)).isoformat()
        new_lines.append(f"{username},{attempts},{lockout_time}\n")

    with open(LOCKOUT_FILE, "w") as f:
        f.writelines(new_lines)

    return attempts


def reset_failed_attempts(username: str) -> None:
    ensure_file_exists(LOCKOUT_FILE)
    with open(LOCKOUT_FILE, "r") as f:
        lines = f.readlines()
    with open(LOCKOUT_FILE, "w") as f:
        for line in lines:
            if not line.startswith(username + ","):
                f.write(line)


def create_session(username: str) -> str:
    """Week 7 Challenge 4"""
    ensure_file_exists(SESSION_FILE)

    token = secrets.token_hex(16)
    timestamp = datetime.now().isoformat()

    with open(SESSION_FILE, "a") as f:
        f.write(f"{username},{token},{timestamp}\n")

    return token


def check_password_strength(password: str):
    """Week 7 Challenge 1"""
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add lowercase letters")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add uppercase letters")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        feedback.append("Add numbers")

    if re.search(r"[!@#$%^&*()]", password):
        score += 1

    if score <= 2:
        return "Weak", feedback
    elif score <= 3:
        return "Medium", feedback
    else:
        return "Strong", feedback


# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None


# If already logged in
if st.session_state.logged_in:
    st.success(f"✅ Logged in as **{st.session_state.user_info['username']}** ({st.session_state.user_info['role']})")
    if st.button("➡️ Go to Dashboard", use_container_width=True, type="primary"):
        st.switch_page("main.py")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.switch_page("main.py")
    st.stop()


st.title("🔐 Intelligence Platform")
st.caption("")
st.markdown("---")

tab1, tab2 = st.tabs(["**Sign In**", "**Create Account**"])


with tab1:
    st.write("### Login to your account")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("**Login**", use_container_width=True, type="primary")

        if submit:
            if not username or not password:
                st.error("⚠️ Please enter both fields")
            else:
                locked, lockout_time = is_account_locked(username)
                if locked:
                    remaining = (lockout_time - datetime.now()).seconds
                    st.error(f"🔒 Account locked. Try again in {remaining//60}m {remaining%60}s")
                else:
                    try:
                        conn = connect_database()
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT username, password_hash, role FROM users WHERE username = ?",
                            (username,),
                        )
                        user = cursor.fetchone()

                        if user and bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8")):
                            reset_failed_attempts(username)
                            token = create_session(username)

                            st.session_state.logged_in = True
                            st.session_state.user_info = {"username": user[0], "role": user[2]}

                            st.success("✅ Login successful!")
                            st.info(f"Session token: {token[:16]}...")
                            conn.close()

                            st.switch_page("main.py")
                        else:
                            attempts = record_failed_attempt(username)
                            if attempts >= 3:
                                st.error("🔒 Account locked for 5 minutes")
                            else:
                                st.error(f"❌ Invalid credentials ({attempts}/3 attempts)")

                        conn.close()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    with st.expander("📋 Test Accounts"):
        st.code("admin -> James1234/ James123")


with tab2:
    st.write("### Create a new account")

    with st.form("register_form"):
        new_user = st.text_input("Username", placeholder="3-20 alphanumeric characters")
        new_pass = st.text_input("Password", type="password", placeholder="Min 6 chars, 1 letter + 1 number")

        if new_pass:
            strength, feedback = check_password_strength(new_pass)
            if strength == "Weak":
                st.warning(f"Password strength: **{strength}**")
            elif strength == "Medium":
                st.info(f"Password strength: **{strength}**")
            else:
                st.success(f"Password strength: **{strength}**")

            if feedback:
                with st.expander("💡 Recommendations"):
                    for tip in feedback:
                        st.write(f"- {tip}")

        confirm_pass = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["user", "analyst", "admin"])
        register = st.form_submit_button("**Create Account**", use_container_width=True, type="primary")

        if register:
            errors = []

            if not new_user:
                errors.append("Username is required")
            elif len(new_user) < 3:
                errors.append("Username must be at least 3 characters")
            elif len(new_user) > 20:
                errors.append("Username must be at most 20 characters")
            elif not new_user.isalnum():
                errors.append("Username must contain only letters and numbers")

            if not new_pass:
                errors.append("Password is required")
            elif len(new_pass) < 6:
                errors.append("Password must be at least 6 characters")
            elif len(new_pass) > 50:
                errors.append("Password must be at most 50 characters")
            elif not re.search(r"[a-zA-Z]", new_pass):
                errors.append("Password must contain at least one letter")
            elif not re.search(r"[0-9]", new_pass):
                errors.append("Password must contain at least one number")

            if new_pass and confirm_pass and new_pass != confirm_pass:
                errors.append("Passwords do not match")

            if errors:
                for error in errors:
                    st.error(f"⚠️ {error}")
            else:
                try:
                    conn = connect_database()
                    cursor = conn.cursor()
                    cursor.execute("SELECT username FROM users WHERE username = ?", (new_user,))
                    if cursor.fetchone():
                        st.error("❌ Username already exists")
                    else:
                        hashed = bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt())
                        cursor.execute(
                            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                            (new_user, hashed.decode("utf-8"), role),
                        )
                        conn.commit()
                        st.success("✅ Account created!")
                        st.info("➡️ Switch to **Sign In** tab to login")
                    conn.close()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.caption("CST1510 Coursework 2")
