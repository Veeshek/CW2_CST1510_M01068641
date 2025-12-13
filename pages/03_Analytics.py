"""
Analytics - Week 9 
- Single auth guard + st.stop()
- RBAC: only admin/analyst can access Analytics
- Clean topbar + logout
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.data.db import connect_database

st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
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

# ---------------- RBAC (max points) ----------------
role = st.session_state.user_info.get("role", "user")
if role not in ["admin", "analyst"]:
    st.error("⛔ You do not have permission to access Analytics.")
    st.stop()

topbar("Analytics")

st.title("📊 Analytics Center")
st.caption("")
st.markdown("---")

domain = st.radio("**Select Domain:**", ["📊 Data Science", "⚙️ IT Operations"], horizontal=True)
st.write("")

try:
    conn = connect_database()

    if domain == "📊 Data Science":
        st.write("## 📊 Data Science Analytics")
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)

        tab1, tab2, tab3 = st.tabs(["💾 Resources", "📁 Sources", "🗄️ Archiving"])

        with tab1:
            st.write("### Dataset Storage Analysis")
            if len(df) > 0:
                df["cells"] = df["rows"] * df["columns"]
                df = df.sort_values("cells", ascending=False)

                fig = px.bar(df.head(10), x="name", y="cells", title="Top 10 Datasets by Size")
                fig.update_layout(xaxis_tickangle=-45, height=420)
                st.plotly_chart(fig, use_container_width=True)

                largest = df.iloc[0]
                st.write("**Key Findings:**")
                st.write(f"- Largest: **{largest['name']}**")
                st.write(f"- Cells: **{largest['cells']:,.0f}** ({largest['rows']:,.0f} × {largest['columns']})")

                st.dataframe(df[["name", "rows", "columns", "cells"]].head(10), use_container_width=True)
            else:
                st.info("No datasets")

        with tab2:
            st.write("### Source Distribution")
            if len(df) > 0:
                by_source = df.groupby("uploaded_by").agg({"name": "count", "rows": "sum"}).reset_index()
                by_source.columns = ["source", "count", "total_rows"]

                fig1 = px.pie(by_source, values="count", names="source", title="Datasets by Source")
                st.plotly_chart(fig1, use_container_width=True)

                fig2 = px.bar(by_source, x="source", y="total_rows", title="Total Rows by Source")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No datasets")

        with tab3:
            st.write("### Archiving Candidates")
            threshold = st.slider("Row threshold:", 1000, 10000, 3000, 500)

            if len(df) > 0:
                candidates = df[df["rows"] >= threshold].sort_values("rows", ascending=False)
                st.write(f"**{len(candidates)}** datasets exceed {threshold:,} rows")

                if len(candidates) > 0:
                    st.dataframe(candidates[["name", "rows", "columns", "uploaded_by"]], use_container_width=True)
                else:
                    st.success(f"✅ No datasets exceed {threshold:,} rows")
            else:
                st.info("No datasets")

    else:
        st.write("## ⚙️ IT Operations Analytics")
        df = pd.read_sql_query("SELECT * FROM it_tickets", conn)

        tab1, tab2, tab3 = st.tabs(["👥 Staff Performance", "📊 Status", "🎯 Priority"])

        with tab1:
            st.write("### Staff Performance")
            if len(df) > 0:
                resolved = df[df["status"] == "Resolved"].copy()

                if len(resolved) > 0 and "resolution_time_hours" in resolved.columns:
                    staff_perf = resolved.groupby("assigned_to")["resolution_time_hours"].mean().reset_index()
                    staff_perf.columns = ["staff", "avg_hours"]
                    staff_perf = staff_perf.sort_values("avg_hours", ascending=False)

                    fig = px.bar(staff_perf, x="staff", y="avg_hours", title="Average Resolution Time by Staff")
                    st.plotly_chart(fig, use_container_width=True)

                    slowest = staff_perf.iloc[0]
                    fastest = staff_perf.iloc[-1]
                    avg = staff_perf["avg_hours"].mean()

                    st.write("**Analysis:**")
                    st.write(f"- Team avg: **{avg:.1f} hours**")
                    st.write(f"- Fastest: **{fastest['staff']}** ({fastest['avg_hours']:.1f}h)")
                    st.write(f"- Slowest: **{slowest['staff']}** ({slowest['avg_hours']:.1f}h)")
                else:
                    st.info("No resolved tickets / no resolution time data")
            else:
                st.info("No tickets")

        with tab2:
            st.write("### Status Distribution")
            if len(df) > 0:
                status_counts = df["status"].value_counts().reset_index()
                status_counts.columns = ["status", "count"]

                fig = px.pie(status_counts, values="count", names="status", title="Tickets by Status")
                st.plotly_chart(fig, use_container_width=True)

                resolved = df[df["status"] == "Resolved"]
                if len(resolved) > 0 and "resolution_time_hours" in resolved.columns:
                    avg = resolved["resolution_time_hours"].mean()
                    st.metric("Average Resolution Time", f"{avg:.1f} hours")
            else:
                st.info("No tickets")

        with tab3:
            st.write("### Priority Analysis")
            if len(df) > 0:
                priority_counts = df["priority"].value_counts().reset_index()
                priority_counts.columns = ["priority", "count"]

                fig = px.bar(priority_counts, x="priority", y="count", title="Tickets by Priority")
                st.plotly_chart(fig, use_container_width=True)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🔴 Critical", len(df[df["priority"] == "Critical"]))
                with col2:
                    st.metric("🟠 High", len(df[df["priority"] == "High"]))
                with col3:
                    st.metric("🟡 Medium", len(df[df["priority"] == "Medium"]))
                with col4:
                    st.metric("🟢 Low", len(df[df["priority"] == "Low"]))
            else:
                st.info("No tickets")

    conn.close()

except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
