"""
Incident management module for Cybersecurity domain
Handles CRUD operations for security incidents
"""

import sqlite3
from app.data.db import connect_database

def get_all_incidents():
    """Retrieve all incidents from database"""
    conn = connect_database()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT incident_id, timestamp, severity, category, status, description "
        "FROM cyber_incidents ORDER BY incident_id"
    )
    
    incidents = cur.fetchall()
    conn.close()
    
    return incidents

def get_incident_by_id(incident_id):
    """Retrieve a specific incident by ID"""
    conn = connect_database()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT incident_id, timestamp, severity, category, status, description "
        "FROM cyber_incidents WHERE incident_id = ?",
        (incident_id,)
    )
    
    incident = cur.fetchone()
    conn.close()
    
    return incident

def create_incident(timestamp, severity, category, status, description):
    """Create a new incident entry"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO cyber_incidents (timestamp, severity, category, status, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (timestamp, severity, category, status, description)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def update_incident(incident_id, timestamp, severity, category, status, description):
    """Update an existing incident"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE cyber_incidents "
            "SET timestamp = ?, severity = ?, category = ?, status = ?, description = ? "
            "WHERE incident_id = ?",
            (timestamp, severity, category, status, description, incident_id)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def delete_incident(incident_id):
    """Delete an incident by ID"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False