import os
from app.data.db import connect_database

USER_TEXT_PATH = os.path.join("DATA", "users.txt")


def migrate_users_from_txt() -> None:
    """
    Migrate users stored in the Week 7 text file into the users table.

    File format: username,password_hash,role

    This function can be run many times safely because it uses
    INSERT OR IGNORE to avoid duplicate usernames.
    """
    if not os.path.exists(USER_TEXT_PATH):
        print("No DATA/users.txt file found. Skipping user migration.")
        return

    conn = connect_database()
    cur = conn.cursor()

    migrated = 0

    with open(USER_TEXT_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) < 3:
                # Bad line format, skip it
                continue

            username, password_hash, role = parts[0], parts[1], parts[2]

            cur.execute("""
                INSERT OR IGNORE INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            migrated += cur.rowcount

    conn.commit()
    conn.close()
    print(f"User migration finished. {migrated} user(s) inserted into the database.")
