import bcrypt
import os
import secrets
import re
from datetime import datetime, timedelta

USER_DATA_FILE = "DATA/users.txt"
LOCKOUT_FILE = "DATA/lockouts.txt"
SESSION_FILE = "DATA/sessions.txt"


def ensure_data_dir_exists():
    """
    Makes sure the DATA directory exists before writing any files.
    """
    data_dir = os.path.dirname(USER_DATA_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)


def hash_password(plain_text_password):
    """
    Hashes a password using bcrypt with automatic salt generation.
    """
    password_bytes = plain_text_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    """
    Verifies a plaintext password against a stored bcrypt hash.
    """
    password_bytes = plain_text_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def user_exists(username):
    """
    Checks if a username already exists in the user database.
    """
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, 'r') as file:
        for line in file:
            if line.strip():
                stored_username = line.strip().split(',')[0]
                if stored_username == username:
                    return True
    return False


def register_user(username, password, role="user"):
    """
    Registers a new user by hashing their password and storing credentials.
    """
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False

    ensure_data_dir_exists()  

    hashed_pwd = hash_password(password)

    with open(USER_DATA_FILE, 'a') as file:
        file.write(f"{username},{hashed_pwd},{role}\n")

    print(f"Success: User '{username}' registered successfully!")
    return True


def is_account_locked(username):
    """
    Checks if an account is currently locked due to failed login attempts.
    """
    if not os.path.exists(LOCKOUT_FILE):
        return False

    with open(LOCKOUT_FILE, 'r') as file:
        for line in file:
            if line.strip():
                stored_username, attempts, lockout_time = line.strip().split(',')
                if stored_username == username:
                    attempts = int(attempts)
                    lockout_time = datetime.fromisoformat(lockout_time)

                    if attempts >= 3:
                        if datetime.now() < lockout_time:
                            remaining = (lockout_time - datetime.now()).seconds
                            print(f"Error: Account locked. Try again in {remaining//60}m {remaining%60}s.")
                            return True
                        else:
                            reset_failed_attempts(username)
                            return False
    return False


def record_failed_attempt(username):
    """
    Records a failed login attempt and locks account if necessary.
    """
    ensure_data_dir_exists()

    attempts = get_failed_attempts(username) + 1
    lockout_time = datetime.now() + timedelta(minutes=5)

    lines = []
    if os.path.exists(LOCKOUT_FILE):
        with open(LOCKOUT_FILE, 'r') as file:
            lines = file.readlines()

    with open(LOCKOUT_FILE, 'w') as file:
        found = False
        for line in lines:
            stored_username, _, _ = line.strip().split(',')
            if stored_username == username:
                file.write(f"{username},{attempts},{lockout_time.isoformat()}\n")
                found = True
            else:
                file.write(line)
        if not found:
            file.write(f"{username},{attempts},{lockout_time.isoformat()}\n")

    if attempts >= 3:
        print("Account locked for 5 minutes.")
    else:
        print(f"Failed login attempts: {attempts}/3")


def get_failed_attempts(username):
    """
    Gets the number of failed login attempts for a user.
    """
    if not os.path.exists(LOCKOUT_FILE):
        return 0

    with open(LOCKOUT_FILE, 'r') as file:
        for line in file:
            stored_username, attempts, lockout_time = line.strip().split(',')
            lockout_time = datetime.fromisoformat(lockout_time)

            if stored_username == username and datetime.now() < lockout_time:
                return int(attempts)
    return 0


def reset_failed_attempts(username):
    """
    Removes lockout entry after successful login.
    """
    if not os.path.exists(LOCKOUT_FILE):
        return

    with open(LOCKOUT_FILE, 'r') as file:
        lines = file.readlines()

    with open(LOCKOUT_FILE, 'w') as file:
        for line in lines:
            if not line.startswith(username + ","):
                file.write(line)


def login_user(username, password):
    """
    Authenticates a user and creates a session token.
    """
    if is_account_locked(username):
        return False

    if not os.path.exists(USER_DATA_FILE):
        print("Error: No users registered yet.")
        return False

    with open(USER_DATA_FILE, 'r') as file:
        for line in file:
            if line.strip():
                stored_username, stored_hash, role = line.strip().split(',')

                if stored_username == username:
                    if verify_password(password, stored_hash):
                        reset_failed_attempts(username)
                        print(f"Success: Welcome, {username}!")
                        print("Role:", role)
                        print("Session Token:", create_session(username))
                        return True
                    else:
                        print("Error: Invalid password.")
                        record_failed_attempt(username)
                        return False

    print("Error: Username not found.")
    return False


def validate_username(username):
    """
    Validates username format (3–20 alphanumeric characters).
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(username) > 20:
        return False, "Username must not exceed 20 characters."
    if not re.match(r"^[a-zA-Z0-9]+$", username):
        return False, "Username must contain only alphanumeric characters."
    return True, ""


def validate_password(password):
    """
    Validates password length (6–50 characters).
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if len(password) > 50:
        return False, "Password must not exceed 50 characters."
    return True, ""


def check_password_strength(password):
    """
    Returns (strength_level, recommendations list).
    """
    score = 0
    rec = []

    if len(password) >= 8: score += 1
    else: rec.append("Use at least 8 characters")

    if len(password) >= 12: score += 1
    else: rec.append("Consider 12+ characters")

    if re.search(r"[a-z]", password): score += 1
    else: rec.append("Add lowercase letters")

    if re.search(r"[A-Z]", password): score += 1
    else: rec.append("Add uppercase letters")

    if re.search(r"[0-9]", password): score += 1
    else: rec.append("Add numbers")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 1
    else: rec.append("Add special characters")

    if any(p in password.lower() for p in ["password", "123456", "qwerty", "abc123"]):
        score -= 2
        rec.append("Avoid common patterns")

    if score <= 2: strength = "Weak"
    elif score <= 4: strength = "Medium"
    else: strength = "Strong"

    return strength, rec


def create_session(username):
    """
    Creates and saves a session token.
    """
    ensure_data_dir_exists()

    token = secrets.token_hex(16)
    timestamp = datetime.now().isoformat()

    with open(SESSION_FILE, 'a') as file:
        file.write(f"{username},{token},{timestamp}\n")

    return token


def display_menu():
    print("\n" + "=" * 50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("=" * 50)
    print("[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)


def main():
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("Please select an option (1-3): ").strip()

        if choice == "1":
            print("\n--- USER REGISTRATION ---")

            username = input("Enter a username: ").strip()
            valid, msg = validate_username(username)
            if not valid:
                print("Error:", msg)
                return

            while True:
                password = input("Enter a password: ").strip()
                valid, msg = validate_password(password)
                if not valid:
                    print("Error:", msg)
                    continue

                strength, rec = check_password_strength(password)
                print("Password strength:", strength)

                if rec:
                    print("\nPassword recommendations:")
                    for r in rec:
                        print("-", r)
                    retry = input("Try different password? (y/n): ").strip().lower()
                    if retry == "y":
                        continue

                break

            confirm = input("Confirm password: ").strip()
            if confirm != password:
                print("Error: Passwords do not match.")
                return

            role = input("Enter role (user/admin/analyst) [default: user]: ").strip().lower()
            role = role if role in ["user", "admin", "analyst"] else "user"

            register_user(username, password, role)

        elif choice == "2":
            print("\n--- USER LOGIN ---")
            u = input("Enter username: ").strip()
            p = input("Enter password: ").strip()
            login_user(u, p)
            input("Press Enter to return...")

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
