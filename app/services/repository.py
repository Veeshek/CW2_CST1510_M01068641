"""
Repository Layer (Week 11 - OOP)

A "Repository" is a design pattern that isolates database access.
Instead of returning raw dicts or tuples, we return entity objects.

Benefits:
- UI code stays clean (no SQL everywhere)
- Easy to maintain and refactor
- Fits OOP principles (encapsulation + separation of concerns)

Week 11 concept: This layer sits between the database and the UI.
The UI calls repository methods, which return nice Python objects.
"""

import pandas as pd
from typing import List

from app.data.db import connect_database
from app.models.security_incident import SecurityIncident
from app.models.dataset import Dataset
from app.models.it_ticket import ITTicket


class Repository:
    """
    Main repository class for loading objects from the SQLite database.
    
    This class demonstrates Week 11 OOP refactoring:
    - Centralizes all database queries
    - Returns entity objects (not raw SQL rows)
    - Makes the UI code much cleaner
    """

    def get_latest_incidents(self, limit: int = 50) -> List[SecurityIncident]:
        """
        Return latest security incidents as SecurityIncident objects.
        
        Week 11 improvement: Instead of returning a list of tuples or dicts,
        we return a list of SecurityIncident objects. This means the UI can
        call methods like incident.is_unresolved() or incident.risk_level().
        
        Args:
            limit: Maximum number of incidents to return
            
        Returns:
            List of SecurityIncident objects
        """
        conn = connect_database()
        try:
            # Query the database using pandas
            df = pd.read_sql_query(
                "SELECT incident_id, timestamp, severity, category, status, description "
                "FROM cyber_incidents ORDER BY timestamp DESC LIMIT ?",
                conn,
                params=(limit,),
            )
            
            # Convert DataFrame rows to SecurityIncident objects
            incidents: List[SecurityIncident] = []
            for _, row in df.iterrows():
                incidents.append(SecurityIncident(
                    incident_id=int(row["incident_id"]),
                    timestamp=str(row["timestamp"]),
                    severity=str(row["severity"]),
                    category=str(row["category"]),
                    status=str(row["status"]),
                    description=str(row["description"]),
                ))
            
            return incidents
            
        except Exception as e:
            # If there's an error, return empty list instead of crashing
            print(f"Error loading incidents: {e}")
            return []
        finally:
            conn.close()

    def get_latest_datasets(self, limit: int = 50) -> List[Dataset]:
        """
        Return latest datasets as Dataset objects.
        
        This method loads dataset metadata from the database and converts
        each row into a Dataset entity object.
        
        Args:
            limit: Maximum number of datasets to return
            
        Returns:
            List of Dataset objects
        """
        conn = connect_database()
        try:
            df = pd.read_sql_query(
                "SELECT dataset_id, name, source, size_mb, rows, quality_score, status "
                "FROM datasets_metadata ORDER BY dataset_id DESC LIMIT ?",
                conn,
                params=(limit,),
            )
            
            datasets: List[Dataset] = []
            for _, row in df.iterrows():
                datasets.append(Dataset(
                    dataset_id=int(row["dataset_id"]),
                    name=str(row["name"]),
                    source=str(row["source"]),
                    size_mb=float(row["size_mb"]),
                    rows=int(row["rows"]),
                    quality_score=float(row["quality_score"]),
                    status=str(row["status"]),
                ))
            
            return datasets
            
        except Exception as e:
            print(f"Error loading datasets: {e}")
            return []
        finally:
            conn.close()

    def get_latest_tickets(self, limit: int = 50) -> List[ITTicket]:
        """
        Return latest IT tickets as ITTicket objects.
        
        Week 11 OOP benefit: The ITTicket object knows how to calculate
        its own urgency score, check if it's overdue, etc. The UI just
        displays this information without knowing the business rules.
        
        Args:
            limit: Maximum number of tickets to return
            
        Returns:
            List of ITTicket objects
        """
        conn = connect_database()
        try:
            df = pd.read_sql_query(
                "SELECT ticket_id, created_at, priority, status, assigned_to, title, description "
                "FROM it_tickets ORDER BY created_at DESC LIMIT ?",
                conn,
                params=(limit,),
            )
            
            tickets: List[ITTicket] = []
            for _, row in df.iterrows():
                tickets.append(ITTicket(
                    ticket_id=int(row["ticket_id"]),
                    created_at=str(row["created_at"]),
                    priority=str(row["priority"]),
                    status=str(row["status"]),
                    assigned_to=str(row["assigned_to"]),
                    title=str(row["title"]),
                    description=str(row["description"]) if pd.notna(row["description"]) else "",
                ))
            
            return tickets
            
        except Exception as e:
            print(f"Error loading tickets: {e}")
            return []
        finally:
            conn.close()

    def get_incident_by_id(self, incident_id: int) -> SecurityIncident:
        """
        Get a specific incident by ID.
        
        Returns a single SecurityIncident object or None if not found.
        """
        conn = connect_database()
        try:
            df = pd.read_sql_query(
                "SELECT incident_id, timestamp, severity, category, status, description "
                "FROM cyber_incidents WHERE incident_id = ?",
                conn,
                params=(incident_id,),
            )
            
            if len(df) == 0:
                return None
            
            row = df.iloc[0]
            return SecurityIncident(
                incident_id=int(row["incident_id"]),
                timestamp=str(row["timestamp"]),
                severity=str(row["severity"]),
                category=str(row["category"]),
                status=str(row["status"]),
                description=str(row["description"]),
            )
            
        finally:
            conn.close()

    def get_dataset_by_id(self, dataset_id: int) -> Dataset:
        """Get a specific dataset by ID."""
        conn = connect_database()
        try:
            df = pd.read_sql_query(
                "SELECT dataset_id, name, source, size_mb, rows, quality_score, status "
                "FROM datasets_metadata WHERE dataset_id = ?",
                conn,
                params=(dataset_id,),
            )
            
            if len(df) == 0:
                return None
            
            row = df.iloc[0]
            return Dataset(
                dataset_id=int(row["dataset_id"]),
                name=str(row["name"]),
                source=str(row["source"]),
                size_mb=float(row["size_mb"]),
                rows=int(row["rows"]),
                quality_score=float(row["quality_score"]),
                status=str(row["status"]),
            )
            
        finally:
            conn.close()

    def get_ticket_by_id(self, ticket_id: int) -> ITTicket:
        """Get a specific ticket by ID."""
        conn = connect_database()
        try:
            df = pd.read_sql_query(
                "SELECT ticket_id, created_at, priority, status, assigned_to, title, description "
                "FROM it_tickets WHERE ticket_id = ?",
                conn,
                params=(ticket_id,),
            )
            
            if len(df) == 0:
                return None
            
            row = df.iloc[0]
            return ITTicket(
                ticket_id=int(row["ticket_id"]),
                created_at=str(row["created_at"]),
                priority=str(row["priority"]),
                status=str(row["status"]),
                assigned_to=str(row["assigned_to"]),
                title=str(row["title"]),
                description=str(row["description"]) if pd.notna(row["description"]) else "",
            )
            
        finally:
            conn.close()