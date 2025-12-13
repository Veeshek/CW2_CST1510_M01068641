from typing import List, Tuple, Optional
from app.data.db import connect_database


def insert_incident(timestamp: str, severity: str, category: str,
                    status: str, description: str = "") -> int:
    """
    Create a new cyber incident record.

    Returns the new incident_id.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO cyber_incidents (timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (timestamp, severity, category, status, description),
    )
    conn.commit()
    incident_id = cur.lastrowid
    conn.close()
    return incident_id


def get_all_incidents(conn=None) -> List[Tuple]:
    if conn is None:
        conn = connect_database()
        should_close = True
    else:
        should_close = False
    """
    Return all incidents as a list of tuples.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT incident_id, timestamp, severity, category, status, description "
        "FROM cyber_incidents ORDER BY timestamp DESC"
    )
    rows = cur.fetchall()
    if should_close:
        conn.close()
    return rows


def get_incident_by_id(incident_id: int) -> Optional[Tuple]:
    """
    Fetch one incident by its ID or return None.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT incident_id, timestamp, severity, category, status, description "
        "FROM cyber_incidents WHERE incident_id = ?",
        (incident_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def update_incident_status(incident_id: int, new_status: str) -> int:
    """
    Update the status of a cyber incident.

    Returns number of rows updated.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cyber_incidents SET status = ? WHERE incident_id = ?",
        (new_status, incident_id),
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def delete_incident(incident_id: int) -> int:
    """
    Delete an incident from the table.

    Returns number of rows deleted.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM cyber_incidents WHERE incident_id = ?",
        (incident_id,),
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def count_by_severity() -> List[Tuple[str, int]]:
    """
    Simple analytical query: count incidents per severity level.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT severity, COUNT(*) AS total
        FROM cyber_incidents
        GROUP BY severity
        ORDER BY total DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows
# ===== NEW FONCTIONS WEEK 9 ANALYTICS =====

import pandas as pd

def get_phishing_trend(conn=None):
    """
    Analyze phishing incidents per month.
    Returns DataFrame with monthly counts.
    """
    if conn is None:
        conn = connect_database()
        should_close = True
    else:
        should_close = False
    
    query = """
        SELECT 
            strftime('%Y-%m', timestamp) as month,
            COUNT(*) as total_count,
            SUM(CASE WHEN status IN ('Open', 'In Progress') THEN 1 ELSE 0 END) as unresolved
        FROM cyber_incidents
        WHERE category = 'Phishing'
        GROUP BY month
        ORDER BY month
    """
    
    df = pd.read_sql_query(query, conn)
    
    if should_close:
        conn.close()
    
    return df


def get_resolution_bottleneck(conn=None):
    """
    Identify categories with highest unresolved percentage.
    """
    if conn is None:
        conn = connect_database()
        should_close = True
    else:
        should_close = False
    
    query = """
        SELECT 
            category,
            COUNT(*) as total,
            SUM(CASE WHEN status IN ('Open', 'In Progress') THEN 1 ELSE 0 END) as unresolved,
            ROUND(CAST(SUM(CASE WHEN status IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as unresolved_pct
        FROM cyber_incidents
        GROUP BY category
        ORDER BY unresolved_pct DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    if should_close:
        conn.close()
    
    return df


def get_incidents_by_category(conn=None):
    """
    Get incident count by category for pie chart.
    """
    if conn is None:
        conn = connect_database()
        should_close = True
    else:
        should_close = False
    
    query = """
        SELECT category, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY category
        ORDER BY count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    if should_close:
        conn.close()
    
    return df


def get_incidents_by_severity_and_status(conn=None):
    """
    Get incidents grouped by severity and status.
    """
    if conn is None:
        conn = connect_database()
        should_close = True
    else:
        should_close = False
    
    query = """
        SELECT severity, status, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY severity, status
        ORDER BY severity, status
    """
    
    df = pd.read_sql_query(query, conn)
    
    if should_close:
        conn.close()
    
    return df