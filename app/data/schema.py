"""
Database schema definitions for the Multi-Domain Intelligence Platform

This module creates all the necessary tables for the three domains:
- Cybersecurity (incidents)
- Data Science (datasets) 
- IT Operations (tickets)

Week 8: Initial schema design with proper normalization
Week 11: Updated to match entity class requirements
"""

from app.data.db import connect_database


def create_tables() -> None:
    """
    Create all tables needed for the intelligence platform.
    
    Uses CREATE TABLE IF NOT EXISTS so it's safe to run multiple times.
    This is helpful during development when testing schema changes.
    """
    conn = connect_database()
    cur = conn.cursor()

    # --------------------------------------------------
    # Users table (Week 7 auth migrated to database)
    # --------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    # --------------------------------------------------
    # Cybersecurity domain table
    # --------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            incident_id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            severity TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT
        )
    """)

    # --------------------------------------------------
    # Data Science domain table
    # FIXED: Added missing columns that were causing errors
    # --------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            size_mb REAL NOT NULL,
            rows INTEGER NOT NULL,
            quality_score REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'active'
        )
    """)

    # --------------------------------------------------
    # IT Operations domain table  
    # FIXED: Added missing 'title' column
    # --------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()
    

def reset_database():
    """
    Drop all tables and recreate them.
    WARNING: This deletes all data! Only use during development/testing.
    """
    conn = connect_database()
    cur = conn.cursor()
    
    # Drop existing tables
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS cyber_incidents")
    cur.execute("DROP TABLE IF EXISTS datasets_metadata")
    cur.execute("DROP TABLE IF EXISTS it_tickets")
    
    conn.commit()
    conn.close()
    
    # Recreate with correct schema
    create_tables()