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


def get_all_incidents() -> List[Tuple]:
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
