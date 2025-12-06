from typing import List, Tuple, Optional
from app.data.db import connect_database


def insert_ticket(priority: str, description: str,
                  status: str, assigned_to: str,
                  created_at: str, resolution_time_hours: Optional[int] = None) -> int:
    """
    Insert a new IT ticket into the it_tickets table.

    Returns the new ticket_id.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO it_tickets
            (priority, description, status, assigned_to, created_at, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (priority, description, status, assigned_to, created_at, resolution_time_hours),
    )
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id


def get_all_tickets() -> List[Tuple]:
    """
    Return all tickets as a list of tuples.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT ticket_id, priority, description, status, assigned_to, created_at, "
        "resolution_time_hours FROM it_tickets ORDER BY created_at DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_ticket(ticket_id: int) -> Optional[Tuple]:
    """
    Get one ticket by id.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT ticket_id, priority, description, status, assigned_to, created_at, "
        "resolution_time_hours FROM it_tickets WHERE ticket_id = ?",
        (ticket_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def update_ticket_status(ticket_id: int, new_status: str) -> int:
    """
    Update the status of a ticket.

    Returns number of rows updated.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
        (new_status, ticket_id),
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def update_resolution_time(ticket_id: int, hours: int) -> int:
    """
    Update the resolution_time_hours field for a ticket.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "UPDATE it_tickets SET resolution_time_hours = ? WHERE ticket_id = ?",
        (hours, ticket_id),
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def delete_ticket(ticket_id: int) -> int:
    """
    Delete a ticket from the table.

    Returns number of rows deleted.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM it_tickets WHERE ticket_id = ?",
        (ticket_id,),
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def count_by_status() -> List[Tuple[str, int]]:
    """
    Simple analytical query: count tickets by status.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT status, COUNT(*) AS total
        FROM it_tickets
        GROUP BY status
        ORDER BY total DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows
