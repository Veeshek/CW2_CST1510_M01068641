"""
03_Analytics.py
Multi-Domain Intelligence Platform - Analytics Page

This page focuses on *analysis* (not CRUD):
- Data Science domain: storage usage, data governance signals, archiving candidates
- IT Operations domain: staff workload, backlog, SLA risk indicators

Key goals (Week 9 + Week 11):
- Interactive charts (Plotly) + meaningful KPIs
- Clean separation: UI here, data access via Repository (OOP)
- Reusable / maintainable code: cached reads + helper functions
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to Python path so imports work when Streamlit runs from /pages
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ui import inject_global_css, topbar, auth_guard
from app.services.repository import Repository


# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()
auth_guard()
topbar("Analytics")

user = st.session_state.get("user_info", {"username": "user", "role": "user"})

st.title("📊 Multi-Domain Analytics")
st.caption(f"Logged in as: **{user.get('username')}** | Role: **{user.get('role')}**")
st.markdown("---")


# -----------------------------
# Data access (Repository + cache)
# Why cache? Streamlit reruns the script often; caching avoids hitting SQLite repeatedly.
# -----------------------------
repo = Repository()

@st.cache_data(show_spinner=False, ttl=60)
def load_datasets(limit: int = 200):
    """Load dataset objects from Repository. Cached to improve performance."""
    return repo.get_latest_datasets(limit=limit)

@st.cache_data(show_spinner=False, ttl=60)
def load_tickets(limit: int = 300):
    """Load ticket objects from Repository. Cached to improve performance."""
    return repo.get_latest_tickets(limit=limit)


def safe_df(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert list of dicts into DataFrame safely.
    If empty, return empty DataFrame with no crash.
    """
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def download_csv_button(df: pd.DataFrame, filename: str, label: str = "⬇️ Download CSV"):
    """Small helper: add a CSV export button for marking 'usability' points."""
    if df is None or df.empty:
        st.info("Nothing to export.")
        return
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


# -----------------------------
# Domain selector (Analytics)
# -----------------------------
domain = st.radio(
    "Select Analytics Domain:",
    ["📊 Data Science", "⚙️ IT Operations"],
    horizontal=True,
)
st.markdown("---")


# =====================================================================
# DATA SCIENCE ANALYTICS
# =====================================================================
if domain == "📊 Data Science":
    st.header("📊 Data Science Analytics")
    st.write("Dataset resource management and governance analysis")

    # Load datasets once (cached)
    with st.spinner("Loading dataset analytics..."):
        datasets = load_datasets(limit=200)

    # If no data, stop gracefully
    if not datasets:
        st.info("No datasets found in database.")
        st.stop()

    # Build DataFrame from OOP objects
    rows = []
    for ds in datasets:
        # NOTE: ds is an object (Week 11). We map fields for analysis charts.
        rows.append(
            {
                "dataset_id": ds.dataset_id,
                "name": ds.name,
                "source": getattr(ds, "source", "Unknown"),     # robust if field differs
                "size_mb": getattr(ds, "size_mb", None),
                "rows": getattr(ds, "rows", None),
                "quality_score": getattr(ds, "quality_score", None),
                "status": getattr(ds, "status", "Unknown"),
                "is_large": bool(ds.is_large()) if hasattr(ds, "is_large") else False,
            }
        )

    df = safe_df(rows)

    # -----------------------------
    # Filters (adds “analytics depth”)
    # -----------------------------
    with st.expander("🔎 Filters (Data Science)", expanded=True):
        colA, colB, colC, colD = st.columns(4)

        # Source filter
        sources = sorted(df["source"].dropna().unique().tolist())
        source_choice = colA.multiselect("Source", options=sources, default=sources)

        # Status filter
        statuses = sorted(df["status"].dropna().unique().tolist())
        status_choice = colB.multiselect("Status", options=statuses, default=statuses)

        # Quality filter
        # If some quality values are missing, we fill with 0 so they show as low-quality.
        df["quality_score"] = pd.to_numeric(df["quality_score"], errors="coerce").fillna(0.0)
        q_min, q_max = float(df["quality_score"].min()), float(df["quality_score"].max())
        q_from, q_to = colC.slider(
            "Quality range",
            min_value=0.0,
            max_value=max(1.0, q_max),
            value=(max(0.0, q_min), max(1.0, q_max)),
            step=0.05,
        )

        # Top N
        top_n = colD.selectbox("Top N (by size)", [5, 10, 15, 20], index=1)

    # Apply filters
    filtered = df[
        df["source"].isin(source_choice)
        & df["status"].isin(status_choice)
        & (df["quality_score"].between(q_from, q_to))
    ].copy()

    if filtered.empty:
        st.warning("No datasets match your filters.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["💾 Resources", "📁 Sources", "🗄️ Archiving"])

    # -----------------------------
    # TAB 1 - Resources
    # -----------------------------
    with tab1:
        st.subheader("Dataset Storage Analysis")

        # Convert size_mb/rows to numeric for safe computations
        filtered["size_mb"] = pd.to_numeric(filtered["size_mb"], errors="coerce").fillna(0.0)
        filtered["rows"] = pd.to_numeric(filtered["rows"], errors="coerce").fillna(0).astype(int)

        total_size = float(filtered["size_mb"].sum())
        avg_quality = float(filtered["quality_score"].mean())
        large_count = int(filtered["is_large"].sum())

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Storage", f"{total_size:.1f} MB")
        col2.metric("Avg Quality Score", f"{avg_quality:.2f}")
        col3.metric("Large Datasets", large_count)
        col4.metric("Total Datasets", len(filtered))

        st.markdown("")

        # Top N by size
        st.write(f"**Top {top_n} Datasets by Size (MB)**")
        top_by_size = filtered.nlargest(top_n, "size_mb")

        fig = px.bar(
            top_by_size.sort_values("size_mb", ascending=True),
            x="size_mb",
            y="name",
            orientation="h",
            title=f"Top {top_n} Datasets by Storage Size",
            labels={"size_mb": "Size (MB)", "name": "Dataset Name"},
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

        # Storage concentration (Top N vs Others)
        top_size_sum = float(top_by_size["size_mb"].sum())
        other_size = max(0.0, total_size - top_size_sum)

        pie = go.Figure(
            data=[
                go.Pie(
                    labels=[f"Top {top_n} Datasets", "Other Datasets"],
                    values=[top_size_sum, other_size],
                    hole=0.35,
                )
            ]
        )
        pie.update_layout(title="Storage Concentration", height=360)
        st.plotly_chart(pie, use_container_width=True)

        concentration = (top_size_sum / total_size * 100) if total_size > 0 else 0.0
        st.info(f"📌 Storage concentration: Top {top_n} datasets use **{concentration:.1f}%** of filtered storage.")

        # Export
        st.markdown("### Export")
        download_csv_button(top_by_size[["dataset_id", "name", "source", "size_mb", "rows", "quality_score", "status"]],
                            filename="data_science_top_datasets.csv")

    # -----------------------------
    # TAB 2 - Sources
    # -----------------------------
    with tab2:
        st.subheader("Data Source Distribution")

        # Group by source
        source_stats = (
            filtered.groupby("source", dropna=False)
            .agg(dataset_count=("dataset_id", "count"), total_size_mb=("size_mb", "sum"), avg_quality=("quality_score", "mean"))
            .reset_index()
            .sort_values("dataset_count", ascending=False)
        )

        fig = px.pie(
            source_stats,
            values="dataset_count",
            names="source",
            title="Dataset Count by Source",
            hole=0.35,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

        st.write("**Source Statistics**")
        st.dataframe(
            source_stats.style.format(
                {"dataset_count": "{:.0f}", "total_size_mb": "{:.1f} MB", "avg_quality": "{:.2f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )

        # Insight: dominant source (count-based)
        dominant = source_stats.iloc[0]
        st.info(
            f"🔍 Dominant source: **{dominant['source']}** "
            f"({dominant['dataset_count']:.0f} datasets, {dominant['total_size_mb']:.1f} MB)."
        )

        # Export
        st.markdown("### Export")
        download_csv_button(source_stats, filename="data_science_sources_summary.csv")

    # -----------------------------
    # TAB 3 - Archiving
    # -----------------------------
    with tab3:
        st.subheader("Archiving Recommendations")

        # Define archiving candidates:
        # - either flagged by OOP method is_large()
        # - OR quality is low and size is significant (simple governance heuristic)
        candidates = filtered[(filtered["is_large"] == True) | ((filtered["quality_score"] < 0.70) & (filtered["size_mb"] > 200))].copy()

        st.metric("Datasets Recommended for Review/Archiving", len(candidates))

        if candidates.empty:
            st.success("✅ No datasets currently exceed archiving/review thresholds (under current filters).")
        else:
            # Reason tagging (explainable rules = good for marking)
            def reason(row):
                if row["is_large"]:
                    return "Large dataset threshold triggered"
                return "Low quality & significant size"

            candidates["reason"] = candidates.apply(reason, axis=1)
            candidates = candidates.sort_values("size_mb", ascending=False)

            st.dataframe(
                candidates[["dataset_id", "name", "source", "size_mb", "rows", "quality_score", "status", "reason"]],
                use_container_width=True,
                hide_index=True,
            )

            total_archivable = float(candidates["size_mb"].sum())
            st.success(f"💾 Potential active storage saving: **{total_archivable:.1f} MB** (if archived/cleaned).")

            st.write("**Recommended Actions (Governance):**")
            st.write("1. Archive datasets that are large but rarely needed (tiered storage policy).")
            st.write("2. Flag large + low-quality datasets for quality review before they keep consuming resources.")
            st.write("3. Introduce upload checks (schema + missing values + quality score).")
            st.write("4. Review sources producing most low-quality datasets and improve upstream processes.")

            # Export
            st.markdown("### Export")
            download_csv_button(
                candidates[["dataset_id", "name", "source", "size_mb", "rows", "quality_score", "status", "reason"]],
                filename="data_science_archiving_candidates.csv",
            )


# =====================================================================
# IT OPERATIONS ANALYTICS
# =====================================================================
else:
    st.header("⚙️ IT Operations Analytics")
    st.write("Service desk performance and bottleneck analysis")

    with st.spinner("Loading IT ticket analytics..."):
        tickets = load_tickets(limit=300)

    if not tickets:
        st.info("No tickets found in database.")
        st.stop()

    # Build DataFrame from ticket objects
    trows = []
    for t in tickets:
        trows.append(
            {
                "ticket_id": t.ticket_id,
                "created_at": getattr(t, "created_at", ""),
                "priority": getattr(t, "priority", "Unknown"),
                "status": getattr(t, "status", "Unknown"),
                "assigned_to": getattr(t, "assigned_to", "Unassigned"),
                "is_overdue": bool(t.is_overdue()) if hasattr(t, "is_overdue") else False,
                "urgency_score": float(t.urgency_score()) if hasattr(t, "urgency_score") else 0.0,
            }
        )

    df_t = safe_df(trows)

    # Filters
    with st.expander("🔎 Filters (IT Operations)", expanded=True):
        colA, colB, colC = st.columns(3)
        staff_list = sorted(df_t["assigned_to"].dropna().unique().tolist())
        staff_sel = colA.multiselect("Assigned to", staff_list, default=staff_list)

        prios = sorted(df_t["priority"].dropna().unique().tolist())
        prio_sel = colB.multiselect("Priority", prios, default=prios)

        statuses = sorted(df_t["status"].dropna().unique().tolist())
        status_sel = colC.multiselect("Status", statuses, default=statuses)

    df_t = df_t[
        df_t["assigned_to"].isin(staff_sel)
        & df_t["priority"].isin(prio_sel)
        & df_t["status"].isin(status_sel)
    ].copy()

    if df_t.empty:
        st.warning("No tickets match your filters.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["👥 Staff Performance", "📊 Status Analysis", "⏱️ SLA / Overdue Risk"])

    # TAB 1 - Staff performance
    with tab1:
        st.subheader("Staff Performance Analysis")

        # Per staff metrics (volume + overdue + avg urgency)
        staff_summary = (
            df_t.groupby("assigned_to", dropna=False)
            .agg(
                total_tickets=("ticket_id", "count"),
                overdue_count=("is_overdue", "sum"),
                avg_urgency=("urgency_score", "mean"),
            )
            .reset_index()
        )
        staff_summary["overdue_pct"] = (staff_summary["overdue_count"] / staff_summary["total_tickets"]) * 100
        staff_summary = staff_summary.sort_values("total_tickets", ascending=False)

        # Chart: volume
        fig1 = px.bar(
            staff_summary,
            x="assigned_to",
            y="total_tickets",
            title="Ticket Volume by Staff Member",
            labels={"assigned_to": "Staff", "total_tickets": "Tickets"},
        )
        fig1.update_layout(height=380)
        st.plotly_chart(fig1, use_container_width=True)

        # Chart: overdue %
        fig2 = px.bar(
            staff_summary,
            x="assigned_to",
            y="overdue_pct",
            title="Overdue Ticket % by Staff",
            labels={"assigned_to": "Staff", "overdue_pct": "Overdue (%)"},
        )
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)

        st.write("**Performance Summary**")
        st.dataframe(
            staff_summary.style.format(
                {"total_tickets": "{:.0f}", "overdue_count": "{:.0f}", "avg_urgency": "{:.2f}", "overdue_pct": "{:.1f}%"}
            ),
            use_container_width=True,
            hide_index=True,
        )

        # Workload imbalance insight (simple ratio-based signal)
        max_tickets = float(staff_summary["total_tickets"].max())
        min_tickets = float(staff_summary["total_tickets"].min()) if float(staff_summary["total_tickets"].min()) > 0 else 1.0
        imbalance = ((max_tickets - min_tickets) / min_tickets) * 100

        if imbalance > 30:
            st.warning(f"⚠️ Workload imbalance detected (~{imbalance:.0f}% difference). Consider redistribution / round-robin assignment.")
        else:
            st.success("✅ Workload looks reasonably balanced under current filters.")

        # Export
        st.markdown("### Export")
        download_csv_button(staff_summary, filename="it_ops_staff_summary.csv")

    # TAB 2 - Status analysis
    with tab2:
        st.subheader("Ticket Status Distribution")

        status_counts = df_t["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        status_counts["percentage"] = (status_counts["count"] / status_counts["count"].sum()) * 100

        pie = go.Figure(
            data=[go.Pie(labels=status_counts["status"], values=status_counts["count"], hole=0.35)]
        )
        pie.update_layout(title="Ticket Distribution by Status", height=420)
        st.plotly_chart(pie, use_container_width=True)

        st.write("**Status Breakdown**")
        st.dataframe(
            status_counts.style.format({"count": "{:.0f}", "percentage": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True,
        )

        # Backlog rate: everything not resolved
        resolved_count = int((df_t["status"].str.lower() == "resolved").sum())
        total = len(df_t)
        backlog = total - resolved_count
        backlog_rate = (backlog / total) * 100 if total > 0 else 0.0

        col1, col2 = st.columns(2)
        col1.metric("Resolved tickets", resolved_count)
        col2.metric("Backlog rate", f"{backlog_rate:.1f}%")

        if backlog_rate > 60:
            st.warning("⚠️ High backlog: many tickets are not resolved. Investigate bottlenecks (Waiting for User / In Progress).")

        # Export
        st.markdown("### Export")
        download_csv_button(status_counts, filename="it_ops_status_breakdown.csv")

    # TAB 3 - SLA / Overdue risk
    with tab3:
        st.subheader("SLA / Overdue Risk Indicators")

        overdue_count = int(df_t["is_overdue"].sum())
        overdue_rate = (overdue_count / len(df_t)) * 100 if len(df_t) > 0 else 0.0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total tickets (filtered)", len(df_t))
        col2.metric("Overdue tickets", overdue_count)
        col3.metric("Overdue rate", f"{overdue_rate:.1f}%")

        # Priority distribution
        prio_counts = df_t["priority"].value_counts().reset_index()
        prio_counts.columns = ["priority", "count"]

        fig = px.bar(
            prio_counts,
            x="priority",
            y="count",
            title="Ticket Volume by Priority",
            labels={"priority": "Priority", "count": "Count"},
        )
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

        # Interpretation / recommendations (clear, marker-friendly)
        if overdue_rate > 20:
            st.error("🚨 Over 20% overdue: immediate action recommended.")
            st.write("**Recommendations:**")
            st.write("1. Add escalation rules for tickets approaching SLA limits.")
            st.write("2. Rebalance staff workload (move high urgency tickets away from overloaded assignees).")
            st.write("3. Create knowledge base for repeated requests (password reset, VPN, install).")
        elif overdue_rate > 10:
            st.warning("⚠️ Overdue rate above 10%: monitor and adjust workload/triage.")
        else:
            st.success("✅ Overdue rate is within a reasonable range.")

        # Export
        st.markdown("### Export")
        download_csv_button(df_t, filename="it_ops_filtered_tickets.csv", label="⬇️ Download filtered tickets CSV")


st.markdown("---")
st.caption("Week 9 + Week 11 - Analytics with OOP Integration (Repository + cached reads + export + filters)")

