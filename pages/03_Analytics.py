
"""
Analytics (Week 9)

Features:
- Auth guard + st.stop()
- RBAC: only admin/analyst can access
- Data Science analytics + IT Ops analytics
- Uses same topbar style (includes AI button)
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.db import connect_database
from app.ui import inject_global_css, topbar, auth_guard

st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
auth_guard()

# RBAC (Week 9 max points)
role = st.session_state.user_info.get("role", "user")
if role not in ["admin", "analyst"]:
    st.error("⛔ You do not have permission to access Analytics.")
    st.stop()

topbar("Analytics")

st.title("📊 Analytics Center")
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
                # A simple measure of size: rows * columns
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
    st.error(f"Error: {e}")
    import traceback

    st.code(traceback.format_exc())
