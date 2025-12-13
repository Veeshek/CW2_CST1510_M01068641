"""
Repository Layer (Week 11 - OOP)

A "Repository" is a design pattern that isolates database access.
Instead of returning raw dicts or tuples, we return entity objects.

Benefits:
- UI code stays clean (no SQL everywhere)
- easy to maintain / refactor
- fits OOP principles (encapsulation + separation of concerns)
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
    We keep it simple: read-only helper methods.
    """

    def get_latest_incidents(self, limit: int = 50) -> List[SecurityIncident]:
        """Return latest incidents as SecurityIncident objects."""
        conn = connect_database()
        try:
            df = pd.read_sql_query(
                "SELECT incident_id, timestamp, severity, category, status, description "
                "FROM cyber_incidents ORDER BY timestamp DESC LIMIT ?",
                conn,
                params=(limit,),
            )
            incidents: List[SecurityIncident] = []
            for _, r in df.iterrows():
                incidents.append(SecurityIncident(
                    incident_id=int(r["incident_id"]),
                    timestamp=str(r["timestamp"]),
                    severity=str(r["severity"]),
                    category=str(r["category"]),
                    status=str(r["status"]),
                    description=str(r["description"]),
                ))
            return incidents
        finally:
            conn.close()

    def get_latest_datasets(self, limit: int = 50) -> List[Dataset]:
        """Return latest datasets as Dataset objects."""
        conn = connect_database()
        try:
            df = pd.read_sql_query(
                "SELECT dataset_id, name, source, size_mb, rows, quality_score, status "
                "FROM datasets_metadata ORDER BY dataset_id DESC LIMIT ?",
                conn,
                params=(limit,),
            )
            datasets: List[Dataset] = []
            for _, r in df.iterrows():
                datasets.append(Dataset(
                    dataset_id=int(r["dataset_id"]),
                    name=str(r["name"]),
                    source=str(r["source"]),
                    size_mb=float(r["size_mb"]),
                    rows=int(r["rows"]),
                    quality_score=float(r["quality_score"]),
                    status=str(r["status"]),
                ))
            return datasets
        finally:
            conn.close()

    def get_latest_tickets(self, limit: int = 50) -> List[ITTicket]:
        """Return latest IT tickets as ITTicket objects."""
        conn = connect_database()
        try:
            df = pd.read_sql_query(
                "SELECT ticket_id, created_at, priority, status, assigned_to, title, description "
                "FROM it_tickets ORDER BY created_at DESC LIMIT ?",
                conn,
                params=(limit,),
            )
            tickets: List[ITTicket] = []
            for _, r in df.iterrows():
                tickets.append(ITTicket(
                    ticket_id=int(r["ticket_id"]),
                    created_at=str(r["created_at"]),
                    priority=str(r["priority"]),
                    status=str(r["status"]),
                    assigned_to=str(r["assigned_to"]),
                    title=str(r["title"]),
                    description=str(r["description"]),
                ))
            return tickets
        finally:
            conn.close()
