"""
Ticket management module for IT Operations domain
Handles CRUD operations for IT support tickets
"""

import sqlite3
from app.data.db import connect_database

def get_all_tickets():
    """Retrieve all tickets from database"""
    conn = connect_database()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT ticket_id, created_at, priority, status, assigned_to, title, description "
        "FROM it_tickets ORDER BY ticket_id"
    )
    
    tickets = cur.fetchall()
    conn.close()
    
    return tickets

def get_ticket_by_id(ticket_id):
    """Retrieve a specific ticket by ID"""
    conn = connect_database()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT ticket_id, created_at, priority, status, assigned_to, title, description "
        "FROM it_tickets WHERE ticket_id = ?",
        (ticket_id,)
    )
    
    ticket = cur.fetchone()
    conn.close()
    
    return ticket

def create_ticket(created_at, priority, status, assigned_to, title, description):
    """Create a new ticket entry"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO it_tickets (created_at, priority, status, assigned_to, title, description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (created_at, priority, status, assigned_to, title, description)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def update_ticket(ticket_id, created_at, priority, status, assigned_to, title, description):
    """Update an existing ticket"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE it_tickets "
            "SET created_at = ?, priority = ?, status = ?, assigned_to = ?, title = ?, description = ? "
            "WHERE ticket_id = ?",
            (created_at, priority, status, assigned_to, title, description, ticket_id)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def delete_ticket(ticket_id):
    """Delete a ticket by ID"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False