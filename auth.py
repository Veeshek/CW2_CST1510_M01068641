import bcrypt
import os

USER_DATA_FILE = "users.txt"


# ---------------------------------------------------
# Hashing and verification
# ---------------------------------------------------

def hash_password(password):
    # convert password to bytes
    password_bytes = password.encode("utf-8")

    # bcrypt generates salt automatically
    salt = bcrypt.gensalt()

    # create hash
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # return as UTF-8 string for storing in file
    return hashed_bytes.decode("utf-8")


def verify_password(password, hashed_password):
    # convert inputs to bytes
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ---------------------------------------------------
# Challenge 1: Password Strength Indicator
# ---------------------------------------------------

def check_password_strength(password):
    # simple scoring system based on length + character types
    length = len(password)

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)

    special_chars = "!@#$%^&*()-_=+[]{};:,.?/"
    has_special = any(c in special_chars for c in password)

    score = 0

    if length >= 8:
        score += 1
    if has_lower and has_upper:
        score += 1
    if has_digit:
        score += 1
    if has_special:
        score += 1

    if score <= 1:
        return "Weak"
    elif score == 2:
        return "Medium"
    else:
        return "Strong"


# ---------------------------------------------------
# User file helpers
# ---------------------------------------------------

def user_exists(username):
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            stored_username, _ = line.split(",", 1)
            if stored_username == username:
                return True

    return False


def register_user(username, password):
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False

    hashed = hash_password(password)

    with open(USER_DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username},{hashed}\n")

    print(f"Success: User '{username}' registered successfully!")
    return True


def login_user(username, password):
    if not os.path.exists(USER_DATA_FILE):
        print("Error: No users are registered yet.")
        return False

    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            stored_username, stored_hash = line.split(",", 1)

            if stored_username == username:
                if verify_password(password, stored_hash):
                    print(f"Success: Welcome, {username}!")
                    return True
                else:
                    print("Error: Invalid password.")
                    return False

    print("Error: Username not found.")
    return False


# ---------------------------------------------------
# Input validation
# ---------------------------------------------------

def validate_username(username):
    # must be 3–20 alphanumeric characters
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters."
    if not username.isalnum():
        return False, "Username must contain only letters and digits."
    return True, ""


def validate_password(password):
    # password length requirement
    if len(password) < 6 or len(password) > 50:
        return False, "Password must be between 6 and 50 characters."
    return True, ""


# ---------------------------------------------------
# Menu system
# ---------------------------------------------------

def display_menu():
    print("\n" + "=" * 50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System - Week 7")
    print("=" * 50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)


def main():
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == "1":
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            is_valid, msg = validate_username(username)
            if not is_valid:
                print(f"Error: {msg}")
                continue

            password = input("Enter a password: ").strip()

            is_valid, msg = validate_password(password)
            if not is_valid:
                print(f"Error: {msg}")
                continue

            # password strength indicator (optional challenge)
            strength = check_password_strength(password)
            print(f"Password strength: {strength}")

            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            register_user(username, password)

        elif choice == "2":
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            if login_user(username, password):
                print("\nYou are now logged in.")
                input("\nPress Enter to return to main menu...")

        elif choice == "3":
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
1