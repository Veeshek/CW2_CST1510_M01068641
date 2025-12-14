"""
Repository pattern implementation
Centralizes database access and converts rows to entity objects
Week 11: OOP architecture
"""

import pandas as pd
from typing import List
from app.data.db import connect_database
from app.models.security_incident import SecurityIncident
from app.models.dataset import Dataset
from app.models.it_ticket import ITTicket

class Repository:
    """Centralized data access layer using Repository pattern"""
    
    def __init__(self):
        """Initialize repository"""
        self.conn = None
    
    def get_latest_incidents(self, limit: int = 50) -> List[SecurityIncident]:
        """
        Get latest security incidents as entity objects
        
        Args:
            limit: Maximum number of incidents to retrieve
            
        Returns:
            List of SecurityIncident objects
        """
        try:
            conn = connect_database()
            
            query = f"""
            SELECT incident_id, timestamp, severity, category, status, description
            FROM cyber_incidents
            ORDER BY incident_id DESC
            LIMIT {limit}
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            incidents = []
            for _, row in df.iterrows():
                incident = SecurityIncident(
                    incident_id=int(row['incident_id']),
                    timestamp=str(row['timestamp']),
                    severity=str(row['severity']),
                    category=str(row['category']),
                    status=str(row['status']),
                    description=str(row['description'])
                )
                incidents.append(incident)
            
            return incidents
            
        except Exception as e:
            print(f"Error loading incidents: {e}")
            return []
    
    def get_latest_datasets(self, limit: int = 100) -> List[Dataset]:
        """
        Get latest datasets as entity objects
        
        Args:
            limit: Maximum number of datasets to retrieve
            
        Returns:
            List of Dataset objects
        """
        try:
            conn = connect_database()
            
            query = f"""
            SELECT dataset_id, name, source, size_mb, rows, quality_score, status
            FROM datasets_metadata
            ORDER BY dataset_id DESC
            LIMIT {limit}
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            datasets = []
            for _, row in df.iterrows():
                dataset = Dataset(
                    dataset_id=int(row['dataset_id']),
                    name=str(row['name']),
                    source=str(row['source']),
                    size_mb=float(row['size_mb']),
                    rows=int(row['rows']),
                    quality_score=float(row['quality_score']),
                    status=str(row['status'])
                )
                datasets.append(dataset)
            
            return datasets
            
        except Exception as e:
            print(f"Error loading datasets: {e}")
            return []
    
    def get_latest_tickets(self, limit: int = 100) -> List[ITTicket]:
        """
        Get latest IT tickets as entity objects
        
        Args:
            limit: Maximum number of tickets to retrieve
            
        Returns:
            List of ITTicket objects
        """
        try:
            conn = connect_database()
            
            query = f"""
            SELECT ticket_id, created_at, priority, status, assigned_to, title, description
            FROM it_tickets
            ORDER BY ticket_id DESC
            LIMIT {limit}
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            tickets = []
            for _, row in df.iterrows():
                ticket = ITTicket(
                    ticket_id=int(row['ticket_id']),
                    created_at=str(row['created_at']),
                    priority=str(row['priority']),
                    status=str(row['status']),
                    assigned_to=str(row['assigned_to']),
                    title=str(row['title']),
                    description=str(row['description'])
                )
                tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            print(f"Error loading tickets: {e}")
            return []
    
    def get_incident_by_id(self, incident_id: int) -> SecurityIncident:
        """Get specific incident by ID"""
        try:
            conn = connect_database()
            
            query = """
            SELECT incident_id, timestamp, severity, category, status, description
            FROM cyber_incidents
            WHERE incident_id = ?
            """
            
            df = pd.read_sql_query(query, conn, params=(incident_id,))
            conn.close()
            
            if not df.empty:
                row = df.iloc[0]
                return SecurityIncident(
                    incident_id=int(row['incident_id']),
                    timestamp=str(row['timestamp']),
                    severity=str(row['severity']),
                    category=str(row['category']),
                    status=str(row['status']),
                    description=str(row['description'])
                )
            
            return None
            
        except Exception as e:
            print(f"Error getting incident: {e}")
            return None
    
    def get_dataset_by_id(self, dataset_id: int) -> Dataset:
        """Get specific dataset by ID"""
        try:
            conn = connect_database()
            
            query = """
            SELECT dataset_id, name, source, size_mb, rows, quality_score, status
            FROM datasets_metadata
            WHERE dataset_id = ?
            """
            
            df = pd.read_sql_query(query, conn, params=(dataset_id,))
            conn.close()
            
            if not df.empty:
                row = df.iloc[0]
                return Dataset(
                    dataset_id=int(row['dataset_id']),
                    name=str(row['name']),
                    source=str(row['source']),
                    size_mb=float(row['size_mb']),
                    rows=int(row['rows']),
                    quality_score=float(row['quality_score']),
                    status=str(row['status'])
                )
            
            return None
            
        except Exception as e:
            print(f"Error getting dataset: {e}")
            return None
    
    def get_ticket_by_id(self, ticket_id: int) -> ITTicket:
        """Get specific ticket by ID"""
        try:
            conn = connect_database()
            
            query = """
            SELECT ticket_id, created_at, priority, status, assigned_to, title, description
            FROM it_tickets
            WHERE ticket_id = ?
            """
            
            df = pd.read_sql_query(query, conn, params=(ticket_id,))
            conn.close()
            
            if not df.empty:
                row = df.iloc[0]
                return ITTicket(
                    ticket_id=int(row['ticket_id']),
                    created_at=str(row['created_at']),
                    priority=str(row['priority']),
                    status=str(row['status']),
                    assigned_to=str(row['assigned_to']),
                    title=str(row['title']),
                    description=str(row['description'])
                )
            
            return None
            
        except Exception as e:
            print(f"Error getting ticket: {e}")
            return None