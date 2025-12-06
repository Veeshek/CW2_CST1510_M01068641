# CST1510 Week 6 – Git & GitHub Practice

## Overview
This mini-project was used to practise Git operations such as cloning, committing, pushing, pulling, creating branches, and managing files inside a repository.

The goal was to become familiar with GitHub workflows before starting the larger coursework.

## What I learned
- Creating a new Git repository  
- Adding files and staging changes  
- Writing meaningful commit messages  
- Pushing code to GitHub  
- Pulling updates and resolving conflicts  
- Working with `.gitignore`

## Project structure
```
test.py
.gitignore
README.md
requirements.txt
```

## How to run
```
python test.py

```
# CST1510 Week 7 – Authentication System

## Overview
This week I implemented a simple authentication system in Python.
The goal was to understand how real applications store passwords securely and how to validate users during login.

All user information is stored inside the `DATA/` folder.

## What I implemented
- Registration of new users  
- Secure storage of password hashes using `bcrypt`  
- Login using hashed password verification  
- Username and password validation  
- Storage of user data in `DATA/users.txt`

## Extra challenges completed
- Password strength checker (weak, medium, strong)  
- User roles (user, admin, analyst)  
- Account lockout after 3 failed attempts (stored in `DATA/lockouts.txt`)  
- Session token creation after login (stored in `DATA/sessions.txt`)

## Project structure
```
auth.py
test.py
DATA/
    users.txt
    lockouts.txt
    sessions.txt
requirements.txt
README.md
```

## How to run
Install dependencies:
```
pip install bcrypt
```

Run the program:
```
python auth.py
```
# CST1510 Week 8 – SQLite Database Migration & CRUD

## Overview
This week the goal was to migrate file-based data into a SQLite database and practise CRUD operations across several domains:

- Users  
- Cyber incidents  
- Dataset metadata  
- IT support tickets  

CSV files are automatically imported into the database, and several CRUD demonstrations are included.

## What I implemented
- Creation of `intelligence_platform.db`  
- Migration of users from `DATA/users.txt`
- Automatic import of CSV files:
  - `cyber_incidents.csv`
  - `datasets_metadata.csv`
  - `it_tickets.csv`
- CRUD demonstrations:
  - Creating, reading, updating and counting incidents  
  - Creating and updating datasets  
  - Creating and modifying IT tickets  
- Aggregation queries (severity breakdown, owner grouping, ticket status, etc.)

## Extra challenges completed
- Modular project structure with `app/` folder  
- Separation of services and database logic (`db.py`, `csv_loader.py`)  
- Reusable schema definitions  
- Domain-specific modules:
  - `data/incidents.py`
  - `data/datasets.py`
  - `data/users.py`
  - `data/tickets.py`

## Project structure
```
main.py
requirements.txt
README.md
app/
    data/
        __init__.py
        db.py
        schema.py
        users.py
        incidents.py
        datasets.py
        tickets.py
    services/
        __init__.py
        csv_loader.py
        user_service.py
DATA/
    cyber_incidents.csv
    datasets_metadata.csv
    it_tickets.csv
```

## How to run
Install dependencies:
```
pip install pandas bcrypt
```

Run migration and CRUD demo:
```
python main.py
```

## Viewing the database
The generated SQLite file can be opened with any viewer, for example:
https://sqliteviewer.app
