"""
Dataset management module for Data Science domain
Handles CRUD operations for dataset metadata
"""

import sqlite3
from app.data.db import connect_database

def get_all_datasets():
    """Retrieve all datasets from database"""
    conn = connect_database()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT dataset_id, name, source, size_mb, rows, quality_score, status "
        "FROM datasets_metadata ORDER BY dataset_id"
    )
    
    datasets = cur.fetchall()
    conn.close()
    
    return datasets

def get_dataset_by_id(dataset_id):
    """Retrieve a specific dataset by ID"""
    conn = connect_database()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT dataset_id, name, source, size_mb, rows, quality_score, status "
        "FROM datasets_metadata WHERE dataset_id = ?",
        (dataset_id,)
    )
    
    dataset = cur.fetchone()
    conn.close()
    
    return dataset

def create_dataset(name, source, size_mb, rows, quality_score=0.8, status="Active"):
    """Create a new dataset entry"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO datasets_metadata (name, source, size_mb, rows, quality_score, status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, source, size_mb, rows, quality_score, status)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def update_dataset(dataset_id, name, source, size_mb, rows, quality_score, status):
    """Update an existing dataset"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE datasets_metadata "
            "SET name = ?, source = ?, size_mb = ?, rows = ?, quality_score = ?, status = ? "
            "WHERE dataset_id = ?",
            (name, source, size_mb, rows, quality_score, status, dataset_id)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def delete_dataset(dataset_id):
    """Delete a dataset by ID"""
    try:
        conn = connect_database()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM datasets_metadata WHERE dataset_id = ?", (dataset_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False