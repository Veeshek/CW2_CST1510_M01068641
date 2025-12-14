"""
Manage Data (CRUD) Page

This page provides full CRUD operations for all three domains:
- Cybersecurity: Security incidents
- Data Science: Dataset metadata
- IT Operations: Support tickets

Week 8: Database CRUD implementation
Week 11: OOP integration with entity classes
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ui import inject_global_css, topbar, auth_guard
from app.data.incidents import (
    get_all_incidents,
    get_incident_by_id,
    create_incident,
    update_incident,
    delete_incident,
)
from app.data.datasets import (
    get_all_datasets,
    get_dataset_by_id,
    create_dataset,
    update_dataset,
    delete_dataset,
)
from app.data.tickets import (
    get_all_tickets,
    get_ticket_by_id,
    create_ticket,
    update_ticket,
    delete_ticket,
)

# Page configuration
st.set_page_config(
    page_title="Manage Data",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply styling and authentication
inject_global_css()
auth_guard()
topbar("Manage Data")

# Get user info
user = st.session_state.get("user_info", {"username": "user", "role": "user"})

# Page header
st.title("📝 Manage Data (CRUD)")
st.caption(f"Logged in as: **{user.get('username')}** | Role: **{user.get('role')}**")
st.markdown("---")

# Domain selector
st.subheader("Select Domain:")
domain = st.radio(
    "Choose the domain to manage:",
    ["🛡️ Cybersecurity Incidents", "📊 Datasets", "🎫 IT Tickets"],
    horizontal=True,
)

st.markdown("---")

# ============================================
# CYBERSECURITY INCIDENTS CRUD
# ============================================
if domain == "🛡️ Cybersecurity Incidents":
    st.header("🛡️ Cybersecurity Incidents")
    
    # Load data function with caching
    @st.cache_data(ttl=5)
    def load_incidents_df():
        """Load incidents as DataFrame"""
        rows = get_all_incidents()
        if rows:
            return pd.DataFrame(
                rows,
                columns=["ID", "Timestamp", "Severity", "Category", "Status", "Description"]
            )
        return pd.DataFrame()
    
    # Create tabs for CRUD operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Create", "✏️ Update", "🗑️ Delete"])
    
    # TAB 1: VIEW
    with tab1:
        st.subheader("📋 All Security Incidents")
        
        df = load_incidents_df()
        
        if not df.empty:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Incidents", len(df))
            with col2:
                critical = len(df[df['Severity'] == 'Critical'])
                st.metric("Critical", critical)
            with col3:
                unresolved = len(df[df['Status'] != 'Resolved'])
                st.metric("Unresolved", unresolved)
            with col4:
                phishing = len(df[df['Category'] == 'Phishing'])
                st.metric("Phishing", phishing)
            
            st.write("")
            
            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Timestamp": st.column_config.TextColumn("Date", width="medium"),
                    "Severity": st.column_config.TextColumn("Severity", width="small"),
                    "Category": st.column_config.TextColumn("Category", width="medium"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                }
            )
            
            # Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export to CSV",
                data=csv,
                file_name="incidents_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No incidents found in database")
    
    # TAB 2: CREATE
    with tab2:
        st.subheader("➕ Create New Incident")
        
        with st.form("create_incident_form"):
            timestamp = st.text_input(
                "Timestamp*",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                help="Format: YYYY-MM-DD HH:MM:SS"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                severity = st.selectbox(
                    "Severity*",
                    ["Critical", "High", "Medium", "Low"]
                )
                category = st.selectbox(
                    "Category*",
                    ["Phishing", "Malware", "DDoS", "Insider Threat", "Data Breach", "Other"]
                )
            
            with col2:
                status = st.selectbox(
                    "Status*",
                    ["Open", "In Progress", "Resolved", "Closed"]
                )
            
            description = st.text_area(
                "Description*",
                placeholder="Detailed description of the security incident...",
                height=100
            )
            
            submitted = st.form_submit_button("✅ Create Incident", use_container_width=True)
            
            if submitted:
                if timestamp and severity and category and status and description:
                    success = create_incident(timestamp, severity, category, status, description)
                    
                    if success:
                        st.success(f"✅ Incident created successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ Failed to create incident")
                else:
                    st.warning("⚠️ Please fill all required fields")
    
    # TAB 3: UPDATE
    with tab3:
        st.subheader("✏️ Update Incident")
        
        df = load_incidents_df()
        
        if not df.empty:
            incident_options = {f"{row['ID']} - {row['Category']} ({row['Severity']})": row['ID'] 
                              for _, row in df.iterrows()}
            
            selected = st.selectbox(
                "Select Incident to Update:",
                options=list(incident_options.keys())
            )
            
            if selected:
                incident_id = incident_options[selected]
                incident = get_incident_by_id(incident_id)
                
                if incident:
                    with st.form("update_incident_form"):
                        st.write(f"**Updating Incident ID: {incident_id}**")
                        
                        timestamp = st.text_input("Timestamp*", value=incident[1])
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            severity = st.selectbox(
                                "Severity*",
                                ["Critical", "High", "Medium", "Low"],
                                index=["Critical", "High", "Medium", "Low"].index(incident[2])
                            )
                            category = st.selectbox(
                                "Category*",
                                ["Phishing", "Malware", "DDoS", "Insider Threat", "Data Breach", "Other"],
                                index=["Phishing", "Malware", "DDoS", "Insider Threat", "Data Breach", "Other"].index(incident[3])
                                      if incident[3] in ["Phishing", "Malware", "DDoS", "Insider Threat", "Data Breach", "Other"] else 0
                            )
                        
                        with col2:
                            status = st.selectbox(
                                "Status*",
                                ["Open", "In Progress", "Resolved", "Closed"],
                                index=["Open", "In Progress", "Resolved", "Closed"].index(incident[4])
                                      if incident[4] in ["Open", "In Progress", "Resolved", "Closed"] else 0
                            )
                        
                        description = st.text_area("Description*", value=incident[5], height=100)
                        
                        submitted = st.form_submit_button("💾 Update Incident", use_container_width=True)
                        
                        if submitted:
                            success = update_incident(incident_id, timestamp, severity, category, status, description)
                            
                            if success:
                                st.success(f"✅ Incident {incident_id} updated!")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Update failed")
        else:
            st.info("No incidents available to update")
    
    # TAB 4: DELETE
    with tab4:
        st.subheader("🗑️ Delete Incident")
        
        df = load_incidents_df()
        
        if not df.empty:
            incident_options = {f"{row['ID']} - {row['Category']} ({row['Severity']})": row['ID'] 
                              for _, row in df.iterrows()}
            
            selected = st.selectbox(
                "Select Incident to Delete:",
                options=list(incident_options.keys()),
                key="delete_selector"
            )
            
            if selected:
                incident_id = incident_options[selected]
                incident = get_incident_by_id(incident_id)
                
                if incident:
                    st.warning(f"⚠️ You are about to delete Incident ID: **{incident_id}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Category:** {incident[3]}")
                        st.write(f"**Severity:** {incident[2]}")
                    with col2:
                        st.write(f"**Status:** {incident[4]}")
                        st.write(f"**Date:** {incident[1]}")
                    
                    st.write(f"**Description:** {incident[5]}")
                    
                    st.error("⚠️ This action cannot be undone!")
                    
                    if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                        success = delete_incident(incident_id)
                        
                        if success:
                            st.success(f"✅ Incident {incident_id} deleted!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Delete failed")
        else:
            st.info("No incidents available to delete")

# ============================================
# DATASETS CRUD
# ============================================
elif domain == "📊 Datasets":
    st.header("📊 Datasets")
    
    # Load data function with caching
    @st.cache_data(ttl=5)
    def load_datasets_df():
        """Load datasets as DataFrame"""
        rows = get_all_datasets()
        if rows:
            return pd.DataFrame(
                rows,
                columns=["ID", "Name", "Source", "Size (MB)", "Rows", "Quality", "Status"]
            )
        return pd.DataFrame()
    
    # Create tabs for CRUD operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Create", "✏️ Update", "🗑️ Delete"])
    
    # TAB 1: VIEW
    with tab1:
        st.subheader("📋 All Datasets")
        
        df = load_datasets_df()
        
        if not df.empty:
            # Metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Datasets", len(df))
            with col2:
                total_size = df['Size (MB)'].sum()
                st.metric("Total Storage", f"{total_size:.1f} MB")
            with col3:
                avg_quality = df['Quality'].mean()
                st.metric("Avg Quality", f"{avg_quality:.2f}")
            
            st.write("")
            
            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Name": st.column_config.TextColumn("Dataset Name", width="medium"),
                    "Source": st.column_config.TextColumn("Source", width="small"),
                    "Size (MB)": st.column_config.NumberColumn("Size (MB)", format="%.1f"),
                    "Rows": st.column_config.NumberColumn("Rows", format="%d"),
                    "Quality": st.column_config.ProgressColumn("Quality", min_value=0, max_value=1),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                }
            )
            
            # Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export to CSV",
                data=csv,
                file_name="datasets_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No datasets found in database")
    
    # TAB 2: CREATE
    with tab2:
        st.subheader("➕ Create New Dataset")
        
        with st.form("create_dataset_form"):
            name = st.text_input("Dataset Name*", placeholder="e.g., Customer_Analytics_2024")
            
            col1, col2 = st.columns(2)
            with col1:
                source = st.selectbox(
                    "Source*",
                    ["IT Department", "Cybersecurity", "Data Science", "Finance", "HR", "Other"]
                )
                size_mb = st.number_input("Size (MB)*", min_value=0.1, value=100.0, step=10.0)
            
            with col2:
                rows = st.number_input("Number of Rows*", min_value=1, value=1000, step=100)
                quality_score = st.slider("Quality Score", min_value=0.0, max_value=1.0, value=0.8, step=0.1)
            
            status = st.selectbox("Status", ["Active", "Archived"])
            
            submitted = st.form_submit_button("✅ Create Dataset", use_container_width=True)
            
            if submitted:
                if name and source:
                    success = create_dataset(name, source, size_mb, rows, quality_score, status)
                    
                    if success:
                        st.success(f"✅ Dataset '{name}' created successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ Failed to create dataset")
                else:
                    st.warning("⚠️ Please fill all required fields")
    
    # TAB 3: UPDATE
    with tab3:
        st.subheader("✏️ Update Dataset")
        
        df = load_datasets_df()
        
        if not df.empty:
            dataset_options = {f"{row['ID']} - {row['Name']}": row['ID'] 
                             for _, row in df.iterrows()}
            
            selected = st.selectbox(
                "Select Dataset to Update:",
                options=list(dataset_options.keys())
            )
            
            if selected:
                dataset_id = dataset_options[selected]
                dataset = get_dataset_by_id(dataset_id)
                
                if dataset:
                    with st.form("update_dataset_form"):
                        st.write(f"**Updating Dataset ID: {dataset_id}**")
                        
                        name = st.text_input("Dataset Name*", value=dataset[1])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            source = st.selectbox(
                                "Source*",
                                ["IT Department", "Cybersecurity", "Data Science", "Finance", "HR", "Other"],
                                index=["IT Department", "Cybersecurity", "Data Science", "Finance", "HR", "Other"].index(dataset[2]) 
                                      if dataset[2] in ["IT Department", "Cybersecurity", "Data Science", "Finance", "HR", "Other"] else 0
                            )
                            size_mb = st.number_input("Size (MB)*", value=float(dataset[3]), min_value=0.1, step=10.0)
                        
                        with col2:
                            rows = st.number_input("Rows*", value=int(dataset[4]), min_value=1, step=100)
                            quality_score = st.slider("Quality Score", value=float(dataset[5]), min_value=0.0, max_value=1.0, step=0.1)
                        
                        status = st.selectbox(
                            "Status",
                            ["Active", "Archived"],
                            index=0 if dataset[6] == "Active" else 1
                        )
                        
                        submitted = st.form_submit_button("💾 Update Dataset", use_container_width=True)
                        
                        if submitted:
                            success = update_dataset(dataset_id, name, source, size_mb, rows, quality_score, status)
                            
                            if success:
                                st.success(f"✅ Dataset '{name}' updated!")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Update failed")
        else:
            st.info("No datasets available to update")
    
    # TAB 4: DELETE
    with tab4:
        st.subheader("🗑️ Delete Dataset")
        
        df = load_datasets_df()
        
        if not df.empty:
            dataset_options = {f"{row['ID']} - {row['Name']}": row['ID'] 
                             for _, row in df.iterrows()}
            
            selected = st.selectbox(
                "Select Dataset to Delete:",
                options=list(dataset_options.keys()),
                key="delete_dataset_selector"
            )
            
            if selected:
                dataset_id = dataset_options[selected]
                dataset = get_dataset_by_id(dataset_id)
                
                if dataset:
                    st.warning(f"⚠️ You are about to delete Dataset ID: **{dataset_id}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {dataset[1]}")
                        st.write(f"**Source:** {dataset[2]}")
                        st.write(f"**Size:** {dataset[3]} MB")
                    with col2:
                        st.write(f"**Rows:** {dataset[4]:,}")
                        st.write(f"**Quality:** {dataset[5]:.2f}")
                        st.write(f"**Status:** {dataset[6]}")
                    
                    st.error("⚠️ This action cannot be undone!")
                    
                    if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                        success = delete_dataset(dataset_id)
                        
                        if success:
                            st.success(f"✅ Dataset {dataset_id} deleted!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Delete failed")
        else:
            st.info("No datasets available to delete")

# ============================================
# IT TICKETS CRUD
# ============================================
else:  # IT Tickets
    st.header("🎫 IT Support Tickets")
    
    # Load data function with caching
    @st.cache_data(ttl=5)
    def load_tickets_df():
        """Load tickets as DataFrame"""
        rows = get_all_tickets()
        if rows:
            return pd.DataFrame(
                rows,
                columns=["ID", "Created", "Priority", "Status", "Assigned To", "Title", "Description"]
            )
        return pd.DataFrame()
    
    # Create tabs for CRUD operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Create", "✏️ Update", "🗑️ Delete"])
    
    # TAB 1: VIEW
    with tab1:
        st.subheader("📋 All Support Tickets")
        
        df = load_tickets_df()
        
        if not df.empty:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tickets", len(df))
            with col2:
                critical = len(df[df['Priority'] == 'Critical'])
                st.metric("Critical", critical)
            with col3:
                open_tickets = len(df[df['Status'] == 'Open'])
                st.metric("Open", open_tickets)
            with col4:
                resolved = len(df[df['Status'] == 'Resolved'])
                st.metric("Resolved", resolved)
            
            st.write("")
            
            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Created": st.column_config.TextColumn("Created", width="medium"),
                    "Priority": st.column_config.TextColumn("Priority", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Assigned To": st.column_config.TextColumn("Assigned To", width="medium"),
                    "Title": st.column_config.TextColumn("Title", width="medium"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                }
            )
            
            # Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export to CSV",
                data=csv,
                file_name="tickets_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No tickets found in database")
    
    # TAB 2: CREATE
    with tab2:
        st.subheader("➕ Create New Ticket")
        
        with st.form("create_ticket_form"):
            created_at = st.text_input(
                "Created At*",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                help="Format: YYYY-MM-DD HH:MM:SS"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                priority = st.selectbox(
                    "Priority*",
                    ["Critical", "High", "Medium", "Low"]
                )
                status = st.selectbox(
                    "Status*",
                    ["Open", "In Progress", "Waiting for User", "Resolved", "Closed"]
                )
            
            with col2:
                assigned_to = st.text_input(
                    "Assigned To*",
                    placeholder="e.g., Michael Chen"
                )
            
            title = st.text_input(
                "Title*",
                placeholder="Brief summary of the issue"
            )
            
            description = st.text_area(
                "Description*",
                placeholder="Detailed description of the ticket...",
                height=100
            )
            
            submitted = st.form_submit_button("✅ Create Ticket", use_container_width=True)
            
            if submitted:
                if created_at and priority and status and assigned_to and title and description:
                    success = create_ticket(created_at, priority, status, assigned_to, title, description)
                    
                    if success:
                        st.success(f"✅ Ticket created successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ Failed to create ticket")
                else:
                    st.warning("⚠️ Please fill all required fields")
    
    # TAB 3: UPDATE
    with tab3:
        st.subheader("✏️ Update Ticket")
        
        df = load_tickets_df()
        
        if not df.empty:
            ticket_options = {f"{row['ID']} - {row['Title']} ({row['Priority']})": row['ID'] 
                            for _, row in df.iterrows()}
            
            selected = st.selectbox(
                "Select Ticket to Update:",
                options=list(ticket_options.keys())
            )
            
            if selected:
                ticket_id = ticket_options[selected]
                ticket = get_ticket_by_id(ticket_id)
                
                if ticket:
                    with st.form("update_ticket_form"):
                        st.write(f"**Updating Ticket ID: {ticket_id}**")
                        
                        created_at = st.text_input("Created At*", value=ticket[1])
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            priority = st.selectbox(
                                "Priority*",
                                ["Critical", "High", "Medium", "Low"],
                                index=["Critical", "High", "Medium", "Low"].index(ticket[2])
                            )
                            status = st.selectbox(
                                "Status*",
                                ["Open", "In Progress", "Waiting for User", "Resolved", "Closed"],
                                index=["Open", "In Progress", "Waiting for User", "Resolved", "Closed"].index(ticket[3])
                                      if ticket[3] in ["Open", "In Progress", "Waiting for User", "Resolved", "Closed"] else 0
                            )
                        
                        with col2:
                            assigned_to = st.text_input("Assigned To*", value=ticket[4])
                        
                        title = st.text_input("Title*", value=ticket[5])
                        description = st.text_area("Description*", value=ticket[6], height=100)
                        
                        submitted = st.form_submit_button("💾 Update Ticket", use_container_width=True)
                        
                        if submitted:
                            success = update_ticket(ticket_id, created_at, priority, status, assigned_to, title, description)
                            
                            if success:
                                st.success(f"✅ Ticket {ticket_id} updated!")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Update failed")
        else:
            st.info("No tickets available to update")
    
    # TAB 4: DELETE
    with tab4:
        st.subheader("🗑️ Delete Ticket")
        
        df = load_tickets_df()
        
        if not df.empty:
            ticket_options = {f"{row['ID']} - {row['Title']}": row['ID'] 
                            for _, row in df.iterrows()}
            
            selected = st.selectbox(
                "Select Ticket to Delete:",
                options=list(ticket_options.keys()),
                key="delete_ticket_selector"
            )
            
            if selected:
                ticket_id = ticket_options[selected]
                ticket = get_ticket_by_id(ticket_id)
                
                if ticket:
                    st.warning(f"⚠️ You are about to delete Ticket ID: **{ticket_id}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Title:** {ticket[5]}")
                        st.write(f"**Priority:** {ticket[2]}")
                        st.write(f"**Status:** {ticket[3]}")
                    with col2:
                        st.write(f"**Assigned To:** {ticket[4]}")
                        st.write(f"**Created:** {ticket[1]}")
                    
                    st.write(f"**Description:** {ticket[6]}")
                    
                    st.error("⚠️ This action cannot be undone!")
                    
                    if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                        success = delete_ticket(ticket_id)
                        
                        if success:
                            st.success(f"✅ Ticket {ticket_id} deleted!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Delete failed")
        else:
            st.info("No tickets available to delete")

st.markdown("---")
st.caption("Week 8 + Week 11 - Full CRUD with OOP Integration")