import os
import sqlite3
import pandas as pd
from app.data.db import DB_PATH


def _table_is_empty(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    Helper function to check if a table already contains rows.
    """
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    (count,) = cur.fetchone()
    return count == 0


def load_all_csv_into_db() -> None:
    """
    Load the three CSV files from the DATA folder into the database.

    - DATA/cyber_incidents.csv   -> cyber_incidents
    - DATA/datasets_metadata.csv -> datasets_metadata
    - DATA/it_tickets.csv        -> it_tickets

    The function only loads data if the target table is empty.
    This avoids inserting the same rows many times.
    """
    data_dir = "DATA"
    incidents_csv = os.path.join(data_dir, "cyber_incidents.csv")
    datasets_csv = os.path.join(data_dir, "datasets_metadata.csv")
    tickets_csv = os.path.join(data_dir, "it_tickets.csv")

    conn = sqlite3.connect(DB_PATH)

    # Cyber incidents
    if os.path.exists(incidents_csv):
        if _table_is_empty(conn, "cyber_incidents"):
            df = pd.read_csv(incidents_csv)
            df.to_sql("cyber_incidents", conn, if_exists="append", index=False)
            print("Loaded cyber_incidents.csv into cyber_incidents table.")
        else:
            print("cyber_incidents table already has data, skipping CSV load.")
    else:
        print("cyber_incidents.csv not found, skipping.")

    # Datasets metadata
    if os.path.exists(datasets_csv):
        if _table_is_empty(conn, "datasets_metadata"):
            df = pd.read_csv(datasets_csv)
            df.to_sql("datasets_metadata", conn, if_exists="append", index=False)
            print("Loaded datasets_metadata.csv into datasets_metadata table.")
        else:
            print("datasets_metadata table already has data, skipping CSV load.")
    else:
        print("datasets_metadata.csv not found, skipping.")

    # IT tickets
    if os.path.exists(tickets_csv):
        if _table_is_empty(conn, "it_tickets"):
            df = pd.read_csv(tickets_csv)
            df.to_sql("it_tickets", conn, if_exists="append", index=False)
            print("Loaded it_tickets.csv into it_tickets table.")
        else:
            print("it_tickets table already has data, skipping CSV load.")
    else:
        print("it_tickets.csv not found, skipping.")

    conn.close()
