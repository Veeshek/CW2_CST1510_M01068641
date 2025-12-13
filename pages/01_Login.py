
"""
Week 7 + Week 9 Login Page

What this page implements:
- Week 7 authentication (bcrypt password hashing)
- Week 7 lockout after failed attempts (stored in DATA/lockouts.txt)
- Week 7 session token logging (stored in DATA/sessions.txt)
- Week 9 UI polish + redirect to Dashboard after login

IMPORTANT:
- We do NOT show test accounts by default in "prod".
  If you want to show them for marking/demo, set SHOW_TEST_ACCOUNTS = True.
"""

import streamlit as st
import sys
from pathlib import Path
import os
import re
import bcrypt
from datetime import datetime, timedelta
import secrets

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.db import connect_database
from app.ui import inject_global_css

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_global_css()

# Toggle (for marking you can set True)
SHOW_TEST_ACCOUNTS = False

# -----------------------------
# Week 7 files (lockouts + sessions)
# -----------------------------
LOCKOUT_FILE = os.path.join("DATA", "lockouts.txt")
SESSION_FILE = os.path.join("DATA", "sessions.txt")


def ensure_file_exists(filepath: str) -> None:
    """Create the file + folder if missing (so app doesn't crash)."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        open(filepath, "a", encoding="utf-8").close()


def is_account_locked(username: str):
    """
    Week 7: Lockout check.

    Rule:
    - If >= 3 failed attempts, lock for 5 minutes.
    """
    ensure_file_exists(LOCKOUT_FILE)

    with open(LOCKOUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            parts = line.strip().split(",")
            if len(parts) < 3:
                continue

            stored_user, attempts_str, lockout_time = parts[0], parts[1], parts[2]

            if stored_user != username:
                continue

            try:
                attempts = int(attempts_str)
            except ValueError:
                continue

            if attempts >= 3:
                lockout_dt = datetime.fromisoformat(lockout_time)
                if datetime.now() < lockout_dt:
                    return True, lockout_dt

    return False, None


def record_failed_attempt(username: str) -> int:
    """
    Week 7: record failed login attempt.

    - Updates attempts count for that username
    - Refreshes lockout timer (5 minutes)
    """
    ensure_file_exists(LOCKOUT_FILE)

    # read existing lines
    with open(LOCKOUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    found = False
    new_lines = []
    attempts = 1
    lockout_time = (datetime.now() + timedelta(minutes=5)).isoformat()

    for line in lines:
        if not line.strip():
            continue

        parts = line.strip().split(",")
        if parts[0] == username:
            # update attempts for this user
            try:
                attempts = int(parts[1]) + 1
            except Exception:
                attempts = 1

            new_lines.append(f"{username},{attempts},{lockout_time}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{username},{attempts},{lockout_time}\n")

    with open(LOCKOUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return attempts


def reset_failed_attempts(username: str) -> None:
    """Clear lockout lines after successful login."""
    ensure_file_exists(LOCKOUT_FILE)

    with open(LOCKOUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(LOCKOUT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if not line.startswith(username + ","):
                f.write(line)


def create_session(username: str) -> str:
    """
    Week 7: Session token creation (stored in DATA/sessions.txt).
    """
    ensure_file_exists(SESSION_FILE)

    token = secrets.token_hex(16)
    timestamp = datetime.now().isoformat()

    with open(SESSION_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username},{token},{timestamp}\n")

    return token


def check_password_strength(password: str):
    """
    Week 7: password strength feedback.

    This doesn't block registration by itself,
    but it provides marking evidence (UX + security).
    """
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
    return "Strong", feedback


# -----------------------------
# Session state (auth)
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None


# -----------------------------
# If user already logged in => go to Dashboard
# -----------------------------
if st.session_state.logged_in:
    st.success("You are already logged in.")
    st.switch_page("pages/02_Dashboard.py")


# -----------------------------
# UI
# -----------------------------
st.title("🔐 Intelligence Platform")
st.caption("Secure login system (Week 7) + Multi-page app (Week 9/10)")
st.markdown("---")

tab1, tab2 = st.tabs(["**Sign In**", "**Create Account**"])

# -----------------------------
# SIGN IN
# -----------------------------
with tab1:
    st.write("### Login to your account")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("**Login**", type="primary", use_container_width=True)

        if submit:
            if not username or not password:
                st.error("⚠️ Please enter both fields.")
            else:
                # Lockout check (Week 7)
                locked, lockout_time = is_account_locked(username)
                if locked:
                    remaining = int((lockout_time - datetime.now()).total_seconds())
                    st.error(f"🔒 Account locked. Try again in {remaining//60}m {remaining%60}s.")
                else:
                    try:
                        conn = connect_database()
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT username, password_hash, role FROM users WHERE username = ?",
                            (username,),
                        )
                        row = cur.fetchone()
                        conn.close()

                        if row and bcrypt.checkpw(password.encode("utf-8"), row[1].encode("utf-8")):
                            # Success => reset lockouts + create session token
                            reset_failed_attempts(username)
                            _token = create_session(username)

                            # Save auth session state for Week 9
                            st.session_state.logged_in = True
                            st.session_state.user_info = {"username": row[0], "role": row[2]}

                            # Redirect to “main menu” (Dashboard)
                            st.switch_page("pages/02_Dashboard.py")
                        else:
                            attempts = record_failed_attempt(username)
                            if attempts >= 3:
                                st.error("🔒 Account locked for 5 minutes.")
                            else:
                                st.error(f"❌ Invalid credentials ({attempts}/3 attempts).")

                    except Exception as e:
                        st.error(f"❌ Error: {e}")

    # Optional: show test accounts (OFF by default)
    if SHOW_TEST_ACCOUNTS:
        with st.expander("📋 Test Accounts (demo only)"):
            st.code("admin / admin123\nanalyst / analyst123\nuser / user123")


# -----------------------------
# REGISTER
# -----------------------------
with tab2:
    st.write("### Create a new account")

    with st.form("register_form"):
        new_user = st.text_input("Username", placeholder="3-20 alphanumeric characters")
        new_pass = st.text_input("Password", type="password", placeholder="Min 6 chars, 1 letter + 1 number")

        # Password strength indicator (Week 7)
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

        register = st.form_submit_button("**Create Account**", type="primary", use_container_width=True)

        if register:
            errors = []

            # Username validation
            if not new_user:
                errors.append("Username is required")
            elif len(new_user) < 3:
                errors.append("Username must be at least 3 characters")
            elif len(new_user) > 20:
                errors.append("Username must be at most 20 characters")
            elif not new_user.isalnum():
                errors.append("Username must contain only letters and numbers")

            # Password validation
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
                for err in errors:
                    st.error(f"⚠️ {err}")
            else:
                try:
                    conn = connect_database()
                    cur = conn.cursor()

                    # Prevent duplicates
                    cur.execute("SELECT username FROM users WHERE username = ?", (new_user,))
                    if cur.fetchone():
                        st.error("❌ Username already exists.")
                    else:
                        hashed = bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                        cur.execute(
                            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                            (new_user, hashed, role),
                        )
                        conn.commit()
                        st.success("✅ Account created successfully!")
                        st.info("Now switch to **Sign In** tab to login.")

                    conn.close()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

st.markdown("---")
st.caption("Week 7: Secure Authentication | Week 9/10: Streamlit UI & Integration")
