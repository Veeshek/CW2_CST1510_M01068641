
"""
Settings - Account management (Week 9)

Features:
- Auth guard
- Change password (bcrypt)
- Show system statistics
- Same topbar style (includes AI button)
"""

import streamlit as st
import sys
from pathlib import Path
import bcrypt
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.db import connect_database
from app.ui import inject_global_css, topbar, auth_guard

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="centered", initial_sidebar_state="collapsed")

inject_global_css()
auth_guard()
topbar("Settings")

st.title("⚙️ Account Settings")
st.markdown("---")

# Account Info
st.write("### 👤 Account Information")
col1, col2 = st.columns(2)
with col1:
    st.write("**Username:**")
    st.code(st.session_state.user_info["username"])
with col2:
    st.write("**Role:**")
    st.code(st.session_state.user_info["role"])

st.markdown("---")

# Change Password
st.write("### 🔐 Change Password")

with st.form("change_password"):
    current = st.text_input("Current Password", type="password")
    new_pass = st.text_input("New Password", type="password", placeholder="Min 6 chars, 1 letter + 1 number")
    confirm = st.text_input("Confirm New Password", type="password")

    submit = st.form_submit_button("**Update Password**", type="primary", use_container_width=True)

    if submit:
        errors = []

        if not current or not new_pass or not confirm:
            errors.append("All fields required")

        if new_pass:
            if len(new_pass) < 6:
                errors.append("New password must be at least 6 characters")
            elif len(new_pass) > 50:
                errors.append("New password must be at most 50 characters")
            elif not re.search(r"[a-zA-Z]", new_pass):
                errors.append("New password must contain at least one letter")
            elif not re.search(r"[0-9]", new_pass):
                errors.append("New password must contain at least one number")

        if new_pass and confirm and new_pass != confirm:
            errors.append("New passwords do not match")

        if errors:
            for error in errors:
                st.error(f"⚠️ {error}")
        else:
            try:
                conn = connect_database()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_hash FROM users WHERE username = ?",
                    (st.session_state.user_info["username"],),
                )
                user_row = cursor.fetchone()

                if user_row and bcrypt.checkpw(current.encode("utf-8"), user_row[0].encode("utf-8")):
                    new_hash = bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt())
                    cursor.execute(
                        "UPDATE users SET password_hash = ? WHERE username = ?",
                        (new_hash.decode("utf-8"), st.session_state.user_info["username"]),
                    )
                    conn.commit()
                    st.success("✅ Password updated!")
                else:
                    st.error("❌ Current password incorrect")

                conn.close()
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown("---")

# Stats
st.write("### 📊 System Statistics")

try:
    conn = connect_database()
    cursor = conn.cursor()

    c1, c2, c3 = st.columns(3)
    with c1:
        cursor.execute("SELECT COUNT(*) FROM users")
        st.metric("Users", cursor.fetchone()[0])
    with c2:
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
        st.metric("Incidents", cursor.fetchone()[0])
    with c3:
        cursor.execute("SELECT COUNT(*) FROM it_tickets")
        st.metric("Tickets", cursor.fetchone()[0])

    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
