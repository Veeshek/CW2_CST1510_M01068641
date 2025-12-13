"""
Manage Data - Week 9 MAX POINTS
- Auth guard + st.stop()
- RBAC: admin full CRUD, analyst read-only, user read-only
- Uses data-layer functions (no SQL in UI)
- Cache for fast loads + clear cache after writes
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.incidents import (
    get_all_incidents,
    insert_incident,
    update_incident_status,
    delete_incident
)
from app.data.datasets import (
    get_all_datasets,
    insert_dataset,
    update_dataset_size,
    delete_dataset
)
from app.data.tickets import (
    get_all_tickets,
    insert_ticket,
    update_ticket_status,
    delete_ticket
)

st.set_page_config(page_title="Manage Data", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")

# ---------------- CSS (hide streamlit sidebar + clean spacing) ----------------
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
section[data-testid="stSidebar"] {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}
header[data-testid="stHeader"] {display: none !important;}
.block-container {padding-top: 1.2rem !important; padding-bottom: 2.2rem !important;}

.badge{
    padding:7px 12px; border-radius:999px;
    border:1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.04);
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TOP BAR ----------------
def topbar(active: str):
    user = st.session_state.get("user_info", {"username": "User", "role": "user"})
    left, right = st.columns([7, 3])

    with left:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🛡️ Dashboard", use_container_width=True, type="primary" if active == "Dashboard" else "secondary"):
                st.switch_page("pages/02_Dashboard.py")
        with c2:
            if st.button("📊 Analytics", use_container_width=True, type="primary" if active == "Analytics" else "secondary"):
                st.switch_page("pages/03_Analytics.py")
        with c3:
            if st.button("📝 Manage", use_container_width=True, type="primary" if active == "Manage" else "secondary"):
                st.switch_page("pages/04_Manage_Data.py")
        with c4:
            if st.button("⚙️ Settings", use_container_width=True, type="primary" if active == "Settings" else "secondary"):
                st.switch_page("pages/05_Settings.py")

    with right:
        r1, r2 = st.columns([2, 1])
        with r1:
            st.markdown(f'<div class="badge">👤 {user["username"]} · {user["role"]}</div>', unsafe_allow_html=True)
        with r2:
            if st.button("🚪", help="Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_info = None
                st.switch_page("main.py")

# ---------------- AUTH GUARD (MAX POINTS: with st.stop) ----------------
if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.switch_page("pages/01_Login.py")
    st.stop()

user = st.session_state.user_info
role = user.get("role", "user")

# ---------------- RBAC ----------------
IS_ADMIN = role == "admin"
IS_ANALYST = role == "analyst"
IS_USER = role == "user"

CAN_CREATE = IS_ADMIN
CAN_UPDATE = IS_ADMIN
CAN_DELETE = IS_ADMIN

topbar("Manage")

st.title("📝 Manage Data (CRUD)")
st.caption("")
st.markdown("---")

# ---------------- CACHED LOADERS (Part 3 bonus) ----------------
@st.cache_data(show_spinner=False)
def load_incidents_df():
    rows = get_all_incidents()
    return pd.DataFrame(rows, columns=["incident_id", "timestamp", "severity", "category", "status", "description"])

@st.cache_data(show_spinner=False)
def load_datasets_df():
    rows = get_all_datasets()
    return pd.DataFrame(rows, columns=["dataset_id", "name", "rows", "columns", "uploaded_by", "upload_date"])

@st.cache_data(show_spinner=False)
def load_tickets_df():
    rows = get_all_tickets()
    return pd.DataFrame(rows, columns=["ticket_id", "priority", "description", "status", "assigned_to", "created_at", "resolution_time_hours"])

def clear_cache_and_rerun():
    st.cache_data.clear()
    st.rerun()

domain = st.radio(
    "**Select Domain:**",
    ["🛡️ Cybersecurity Incidents", "📊 Datasets", "🎫 IT Tickets"],
    horizontal=True
)

st.write("")

# ==========================================================
# 🛡️ INCIDENTS
# ==========================================================
if domain == "🛡️ Cybersecurity Incidents":
    st.subheader("🛡️ Cybersecurity Incidents")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Create", "✏️ Update", "🗑️ Delete"])

    with tab1:
        df = load_incidents_df()
        st.dataframe(df, use_container_width=True, height=420)

    with tab2:
        if not CAN_CREATE:
            st.info("🔒 Only **admin** can create incidents.")
        else:
            with st.form("create_incident"):
                c1, c2 = st.columns(2)
                with c1:
                    timestamp = st.text_input("Timestamp", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                    category = st.selectbox("Category", ["Phishing", "Malware", "DDoS", "Data Breach", "Unauthorized Access"])
                with c2:
                    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
                    description = st.text_area("Description")

                submit = st.form_submit_button("Create Incident", type="primary", use_container_width=True)
                if submit:
                    if not description.strip():
                        st.error("Description is required.")
                    else:
                        insert_incident(timestamp, severity, category, status, description)
                        st.success("✅ Incident created.")
                        clear_cache_and_rerun()

    with tab3:
        if not CAN_UPDATE:
            st.info("🔒 Only **admin** can update incidents.")
        else:
            df = load_incidents_df()
            if len(df) == 0:
                st.info("No incidents to update.")
            else:
                incident_id = st.selectbox("Select incident ID", df["incident_id"].tolist())
                new_status = st.selectbox("New status", ["Open", "In Progress", "Resolved"])
                if st.button("Update Incident", type="primary", use_container_width=True):
                    update_incident_status(int(incident_id), new_status)
                    st.success("✅ Incident updated.")
                    clear_cache_and_rerun()

    with tab4:
        if not CAN_DELETE:
            st.info("🔒 Only **admin** can delete incidents.")
        else:
            df = load_incidents_df()
            if len(df) == 0:
                st.info("No incidents to delete.")
            else:
                incident_id = st.selectbox("Select incident ID to delete", df["incident_id"].tolist())
                st.warning("This action cannot be undone.")
                if st.button("Confirm Delete", type="primary", use_container_width=True):
                    delete_incident(int(incident_id))
                    st.success("✅ Incident deleted.")
                    clear_cache_and_rerun()

# ==========================================================
# 📊 DATASETS
# ==========================================================
elif domain == "📊 Datasets":
    st.subheader("📊 Datasets")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Create", "✏️ Update", "🗑️ Delete"])

    with tab1:
        df = load_datasets_df()
        st.dataframe(df, use_container_width=True, height=420)

    with tab2:
        if not CAN_CREATE:
            st.info("🔒 Only **admin** can create datasets.")
        else:
            with st.form("create_dataset"):
                name = st.text_input("Dataset Name")
                rows = st.number_input("Rows", min_value=0, value=1000, step=100)
                cols = st.number_input("Columns", min_value=1, value=10, step=1)
                uploaded_by = st.text_input("Uploaded By", value=user["username"])
                upload_date = st.date_input("Upload Date", value=date.today())

                submit = st.form_submit_button("Create Dataset", type="primary", use_container_width=True)
                if submit:
                    if not name.strip():
                        st.error("Dataset name is required.")
                    else:
                        insert_dataset(name, int(rows), int(cols), uploaded_by, str(upload_date))
                        st.success("✅ Dataset created.")
                        clear_cache_and_rerun()

    with tab3:
        if not CAN_UPDATE:
            st.info("🔒 Only **admin** can update datasets.")
        else:
            df = load_datasets_df()
            if len(df) == 0:
                st.info("No datasets to update.")
            else:
                dataset_id = st.selectbox("Select dataset ID", df["dataset_id"].tolist())
                new_rows = st.number_input("New rows", min_value=0, value=1000, step=100)
                new_cols = st.number_input("New columns", min_value=1, value=10, step=1)
                if st.button("Update Dataset Size", type="primary", use_container_width=True):
                    update_dataset_size(int(dataset_id), int(new_rows), int(new_cols))
                    st.success("✅ Dataset updated.")
                    clear_cache_and_rerun()

    with tab4:
        if not CAN_DELETE:
            st.info("🔒 Only **admin** can delete datasets.")
        else:
            df = load_datasets_df()
            if len(df) == 0:
                st.info("No datasets to delete.")
            else:
                dataset_id = st.selectbox("Select dataset ID to delete", df["dataset_id"].tolist())
                st.warning("This action cannot be undone.")
                if st.button("Confirm Delete", type="primary", use_container_width=True):
                    delete_dataset(int(dataset_id))
                    st.success("✅ Dataset deleted.")
                    clear_cache_and_rerun()

# ==========================================================
# 🎫 TICKETS
# ==========================================================
else:
    st.subheader("🎫 IT Tickets")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Create", "✏️ Update", "🗑️ Delete"])

    with tab1:
        df = load_tickets_df()
        st.dataframe(df, use_container_width=True, height=420)

    with tab2:
        if not CAN_CREATE:
            st.info("🔒 Only **admin** can create tickets.")
        else:
            with st.form("create_ticket"):
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                description = st.text_area("Description")
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
                assigned_to = st.text_input("Assigned To", value="Unassigned")
                created_at = st.text_input("Created At", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                resolution_time_hours = st.number_input("Resolution Time (hours)", min_value=0.0, value=0.0, step=1.0)

                submit = st.form_submit_button("Create Ticket", type="primary", use_container_width=True)
                if submit:
                    if not description.strip():
                        st.error("Description is required.")
                    else:
                        insert_ticket(priority, description, status, assigned_to, created_at, float(resolution_time_hours))
                        st.success("✅ Ticket created.")
                        clear_cache_and_rerun()

    with tab3:
        if not CAN_UPDATE:
            st.info("🔒 Only **admin** can update tickets.")
        else:
            df = load_tickets_df()
            if len(df) == 0:
                st.info("No tickets to update.")
            else:
                ticket_id = st.selectbox("Select ticket ID", df["ticket_id"].tolist())
                new_status = st.selectbox("New status", ["Open", "In Progress", "Resolved"])
                if st.button("Update Ticket", type="primary", use_container_width=True):
                    update_ticket_status(int(ticket_id), new_status)
                    st.success("✅ Ticket updated.")
                    clear_cache_and_rerun()

    with tab4:
        if not CAN_DELETE:
            st.info("🔒 Only **admin** can delete tickets.")
        else:
            df = load_tickets_df()
            if len(df) == 0:
                st.info("No tickets to delete.")
            else:
                ticket_id = st.selectbox("Select ticket ID to delete", df["ticket_id"].tolist())
                st.warning("This action cannot be undone.")
                if st.button("Confirm Delete", type="primary", use_container_width=True):
                    delete_ticket(int(ticket_id))
                    st.success("✅ Ticket deleted.")
                    clear_cache_and_rerun()
