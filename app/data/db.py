import os
import sqlite3

# Path to the SQLite database stored in the DATA folder
DB_PATH = os.path.join("DATA", "intelligence_platform.db")


def connect_database(path: str = DB_PATH) -> sqlite3.Connection:
    """
    Create or open the SQLite database in the DATA folder.

    This helper keeps all connection logic in one place.
    """
    # Make sure the DATA directory exists
    data_dir = os.path.dirname(path)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    conn = sqlite3.connect(path)
    # Keep the default row format (simple tuples) .
    return conn
def get_connection(path: str = DB_PATH) -> sqlite3.Connection:
    """
    Alias for connect_database to support new code.
    """
    return connect_database(path)


def close_connection(conn: sqlite3.Connection):
    """
    Close the database connection.
    """
    if conn:
        conn.close()