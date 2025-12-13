
"""
Cybersecurity Dashboard

Weeks covered:
- Week 9: multi-page dashboard + analytics + clean UI
- Week 10: AI integration (tab + separate AI page)

Key features:
- Auth guard (must be logged in)
- Filters + metrics + charts + export CSV
- Clean navigation topbar with AI button
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.db import connect_database
from app.ui import inject_global_css, topbar, auth_guard


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Global UI style
inject_global_css()

# Security: block page if not logged in
auth_guard()

# Show navigation bar
topbar("Dashboard")

st.title("🛡️ Cybersecurity Dashboard")
st.markdown("---")


# -----------------------------
# Load data from database (Week 8)
# -----------------------------
try:
    conn = connect_database()

    all_incidents_df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY timestamp",
        conn,
    )

    # -----------------------------
    # Filters (NOT sidebar)
    # -----------------------------
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

    # Apply filters
    filtered_df = all_incidents_df.copy()

    if selected_severity != "All":
        filtered_df = filtered_df[filtered_df["severity"] == selected_severity]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]

    # -----------------------------
    # Metrics (Week 9)
    # -----------------------------
    total = len(filtered_df)
    unresolved = len(filtered_df[filtered_df["status"] != "Resolved"])
    resolved = len(filtered_df[filtered_df["status"] == "Resolved"])

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total incidents", total)
    with m2:
        # delta is a small “bonus UI” to show change
        st.metric("Unresolved", unresolved, delta=unresolved - resolved)
    with m3:
        st.metric("Resolved", resolved)

    st.markdown("---")

    # -----------------------------
    # Tabs for analysis
    # -----------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📈 Phishing Analysis",
            "📊 Category Distribution",
            "⚠️ Severity Analysis",
            "📋 Incident Data",
            "🤖 AI (Go to Assistant)",
        ]
    )

    # TAB 1: Phishing trend
    with tab1:
        st.write("### Phishing Incident Trends Over Time")

        phishing_df = filtered_df[filtered_df["category"] == "Phishing"].copy()

        if len(phishing_df) > 0:
            # Convert timestamp safely (handles dirty data)
            phishing_df["timestamp_clean"] = pd.to_datetime(phishing_df["timestamp"], errors="coerce")
            phishing_df = phishing_df.dropna(subset=["timestamp_clean"])

            if len(phishing_df) > 0:
                phishing_df["month"] = phishing_df["timestamp_clean"].dt.to_period("M").astype(str)

                monthly_total = phishing_df.groupby("month").size().reset_index(name="total")
                monthly_unresolved = (
                    phishing_df[phishing_df["status"] != "Resolved"]
                    .groupby("month")
                    .size()
                    .reset_index(name="unresolved")
                )
                monthly_data = monthly_total.merge(monthly_unresolved, on="month", how="left").fillna(0)

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=monthly_data["month"],
                        y=monthly_data["total"],
                        mode="lines+markers",
                        name="Total Phishing",
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=monthly_data["month"],
                        y=monthly_data["unresolved"],
                        mode="lines+markers",
                        name="Unresolved",
                        line=dict(dash="dash"),
                    )
                )

                fig.update_layout(
                    title="Monthly Phishing Incidents (Total vs Unresolved)",
                    xaxis_title="Month",
                    yaxis_title="Number of Incidents",
                    height=420,
                    hovermode="x unified",
                )

                st.plotly_chart(fig, use_container_width=True)

                st.write("**Key Insights:**")
                max_month = monthly_data.loc[monthly_data["total"].idxmax()]
                st.write(f"- Peak month: **{max_month['month']}** with {int(max_month['total'])} incidents")
                st.write(f"- Total unresolved phishing incidents: **{int(monthly_data['unresolved'].sum())}**")
            else:
                st.info("No valid timestamp data available.")
        else:
            st.info("No phishing incidents found.")

    # TAB 2: category dist
    with tab2:
        st.write("### Incident Distribution by Category")

        if len(filtered_df) > 0:
            category_counts = filtered_df["category"].value_counts().reset_index()
            category_counts.columns = ["category", "count"]

            fig = px.pie(
                category_counts,
                values="count",
                names="category",
                title="Incidents by Category",
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(height=420)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available.")

    # TAB 3: severity analysis
    with tab3:
        st.write("### Incidents by Severity and Status")

        if len(filtered_df) > 0:
            severity_status = filtered_df.groupby(["severity", "status"]).size().reset_index(name="count")

            fig = px.bar(
                severity_status,
                x="severity",
                y="count",
                color="status",
                barmode="group",
                title="Incidents by Severity and Status",
            )
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available.")

    # TAB 4: table + export
    with tab4:
        st.write(f"### Incident Records ({len(filtered_df)} total)")

        if len(filtered_df) > 0:
            st.dataframe(
                filtered_df[["incident_id", "timestamp", "severity", "category", "status", "description"]],
                use_container_width=True,
                height=420,
            )

            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export to CSV",
                data=csv,
                file_name="cybersecurity_incidents.csv",
                mime="text/csv",
            )
        else:
            st.info("No incidents match the filters.")

    # TAB 5: AI navigation
    with tab5:
        st.write("### 🤖 AI Assistant")
        st.info("Open the AI Assistant page to run multi-domain chat + database context.")
        if st.button("Go to AI Assistant", type="primary", use_container_width=True):
            st.switch_page("pages/06_AI_Assistant.py")

    conn.close()

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    import traceback

    st.code(traceback.format_exc())
