"""
Cybersecurity Dashboard - Week 9
- Single auth guard + st.stop()
- Clean topbar + logout
- Filters moved to expander (sidebar hidden)
- Adds st.metric(delta=...) bonus
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.data.db import connect_database

st.set_page_config(
    page_title="Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CSS ----------------
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

# ---------------- TOPBAR ----------------
def topbar(active: str):
    user = st.session_state.get("user_info", {"username": "User", "role": "user"})
    left, right = st.columns([7, 3])

    with left:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🛡️ Dashboard", use_container_width=True,
                        type="primary" if active == "Dashboard" else "secondary"):
                st.switch_page("pages/02_Dashboard.py")
        with c2:
            if st.button("📊 Analytics", use_container_width=True,
                        type="primary" if active == "Analytics" else "secondary"):
                st.switch_page("pages/03_Analytics.py")
        with c3:
            if st.button("📝 Manage", use_container_width=True,
                        type="primary" if active == "Manage" else "secondary"):
                st.switch_page("pages/04_Manage_Data.py")
        with c4:
            if st.button("⚙️ Settings", use_container_width=True,
                        type="primary" if active == "Settings" else "secondary"):
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

# ---------------- AUTH GUARD (single + stop) ----------------
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please login first")
    st.switch_page("pages/01_Login.py")
    st.stop()

topbar("Dashboard")

st.title("🛡️ Cybersecurity Dashboard")
st.caption("")
st.markdown("---")

try:
    conn = connect_database()

    # Load all incidents
    all_incidents_df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY timestamp",
        conn
    )

    # Filters moved here (sidebar hidden)
    with st.expander("🔍 Filters", expanded=True):
        f1, f2, f3 = st.columns(3)
        severity_options = ["All"] + sorted(all_incidents_df["severity"].dropna().unique().tolist())
        category_options = ["All"] + sorted(all_incidents_df["category"].dropna().unique().tolist())
        status_options = ["All"] + sorted(all_incidents_df["status"].dropna().unique().tolist())

        with f1:
            selected_severity = st.selectbox("Severity", severity_options)
        with f2:
            selected_category = st.selectbox("Category", category_options)
        with f3:
            selected_status = st.selectbox("Status", status_options)

    filtered_df = all_incidents_df.copy()
    if selected_severity != "All":
        filtered_df = filtered_df[filtered_df["severity"] == selected_severity]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]

    # ---------------- Metrics (bonus: delta) ----------------
    total = len(filtered_df)
    unresolved = len(filtered_df[filtered_df["status"] != "Resolved"])
    resolved = len(filtered_df[filtered_df["status"] == "Resolved"])

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total incidents", total)
    with m2:
        st.metric("Unresolved", unresolved, delta=unresolved - resolved)  # ✅ delta bonus
    with m3:
        st.metric("Resolved", resolved)

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Phishing Analysis",
        "📊 Category Distribution",
        "⚠️ Severity Analysis",
        "📋 Incident Data"
    ])

    # --- TAB 1 ---
    with tab1:
        st.write("### Phishing Incident Trends Over Time")

        phishing_df = filtered_df[filtered_df["category"] == "Phishing"].copy()

        if len(phishing_df) > 0:
            phishing_df["timestamp_clean"] = pd.to_datetime(phishing_df["timestamp"], errors="coerce")
            phishing_df = phishing_df.dropna(subset=["timestamp_clean"])

            if len(phishing_df) > 0:
                phishing_df["month"] = phishing_df["timestamp_clean"].dt.to_period("M").astype(str)

                monthly_total = phishing_df.groupby("month").size().reset_index(name="total")
                monthly_unresolved = phishing_df[phishing_df["status"] != "Resolved"].groupby("month").size().reset_index(name="unresolved")
                monthly_data = monthly_total.merge(monthly_unresolved, on="month", how="left").fillna(0)

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=monthly_data["month"], y=monthly_data["total"],
                    mode="lines+markers", name="Total Phishing"
                ))
                fig.add_trace(go.Scatter(
                    x=monthly_data["month"], y=monthly_data["unresolved"],
                    mode="lines+markers", name="Unresolved", line=dict(dash="dash")
                ))
                fig.update_layout(
                    title="Monthly Phishing Incidents (Total vs Unresolved)",
                    xaxis_title="Month",
                    yaxis_title="Number of Incidents",
                    height=420,
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.write("**Key Insights:**")
                max_month = monthly_data.loc[monthly_data["total"].idxmax()]
                st.write(f"- Peak month: **{max_month['month']}** with {int(max_month['total'])} incidents")
                st.write(f"- Current unresolved: **{int(monthly_data['unresolved'].sum())}** phishing incidents")
            else:
                st.info("No valid timestamp data for phishing incidents")
        else:
            st.info("No phishing incidents found with current filters")

    # --- TAB 2 ---
    with tab2:
        st.write("### Incident Distribution by Category")
        if len(filtered_df) > 0:
            category_counts = filtered_df["category"].value_counts().reset_index()
            category_counts.columns = ["category", "count"]

            fig = px.pie(category_counts, values="count", names="category", title="Incidents by Category")
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

            st.write("### Resolution Bottleneck by Category")
            category_status = filtered_df.groupby(["category", "status"]).size().reset_index(name="count")
            unresolved_df = category_status[category_status["status"] != "Resolved"].groupby("category")["count"].sum().reset_index()
            total_df = category_status.groupby("category")["count"].sum().reset_index()

            bottleneck = total_df.merge(unresolved_df, on="category", how="left", suffixes=("_total", "_unresolved")).fillna(0)
            bottleneck["unresolved_pct"] = (bottleneck["count_unresolved"] / bottleneck["count_total"] * 100).round(1)
            bottleneck = bottleneck.sort_values("unresolved_pct", ascending=False)

            fig2 = px.bar(
                bottleneck, x="category", y="unresolved_pct",
                title="Unresolved Incident Percentage by Category",
                labels={"unresolved_pct": "Unresolved %", "category": "Category"},
            )
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data to display with current filters")

    # --- TAB 3 ---
    with tab3:
        st.write("### Incidents by Severity and Status")
        if len(filtered_df) > 0:
            severity_status = filtered_df.groupby(["severity", "status"]).size().reset_index(name="count")

            fig = px.bar(
                severity_status, x="severity", y="count", color="status",
                barmode="group",
                title="Incidents by Severity and Status",
                labels={"count": "Number of Incidents", "severity": "Severity"},
            )
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("🔴 Critical", len(filtered_df[filtered_df["severity"] == "Critical"]))
            with c2:
                st.metric("🟠 High", len(filtered_df[filtered_df["severity"] == "High"]))
            with c3:
                st.metric("🟡 Medium", len(filtered_df[filtered_df["severity"] == "Medium"]))
        else:
            st.info("No data to display with current filters")

    # --- TAB 4 ---
    with tab4:
        st.write(f"### Incident Records ({len(filtered_df)} total)")
        if len(filtered_df) > 0:
            st.dataframe(
                filtered_df[["incident_id", "timestamp", "severity", "category", "status", "description"]],
                use_container_width=True,
                height=420
            )
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export to CSV",
                data=csv,
                file_name="cybersecurity_incidents.csv",
                mime="text/csv"
            )
        else:
            st.info("No incidents match the current filters")

    conn.close()

except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
