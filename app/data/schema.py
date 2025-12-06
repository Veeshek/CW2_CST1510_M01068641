from app.data.db import connect_database


def create_tables() -> None:
    """
    Create all tables needed for the Week 8 intelligence platform.

    If a table already exists, SQLite will ignore the CREATE statement.
    """
    conn = connect_database()
    cur = conn.cursor()

    # Users table (for authentication, migrated from Week 7)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    # Cyber incidents domain
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

    # Datasets metadata domain
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rows INTEGER NOT NULL,
            columns INTEGER NOT NULL,
            uploaded_by TEXT NOT NULL,
            upload_date TEXT NOT NULL
        )
    """)

    # IT tickets domain
    cur.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id INTEGER PRIMARY KEY,
            priority TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolution_time_hours INTEGER
        )
    """)

    conn.commit()
    conn.close()
