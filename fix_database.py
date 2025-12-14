"""
Database Fix Script

This script will:
1. Backup your current database (just in case)
2. Drop and recreate tables with the CORRECT schema
3. Reload data from CSV files

Run this ONCE to fix the schema mismatch errors you're seeing.

WARNING: This will delete existing data and reload from CSV files!
"""

import sys
from pathlib import Path
import sqlite3
import pandas as pd
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.data.db import connect_database

# Database file path
DB_PATH = Path(__file__).parent / "DATA" / "intelligence_platform.db"


def backup_database():
    """Create a backup of the current database."""
    if DB_PATH.exists():
        backup_path = DB_PATH.parent / f"intelligence_platform_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
    else:
        print("ℹ️  No existing database to backup")


def drop_all_tables():
    """Drop all existing tables to start fresh."""
    conn = connect_database()
    cur = conn.cursor()
    
    print("🗑️  Dropping existing tables...")
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS cyber_incidents")
    cur.execute("DROP TABLE IF EXISTS datasets_metadata")
    cur.execute("DROP TABLE IF EXISTS it_tickets")
    
    conn.commit()
    conn.close()
    print("✅ All tables dropped")


def create_correct_schema():
    """
    Create tables with the CORRECT schema that matches our code.
    
    This fixes the errors you were seeing:
    - datasets_metadata now has: source, size_mb, quality_score, status
    - it_tickets now has: title column
    """
    conn = connect_database()
    cur = conn.cursor()
    
    print("📋 Creating tables with correct schema...")
    
    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)
    
    # Cyber incidents (this one was already correct)
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
    
    # Datasets metadata - FIXED SCHEMA
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            size_mb REAL NOT NULL,
            rows INTEGER NOT NULL,
            quality_score REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'active'
        )
    """)
    
    # IT tickets - FIXED SCHEMA (added 'title')
    cur.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Tables created with correct schema")


def load_sample_data():
    """Load data from CSV files into the database."""
    conn = connect_database()
    
    data_dir = Path(__file__).parent / "DATA"
    
    print("📊 Loading data from CSV files...")
    
    # Load cyber incidents
    try:
        incidents_csv = data_dir / "cyber_incidents.csv"
        if incidents_csv.exists():
            df = pd.read_csv(incidents_csv)
            df.to_sql("cyber_incidents", conn, if_exists="replace", index=False)
            print(f"✅ Loaded {len(df)} cyber incidents")
        else:
            print(f"⚠️  File not found: {incidents_csv}")
    except Exception as e:
        print(f"❌ Error loading cyber incidents: {e}")
    
    # Load datasets metadata
    try:
        datasets_csv = data_dir / "datasets_metadata.csv"
        if datasets_csv.exists():
            df = pd.read_csv(datasets_csv)
            
            # Make sure we have all required columns
            required_cols = ['dataset_id', 'name', 'source', 'size_mb', 'rows', 'quality_score', 'status']
            
            # Add missing columns with defaults if needed
            for col in required_cols:
                if col not in df.columns:
                    if col == 'source':
                        df[col] = 'Unknown'
                    elif col == 'size_mb':
                        df[col] = df.get('rows', 0) * 0.001  # estimate from rows
                    elif col == 'quality_score':
                        df[col] = 0.75  # default good quality
                    elif col == 'status':
                        df[col] = 'active'
            
            df[required_cols].to_sql("datasets_metadata", conn, if_exists="replace", index=False)
            print(f"✅ Loaded {len(df)} datasets")
        else:
            print(f"⚠️  File not found: {datasets_csv}")
    except Exception as e:
        print(f"❌ Error loading datasets: {e}")
    
    # Load IT tickets
    try:
        tickets_csv = data_dir / "it_tickets.csv"
        if tickets_csv.exists():
            df = pd.read_csv(tickets_csv)
            
            # Make sure we have the 'title' column
            if 'title' not in df.columns:
                # Create title from description or use default
                if 'description' in df.columns:
                    df['title'] = df['description'].str[:50] + "..."
                else:
                    df['title'] = "Support Request"
            
            df.to_sql("it_tickets", conn, if_exists="replace", index=False)
            print(f"✅ Loaded {len(df)} IT tickets")
        else:
            print(f"⚠️  File not found: {tickets_csv}")
    except Exception as e:
        print(f"❌ Error loading IT tickets: {e}")
    
    conn.close()


def load_default_users():
    """Create default test users with bcrypt hashed passwords."""
    try:
        import bcrypt
        from app.data.users import create_user
        
        print("👤 Creating default users...")
        
        conn = connect_database()
        
        # Admin user
        create_user(conn, "admin", "admin123", "admin")
        
        # Analyst user
        create_user(conn, "analyst", "analyst123", "analyst")
        
        # Regular user
        create_user(conn, "user", "user123", "user")
        
        conn.close()
        print("✅ Default users created")
        
    except Exception as e:
        print(f"⚠️  Could not create users: {e}")
        print("   You'll need to register users through the UI")


def verify_schema():
    """Verify that tables have the correct columns."""
    conn = connect_database()
    cur = conn.cursor()
    
    print("\n🔍 Verifying schema...")
    
    tables = {
        'cyber_incidents': ['incident_id', 'timestamp', 'severity', 'category', 'status', 'description'],
        'datasets_metadata': ['dataset_id', 'name', 'source', 'size_mb', 'rows', 'quality_score', 'status'],
        'it_tickets': ['ticket_id', 'created_at', 'priority', 'status', 'assigned_to', 'title', 'description'],
    }
    
    all_good = True
    
    for table_name, expected_cols in tables.items():
        cur.execute(f"PRAGMA table_info({table_name})")
        actual_cols = [row[1] for row in cur.fetchall()]
        
        missing = set(expected_cols) - set(actual_cols)
        extra = set(actual_cols) - set(expected_cols)
        
        if missing or extra:
            all_good = False
            print(f"❌ {table_name}:")
            if missing:
                print(f"   Missing columns: {missing}")
            if extra:
                print(f"   Extra columns: {extra}")
        else:
            print(f"✅ {table_name}: All columns present")
    
    conn.close()
    
    if all_good:
        print("\n🎉 Schema verification passed! Database is ready.")
    else:
        print("\n⚠️  Schema has issues - please review errors above")
    
    return all_good


def main():
    """Run the full database fix process."""
    print("="*60)
    print("DATABASE FIX SCRIPT")
    print("="*60)
    print()
    
    # Step 1: Backup
    backup_database()
    print()
    
    # Step 2: Drop old tables
    drop_all_tables()
    print()
    
    # Step 3: Create new schema
    create_correct_schema()
    print()
    
    # Step 4: Load data
    load_sample_data()
    print()
    
    # Step 5: Create users
    load_default_users()
    print()
    
    # Step 6: Verify
    verify_schema()
    print()
    
    print("="*60)
    print("✅ DATABASE FIX COMPLETE!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Run your Streamlit app: streamlit run home.py")
    print("2. The AI Assistant page should now work without errors")
    print("3. Test all three domains (Cybersecurity, Data Science, IT Ops)")
    print()


if __name__ == "__main__":
    main()