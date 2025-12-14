"""
Analytics Page - Data Science and IT Operations Domains

This page provides comprehensive analytics for:
- Data Science: Dataset resource management and governance
- IT Operations: Service desk performance and bottleneck analysis

Week 9: Interactive Streamlit visualizations
Week 11: OOP integration with Repository pattern
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ui import inject_global_css, topbar, auth_guard
from app.services.repository import Repository

# Page configuration
st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply styling and authentication
inject_global_css()
auth_guard()
topbar("Analytics")

# Get user info
user = st.session_state.get("user_info", {"username": "user", "role": "user"})

# Page header
st.title("📊 Multi-Domain Analytics")
st.caption(f"Logged in as: **{user.get('username')}** | Role: **{user.get('role')}**")
st.markdown("---")

# Domain selector
domain = st.radio(
    "Select Analytics Domain:",
    ["📊 Data Science", "⚙️ IT Operations"],
    horizontal=True,
)

st.markdown("---")

# Create repository instance
repo = Repository()

# ============================================
# DATA SCIENCE DOMAIN
# ============================================
if domain == "📊 Data Science":
    st.header("📊 Data Science Analytics")
    st.write("Dataset resource management and governance analysis")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["💾 Resources", "📁 Sources", "🗄️ Archiving"])
    
    # TAB 1: RESOURCE ANALYSIS
    with tab1:
        st.subheader("Dataset Storage Analysis")
        
        try:
            # Get datasets
            datasets = repo.get_latest_datasets(limit=100)
            
            if datasets:
                # Convert to dataframe for analysis
                df_data = []
                for ds in datasets:
                    df_data.append({
                        'dataset_id': ds.dataset_id,
                        'name': ds.name,
                        'source': ds.source,
                        'size_mb': ds.size_mb,
                        'rows': ds.rows,
                        'cells': ds.rows * 10,  # Estimate cells (simplified)
                        'quality_score': ds.quality_score,
                        'status': ds.status
                    })
                
                df = pd.DataFrame(df_data)
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_size = df['size_mb'].sum()
                    st.metric("Total Storage", f"{total_size:.1f} MB")
                
                with col2:
                    avg_quality = df['quality_score'].mean()
                    st.metric("Avg Quality Score", f"{avg_quality:.2f}")
                
                with col3:
                    large_datasets = sum(1 for ds in datasets if ds.is_large())
                    st.metric("Large Datasets", large_datasets)
                
                st.write("")
                
                # Top 10 by size
                st.write("**Top 10 Datasets by Size (MB)**")
                
                top_10 = df.nlargest(10, 'size_mb')
                
                fig = px.bar(
                    top_10,
                    x='size_mb',
                    y='name',
                    orientation='h',
                    title='Top 10 Datasets by Storage Size',
                    labels={'size_mb': 'Size (MB)', 'name': 'Dataset Name'},
                    color='size_mb',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Storage breakdown
                st.write("**Storage Distribution**")
                
                top_10_size = top_10['size_mb'].sum()
                other_size = total_size - top_10_size
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Top 10 Datasets', 'Other Datasets'],
                    values=[top_10_size, other_size],
                    hole=0.3
                )])
                
                fig_pie.update_layout(
                    title="Storage Concentration",
                    height=350
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
                
                st.info(f"📊 Top 10 datasets consume **{(top_10_size/total_size)*100:.1f}%** of total storage")
                
            else:
                st.info("No datasets found in database")
                
        except Exception as e:
            st.error(f"Error loading dataset analytics: {str(e)}")
    
    # TAB 2: SOURCE ANALYSIS
    with tab2:
        st.subheader("Data Source Distribution")
        
        try:
            datasets = repo.get_latest_datasets(limit=100)
            
            if datasets:
                # Group by source
                df_data = [{'source': ds.source, 'size_mb': ds.size_mb} for ds in datasets]
                df = pd.DataFrame(df_data)
                
                source_stats = df.groupby('source').agg({
                    'size_mb': ['sum', 'count']
                }).reset_index()
                
                source_stats.columns = ['source', 'total_size_mb', 'dataset_count']
                
                # Source distribution chart
                fig = px.pie(
                    source_stats,
                    values='dataset_count',
                    names='source',
                    title='Dataset Count by Source',
                    hole=0.3
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Source table
                st.write("**Source Statistics**")
                
                source_stats['avg_size_mb'] = source_stats['total_size_mb'] / source_stats['dataset_count']
                source_stats = source_stats.sort_values('total_size_mb', ascending=False)
                
                st.dataframe(
                    source_stats.style.format({
                        'total_size_mb': '{:.1f} MB',
                        'dataset_count': '{:.0f}',
                        'avg_size_mb': '{:.1f} MB'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Insights
                dominant_source = source_stats.iloc[0]
                st.info(f"🔍 **{dominant_source['source']}** is the dominant source with {dominant_source['dataset_count']:.0f} datasets ({dominant_source['total_size_mb']:.1f} MB)")
                
            else:
                st.info("No datasets found")
                
        except Exception as e:
            st.error(f"Error loading source analytics: {str(e)}")
    
    # TAB 3: ARCHIVING RECOMMENDATIONS
    with tab3:
        st.subheader("Archiving Recommendations")
        
        try:
            datasets = repo.get_latest_datasets(limit=100)
            
            if datasets:
                # Find datasets that need archiving
                archiving_candidates = [ds for ds in datasets if ds.is_large()]
                
                st.metric("Datasets Recommended for Archiving", len(archiving_candidates))
                
                if archiving_candidates:
                    # Create table
                    archive_data = []
                    for ds in archiving_candidates:
                        archive_data.append({
                            'Dataset': ds.name,
                            'Size (MB)': ds.size_mb,
                            'Rows': f"{ds.rows:,}",
                            'Source': ds.source,
                            'Quality': f"{ds.quality_score:.2f}",
                            'Reason': 'Size > 500 MB' if ds.size_mb > 500 else 'Rows > 1M'
                        })
                    
                    df_archive = pd.DataFrame(archive_data)
                    
                    st.dataframe(df_archive, use_container_width=True, hide_index=True)
                    
                    # Calculate savings
                    total_archivable = sum(ds.size_mb for ds in archiving_candidates)
                    
                    st.success(f"💾 Archiving these datasets would free up **{total_archivable:.1f} MB** from active storage")
                    
                    # Recommendations
                    st.write("**Recommended Actions:**")
                    st.write("1. Move datasets > 500 MB to archive tier storage")
                    st.write("2. Implement tiered storage: Active (SSD) → Archive (HDD) → Cold (Cloud)")
                    st.write("3. Set up automated archiving policies based on age and access patterns")
                    st.write("4. Review quality scores - low quality large datasets should be validated or deleted")
                    
                else:
                    st.success("✅ No datasets currently exceed archiving thresholds")
                    
            else:
                st.info("No datasets found")
                
        except Exception as e:
            st.error(f"Error loading archiving recommendations: {str(e)}")

# ============================================
# IT OPERATIONS DOMAIN  
# ============================================
else:  # IT Operations
    st.header("⚙️ IT Operations Analytics")
    st.write("Service desk performance and bottleneck analysis")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["👥 Staff Performance", "📊 Status Analysis", "⏱️ Resolution Times"])
    
    # TAB 1: STAFF PERFORMANCE
    with tab1:
        st.subheader("Staff Performance Analysis")
        
        try:
            tickets = repo.get_latest_tickets(limit=200)
            
            if tickets:
                # Calculate per-staff metrics
                staff_metrics = {}
                
                for ticket in tickets:
                    staff = ticket.assigned_to
                    
                    if staff not in staff_metrics:
                        staff_metrics[staff] = {
                            'tickets': 0,
                            'urgency_total': 0,
                            'overdue': 0
                        }
                    
                    staff_metrics[staff]['tickets'] += 1
                    staff_metrics[staff]['urgency_total'] += ticket.urgency_score()
                    
                    if ticket.is_overdue():
                        staff_metrics[staff]['overdue'] += 1
                
                # Create dataframe
                staff_data = []
                for staff, metrics in staff_metrics.items():
                    staff_data.append({
                        'Staff Member': staff,
                        'Total Tickets': metrics['tickets'],
                        'Avg Urgency': metrics['urgency_total'] / metrics['tickets'],
                        'Overdue Count': metrics['overdue'],
                        'Overdue %': (metrics['overdue'] / metrics['tickets']) * 100
                    })
                
                df_staff = pd.DataFrame(staff_data).sort_values('Total Tickets', ascending=False)
                
                # Chart: Tickets per staff
                fig = px.bar(
                    df_staff,
                    x='Staff Member',
                    y='Total Tickets',
                    title='Ticket Volume by Staff Member',
                    color='Total Tickets',
                    color_continuous_scale='Viridis'
                )
                
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Chart: Overdue rates
                fig2 = px.bar(
                    df_staff,
                    x='Staff Member',
                    y='Overdue %',
                    title='Overdue Ticket Percentage by Staff',
                    color='Overdue %',
                    color_continuous_scale='Reds'
                )
                
                fig2.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)
                
                # Staff table
                st.write("**Performance Metrics**")
                st.dataframe(
                    df_staff.style.format({
                        'Total Tickets': '{:.0f}',
                        'Avg Urgency': '{:.1f}',
                        'Overdue Count': '{:.0f}',
                        'Overdue %': '{:.1f}%'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Workload analysis
                max_tickets = df_staff['Total Tickets'].max()
                min_tickets = df_staff['Total Tickets'].min()
                imbalance = ((max_tickets - min_tickets) / min_tickets) * 100
                
                if imbalance > 30:
                    st.warning(f"⚠️ Workload imbalance detected: {imbalance:.0f}% difference between highest and lowest workload")
                    st.write("**Recommendation:** Redistribute tickets to balance workload")
                else:
                    st.success("✅ Workload is relatively balanced across staff")
                    
            else:
                st.info("No tickets found in database")
                
        except Exception as e:
            st.error(f"Error loading staff analytics: {str(e)}")
    
    # TAB 2: STATUS ANALYSIS
    with tab2:
        st.subheader("Ticket Status Distribution")
        
        try:
            tickets = repo.get_latest_tickets(limit=200)
            
            if tickets:
                # Count by status
                status_counts = {}
                for ticket in tickets:
                    status = ticket.status
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Create pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=list(status_counts.keys()),
                    values=list(status_counts.values()),
                    hole=0.3
                )])
                
                fig.update_layout(
                    title="Ticket Distribution by Status",
                    height=450
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Status breakdown table
                status_df = pd.DataFrame({
                    'Status': list(status_counts.keys()),
                    'Count': list(status_counts.values()),
                    'Percentage': [v/sum(status_counts.values())*100 for v in status_counts.values()]
                }).sort_values('Count', ascending=False)
                
                st.dataframe(
                    status_df.style.format({
                        'Count': '{:.0f}',
                        'Percentage': '{:.1f}%'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Bottleneck identification
                resolved = status_counts.get('Resolved', 0)
                total = sum(status_counts.values())
                resolution_rate = (resolved / total) * 100
                
                st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
                
                if resolution_rate < 50:
                    st.warning("⚠️ Resolution rate below 50% - potential bottleneck in workflow")
                    
            else:
                st.info("No tickets found")
                
        except Exception as e:
            st.error(f"Error loading status analytics: {str(e)}")
    
    # TAB 3: RESOLUTION TIMES
    with tab3:
        st.subheader("Resolution Time Analysis")
        
        try:
            tickets = repo.get_latest_tickets(limit=200)
            
            if tickets:
                # Priority distribution
                priority_counts = {}
                urgency_by_priority = {}
                
                for ticket in tickets:
                    priority = ticket.priority
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                    
                    if priority not in urgency_by_priority:
                        urgency_by_priority[priority] = []
                    urgency_by_priority[priority].append(ticket.urgency_score())
                
                # Chart: Priority distribution
                fig = px.bar(
                    x=list(priority_counts.keys()),
                    y=list(priority_counts.values()),
                    title='Ticket Volume by Priority',
                    labels={'x': 'Priority', 'y': 'Count'},
                    color=list(priority_counts.values()),
                    color_continuous_scale='RdYlGn_r'
                )
                
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # SLA information
                st.write("**SLA Targets by Priority:**")
                
                sla_data = []
                for priority in ['Critical', 'High', 'Medium', 'Low']:
                    # Create dummy ticket to get SLA
                    from app.models.it_ticket import ITTicket
                    dummy = ITTicket(
                        ticket_id=0,
                        created_at="2024-01-01",
                        priority=priority,
                        status="Open",
                        assigned_to="",
                        title="",
                        description=""
                    )
                    
                    sla_hours = dummy.get_sla_hours()
                    count = priority_counts.get(priority, 0)
                    
                    sla_data.append({
                        'Priority': priority,
                        'SLA Target': f"{sla_hours} hours",
                        'Current Count': count
                    })
                
                st.dataframe(pd.DataFrame(sla_data), use_container_width=True, hide_index=True)
                
                # Overdue analysis
                overdue_count = sum(1 for t in tickets if t.is_overdue())
                overdue_rate = (overdue_count / len(tickets)) * 100
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Overdue Tickets", overdue_count)
                with col2:
                    st.metric("Overdue Rate", f"{overdue_rate:.1f}%")
                
                if overdue_rate > 20:
                    st.error("🚨 Over 20% of tickets are overdue - immediate action required")
                    st.write("**Recommendations:**")
                    st.write("1. Implement automated escalation for tickets approaching SLA limits")
                    st.write("2. Review and rebalance staff workload")
                    st.write("3. Consider adding temporary resources during peak periods")
                elif overdue_rate > 10:
                    st.warning("⚠️ Overdue rate above 10% - monitor closely")
                else:
                    st.success("✅ Overdue rate within acceptable range")
                    
            else:
                st.info("No tickets found")
                
        except Exception as e:
            st.error(f"Error loading resolution analytics: {str(e)}")

st.markdown("---")
st.caption("Week 9 + Week 11 - Analytics with OOP Integration")