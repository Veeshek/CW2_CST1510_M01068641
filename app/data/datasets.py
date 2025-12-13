from typing import List, Tuple, Optional
from app.data.db import connect_database


def insert_dataset(name: str, rows: int, columns: int,
                   uploaded_by: str, upload_date: str) -> int:
    """
    Insert a new dataset description into datasets_metadata.

    Returns the new dataset_id.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO datasets_metadata (name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, rows, columns, uploaded_by, upload_date),
    )
    conn.commit()
    dataset_id = cur.lastrowid
    conn.close()
    return dataset_id


def get_all_datasets() -> List[Tuple]:
    """
    Return all datasets as a list of tuples.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date "
        "FROM datasets_metadata ORDER BY dataset_id"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_dataset(dataset_id: int) -> Optional[Tuple]:
    """
    Get one dataset by id.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date "
        "FROM datasets_metadata WHERE dataset_id = ?",
        (dataset_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def update_dataset_size(dataset_id: int, new_rows: int, new_columns: int) -> int:
    """
    Update the number of rows/columns for a dataset.

    Returns number of rows updated.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE datasets_metadata
        SET rows = ?, columns = ?
        WHERE dataset_id = ?
        """,
        (new_rows, new_columns, dataset_id),
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def delete_dataset(dataset_id: int) -> int:
    """
    Delete a dataset from the table.

    Returns number of rows deleted.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM datasets_metadata WHERE dataset_id = ?",
        (dataset_id,),
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def count_by_owner() -> List[Tuple[str, int]]:
    """
    Simple analytical query: count how many datasets each person uploaded.
    """
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT uploaded_by, COUNT(*) AS total
        FROM datasets_metadata
        GROUP BY uploaded_by
        ORDER BY total DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows
# ===== NEW FUNCTIONS FOR WEEK 9 ANALYTICS =====

import pandas as pd

def analyze_resource_consumption(conn=None):
    """
    Calculate estimated resource usage (rows × columns).
    """
    if conn is None:
        conn = connect_database()
        should_close = True
    else:
        should_close = False
    
    query = """
        SELECT 
            name,
            rows,
            columns,
            (rows * columns) as estimated_cells,
            uploaded_by,
            upload_date
        FROM datasets_metadata
        ORDER BY estimated_cells DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    if should_close:
        conn.close()
    
    return df


def analyze_by_uploader(conn=None):
    """
    Analyze dataset distribution by uploader.
    """
    if conn is None:
        conn = connect_database()
        should_close = True
    else:
        should_close = False
    
    query = """
        SELECT 
            uploaded_by,
            COUNT(*) as dataset_count,
            SUM(rows) as total_rows,
            AVG(rows) as avg_rows_per_dataset
        FROM datasets_metadata
        GROUP BY uploaded_by
        ORDER BY total_rows DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    if should_close:
        conn.close()
    
    return df


def identify_archiving_candidates(conn=None, row_threshold=100000):
    """
    Find datasets exceeding size threshold.
    """
    if conn is None:
        conn = connect_database()
        should_close = True
    else:
        should_close = False
    
    query = """
        SELECT 
            name,
            rows,
            columns,
            (rows * columns) as estimated_size,
            uploaded_by,
            upload_date
        FROM datasets_metadata
        WHERE rows > ?
        ORDER BY rows DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(row_threshold,))
    
    if should_close:
        conn.close()
    
    return df