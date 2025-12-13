"""
User service for authentication
"""

import bcrypt
from app.data.db import connect_database


def login(conn, username, password):
    """
    Authenticate a user
    Returns (success, message, user_data)
    """
    cursor = conn.cursor()
    
    # Get user from database
    cursor.execute(
        "SELECT username, password_hash, role FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    
    if not user:
        return False, "Invalid username or password", None
    
    # Verify password
    stored_hash = user[1]
    try:
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            user_data = {
                'username': user[0],
                'role': user[2]
            }
            return True, "Login successful!", user_data
        else:
            return False, "Invalid username or password", None
    except Exception as e:
        return False, f"Authentication error: {str(e)}", None


def register_user(conn, username, password, role="user"):
    """
    Register a new user
    Returns (success, message)
    """
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return False, "Username already exists"
    
    try:
        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed.decode('utf-8'), role)
        )
        conn.commit()
        
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"