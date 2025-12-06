"""
Week 8 - Interactive CLI for the intelligence platform.

This script:
- creates the database tables
- migrates users from Week 7 text file
- loads CSV files into the database
- provides an interactive menu for CRUD and simple analytics
"""

from datetime import datetime

from app.data.schema import create_tables
from app.services.user_service import migrate_users_from_txt
from app.services.csv_loader import load_all_csv_into_db

from app.data.users import (
    get_all_users,
    create_user,
    update_user_role,
    delete_user,
)
from app.data.incidents import (
    get_all_incidents,
    insert_incident,
    update_incident_status,
    delete_incident,
    count_by_severity,
)
from app.data.datasets import (
    get_all_datasets,
    insert_dataset,
    update_dataset_size,
    delete_dataset,
    count_by_owner,
)
from app.data.tickets import (
    get_all_tickets,
    insert_ticket,
    update_ticket_status,
    update_resolution_time,
    delete_ticket,
    count_by_status,
)

# We reuse the password hashing function from Week 7 auth system
try:
    from auth import hash_password
except ImportError:
    hash_password = None  # if auth.py is missing we handle it later


# =========================
#  INITIALISATION
# =========================

def init_database_pipeline() -> None:
    """
    Run the full Week 8 data pipeline:
    - create tables
    - migrate users from text file
    - load CSV files into the database
    """
    print("=== Initialising database ===")
    create_tables()
    migrate_users_from_txt()
    load_all_csv_into_db()
    print("=== Database ready ===\n")


def show_quick_summary() -> None:
    """
    Print a short summary of all domains for Week 8.
    This helps to demonstrate that the database is populated
    and that basic analytics work for all domains.
    """
    print("=== QUICK SUMMARY AFTER PIPELINE ===")

    # Users
    users = get_all_users()
    print(f"[Users] Total users in database: {len(users)}")

    # Incidents
    incidents = get_all_incidents()
    print(f"[Cyber incidents] Total incidents: {len(incidents)}")
    sev_rows = count_by_severity()
    if sev_rows:
        print("    Incidents per severity:")
        for severity, total in sev_rows:
            print(f"      {severity}: {total}")

    # Datasets
    datasets = get_all_datasets()
    print(f"[Datasets] Total datasets: {len(datasets)}")
    owner_rows = count_by_owner()
    if owner_rows:
        print("    Datasets per owner:")
        for owner, total in owner_rows:
            print(f"      {owner}: {total}")

    # Tickets
    tickets = get_all_tickets()
    print(f"[IT tickets] Total tickets: {len(tickets)}")
    status_rows = count_by_status()
    if status_rows:
        print("    Tickets per status:")
        for status, total in status_rows:
            print(f"      {status}: {total}")

    print("=== END OF SUMMARY ===\n")


# =========================
#  HELPERS FOR INPUT
# =========================

def ask(prompt: str) -> str:
    """
    Simple helper to read user input with stripping.
    """
    return input(prompt).strip()


def press_enter_to_continue() -> None:
    """
    Pause the screen so the user can read the output.
    """
    input("\nPress Enter to continue...")


# =========================
#  USERS MENU
# =========================

def users_menu() -> None:
    """
    Sub-menu for managing users in the database.
    """
    while True:
        print("\n=== USERS MENU ===")
        print("[1] List all users")
        print("[2] Create a new user")
        print("[3] Change user role")
        print("[4] Delete a user")
        print("[0] Back to main menu")

        choice = ask("Select an option: ")

        if choice == "1":
            print("\n--- All users ---")
            users = get_all_users()
            if not users:
                print("No users found.")
            else:
                for uid, username, role in users:
                    print(f"ID={uid} | username={username} | role={role}")
            press_enter_to_continue()

        elif choice == "2":
            print("\n--- Create new user ---")
            username = ask("Enter username: ")

            if hash_password is None:
                print("hash_password not available. Please implement or import it from auth.py.")
                press_enter_to_continue()
                continue

            password = ask("Enter password (will be hashed): ")
            role = ask("Enter role (user/admin/analyst) [default: user]: ") or "user"
            password_hash = hash_password(password)
            create_user(username, password_hash, role)
            print(f"User '{username}' created with role '{role}'.")
            press_enter_to_continue()

        elif choice == "3":
            print("\n--- Change user role ---")
            username = ask("Enter username: ")
            new_role = ask("Enter new role: ")
            updated = update_user_role(username, new_role)
            if updated:
                print(f"Role updated to '{new_role}' for user '{username}'.")
            else:
                print("User not found.")
            press_enter_to_continue()

        elif choice == "4":
            print("\n--- Delete user ---")
            username = ask("Enter username to delete: ")
            deleted = delete_user(username)
            if deleted:
                print(f"User '{username}' deleted.")
            else:
                print("User not found.")
            press_enter_to_continue()

        elif choice == "0":
            break
        else:
            print("Invalid option. Try again.")


# =========================
#  INCIDENTS MENU
# =========================

def incidents_menu() -> None:
    """
    Sub-menu for managing cyber incidents.
    """
    while True:
        print("\n=== CYBER INCIDENTS MENU ===")
        print("[1] List incidents (first 20)")
        print("[2] Create new incident")
        print("[3] Update incident status")
        print("[4] Delete incident")
        print("[5] Show count by severity")
        print("[0] Back to main menu")

        choice = ask("Select an option: ")

        if choice == "1":
            print("\n--- First 20 incidents ---")
            incidents = get_all_incidents()
            if not incidents:
                print("No incidents found.")
            else:
                for row in incidents[:20]:
                    incident_id, timestamp, severity, category, status, description = row
                    print(
                        f"ID={incident_id} | {timestamp} | "
                        f"{severity}/{category} | status={status}"
                    )
            press_enter_to_continue()

        elif choice == "2":
            print("\n--- Create incident ---")
            timestamp = ask("Timestamp [default: now]: ")
            if not timestamp:
                timestamp = datetime.now().isoformat(sep=" ", timespec="seconds")
            severity = ask("Severity (Low/Medium/High/Critical): ")
            category = ask("Category (e.g. Phishing, Malware): ")
            status = ask("Status (Open/Resolved/etc.): ")
            description = ask("Short description: ")

            incident_id = insert_incident(timestamp, severity, category, status, description)
            print(f"Incident created with id={incident_id}.")
            press_enter_to_continue()

        elif choice == "3":
            print("\n--- Update incident status ---")
            try:
                incident_id = int(ask("Incident ID: "))
            except ValueError:
                print("Invalid ID.")
                press_enter_to_continue()
                continue
            new_status = ask("New status: ")
            updated = update_incident_status(incident_id, new_status)
            if updated:
                print("Status updated.")
            else:
                print("Incident not found.")
            press_enter_to_continue()

        elif choice == "4":
            print("\n--- Delete incident ---")
            try:
                incident_id = int(ask("Incident ID to delete: "))
            except ValueError:
                print("Invalid ID.")
                press_enter_to_continue()
                continue
            deleted = delete_incident(incident_id)
            if deleted:
                print("Incident deleted.")
            else:
                print("Incident not found.")
            press_enter_to_continue()

        elif choice == "5":
            print("\n--- Incidents by severity ---")
            rows = count_by_severity()
            if not rows:
                print("No incident data.")
            else:
                for severity, total in rows:
                    print(f"{severity}: {total}")
            press_enter_to_continue()

        elif choice == "0":
            break
        else:
            print("Invalid option. Try again.")


# =========================
#  DATASETS MENU
# =========================

def datasets_menu() -> None:
    """
    Sub-menu for managing dataset metadata.
    """
    while True:
        print("\n=== DATASETS MENU ===")
        print("[1] List all datasets")
        print("[2] Add new dataset")
        print("[3] Update dataset size")
        print("[4] Delete dataset")
        print("[5] Show datasets per owner")
        print("[0] Back to main menu")

        choice = ask("Select an option: ")

        if choice == "1":
            print("\n--- All datasets ---")
            datasets = get_all_datasets()
            if not datasets:
                print("No datasets found.")
            else:
                for row in datasets:
                    dataset_id, name, rows, columns, uploaded_by, upload_date = row
                    print(
                        f"ID={dataset_id} | {name} | "
                        f"{rows}x{columns} | owner={uploaded_by} | date={upload_date}"
                    )
            press_enter_to_continue()

        elif choice == "2":
            print("\n--- Add dataset ---")
            name = ask("Dataset name: ")
            try:
                rows_val = int(ask("Number of rows: "))
                cols_val = int(ask("Number of columns: "))
            except ValueError:
                print("Rows/columns must be integers.")
                press_enter_to_continue()
                continue
            uploaded_by = ask("Uploaded by: ")
            upload_date = ask("Upload date [YYYY-MM-DD, default: today]: ")
            if not upload_date:
                upload_date = datetime.now().date().isoformat()

            dataset_id = insert_dataset(name, rows_val, cols_val, uploaded_by, upload_date)
            print(f"Dataset created with id={dataset_id}.")
            press_enter_to_continue()

        elif choice == "3":
            print("\n--- Update dataset size ---")
            try:
                dataset_id = int(ask("Dataset ID: "))
                new_rows = int(ask("New number of rows: "))
                new_cols = int(ask("New number of columns: "))
            except ValueError:
                print("IDs and sizes must be integers.")
                press_enter_to_continue()
                continue
            updated = update_dataset_size(dataset_id, new_rows, new_cols)
            if updated:
                print("Dataset size updated.")
            else:
                print("Dataset not found.")
            press_enter_to_continue()

        elif choice == "4":
            print("\n--- Delete dataset ---")
            try:
                dataset_id = int(ask("Dataset ID to delete: "))
            except ValueError:
                print("Invalid ID.")
                press_enter_to_continue()
                continue
            deleted = delete_dataset(dataset_id)
            if deleted:
                print("Dataset deleted.")
            else:
                print("Dataset not found.")
            press_enter_to_continue()

        elif choice == "5":
            print("\n--- Datasets per owner ---")
            rows = count_by_owner()
            if not rows:
                print("No dataset data.")
            else:
                for owner, total in rows:
                    print(f"{owner}: {total}")
            press_enter_to_continue()

        elif choice == "0":
            break
        else:
            print("Invalid option. Try again.")


# =========================
#  TICKETS MENU
# =========================

def tickets_menu() -> None:
    """
    Sub-menu for managing IT tickets.
    """
    while True:
        print("\n=== IT TICKETS MENU ===")
        print("[1] List tickets (first 20)")
        print("[2] Create new ticket")
        print("[3] Update ticket status")
        print("[4] Update ticket resolution time")
        print("[5] Delete ticket")
        print("[6] Show tickets per status")
        print("[0] Back to main menu")

        choice = ask("Select an option: ")

        if choice == "1":
            print("\n--- First 20 tickets ---")
            tickets = get_all_tickets()
            if not tickets:
                print("No tickets found.")
            else:
                for row in tickets[:20]:
                    (
                        ticket_id,
                        priority,
                        description,
                        status,
                        assigned_to,
                        created_at,
                        resolution_time_hours,
                    ) = row
                    print(
                        f"ID={ticket_id} | {priority} | status={status} | "
                        f"assigned_to={assigned_to} | created={created_at} | "
                        f"resolution={resolution_time_hours}"
                    )
            press_enter_to_continue()

        elif choice == "2":
            print("\n--- Create ticket ---")
            priority = ask("Priority (Low/Medium/High): ")
            description = ask("Description: ")
            status = ask("Status (Open/In Progress/etc.): ")
            assigned_to = ask("Assigned to: ")
            created_at = ask("Created at [YYYY-MM-DD HH:MM, default: now]: ")
            if not created_at:
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res_str = ask("Resolution time in hours [optional]: ")
            resolution_time = None
            if res_str:
                try:
                    resolution_time = int(res_str)
                except ValueError:
                    print("Resolution time ignored (must be integer).")

            ticket_id = insert_ticket(
                priority,
                description,
                status,
                assigned_to,
                created_at,
                resolution_time,
            )
            print(f"Ticket created with id={ticket_id}.")
            press_enter_to_continue()

        elif choice == "3":
            print("\n--- Update ticket status ---")
            try:
                ticket_id = int(ask("Ticket ID: "))
            except ValueError:
                print("Invalid ID.")
                press_enter_to_continue()
                continue
            new_status = ask("New status: ")
            updated = update_ticket_status(ticket_id, new_status)
            if updated:
                print("Ticket status updated.")
            else:
                print("Ticket not found.")
            press_enter_to_continue()

        elif choice == "4":
            print("\n--- Update resolution time ---")
            try:
                ticket_id = int(ask("Ticket ID: "))
                hours = int(ask("Resolution time in hours: "))
            except ValueError:
                print("ID and hours must be integers.")
                press_enter_to_continue()
                continue
            updated = update_resolution_time(ticket_id, hours)
            if updated:
                print("Resolution time updated.")
            else:
                print("Ticket not found.")
            press_enter_to_continue()

        elif choice == "5":
            print("\n--- Delete ticket ---")
            try:
                ticket_id = int(ask("Ticket ID to delete: "))
            except ValueError:
                print("Invalid ID.")
                press_enter_to_continue()
                continue
            deleted = delete_ticket(ticket_id)
            if deleted:
                print("Ticket deleted.")
            else:
                print("Ticket not found.")
            press_enter_to_continue()

        elif choice == "6":
            print("\n--- Tickets per status ---")
            rows = count_by_status()
            if not rows:
                print("No ticket data.")
            else:
                for status, total in rows:
                    print(f"{status}: {total}")
            press_enter_to_continue()

        elif choice == "0":
            break
        else:
            print("Invalid option. Try again.")


# =========================
#  MAIN MENU
# =========================

def main() -> None:
    """
    Main entry point: runs the pipeline once,
    prints a quick summary, then opens the CLI menu.
    """
    init_database_pipeline()
    show_quick_summary()

    while True:
        print("\n=== MAIN MENU ===")
        print("[1] Manage users")
        print("[2] Manage cyber incidents")
        print("[3] Manage datasets")
        print("[4] Manage IT tickets")
        print("[0] Exit")

        choice = ask("Select an option: ")

        if choice == "1":
            users_menu()
        elif choice == "2":
            incidents_menu()
        elif choice == "3":
            datasets_menu()
        elif choice == "4":
            tickets_menu()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
