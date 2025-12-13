# CST1510 – Coursework 2  
## Multi-Domain Intelligence Platform

**Student Name:** Veeshek Bhagoban  
**Student ID:** M01068641  
**Module:** CST1510 – Programming for Data Communication and Networks  
**Institution:** Middlesex University Mauritius  

---

## 📌 Overview

This repository contains the submission for **Coursework 2** of the module  
**CST1510 – Programming for Data Communication and Networks**.

The project implements a **Multi-Domain Intelligence Platform** developed using  
**Python**, **Streamlit**, **SQLite**, and **Pandas**.

The coursework consolidates concepts introduced progressively throughout the module,
including secure authentication, database abstraction, CRUD operations, analytics,
and role-based access control.

---

## 🗓️ Week 7 – Secure Authentication System

During this phase, a complete authentication system was implemented.

### Features
- User registration and login
- Password hashing using **bcrypt**
- Password strength validation
- Account lockout after multiple failed login attempts
- Session handling using Streamlit `session_state`
- Persistent storage of users, sessions, and lockout records

### Security
- Protected pages are inaccessible without authentication
- Sessions are invalidated on logout
- Credentials are never stored in plain text

---

## 🗓️ Week 8 – Data Layer & CRUD Operations

This phase focused on database design, abstraction, and full CRUD functionality.

### Database Architecture
- SQLite database with a structured schema
- Centralised database connection (`db.py`)
- Schema initialisation handled via `schema.py`
- Initial data loaded from CSV files

### Data Abstraction
- Clear separation between UI logic and database access
- All SQL queries encapsulated in dedicated data modules (`app/data`)
- UI pages never execute raw SQL directly

### CRUD Functionality (Create, Read, Update, Delete)

Full CRUD operations were implemented for **all application domains**:

#### 🛡️ Cybersecurity – Incidents
- **Create:** add new cybersecurity incidents
- **Read:** list and filter incidents
- **Update:** modify severity, category, status, and description
- **Delete:** remove incidents (admin only)

#### 📊 Data Science – Dataset Metadata
- **Create:** add dataset metadata records
- **Read:** display dataset information and statistics
- **Update:** modify dataset size and ownership details
- **Delete:** remove dataset entries

#### ⚙️ IT Operations – Support Tickets
- **Create:** create IT support tickets
- **Read:** view tickets and status summaries
- **Update:** change ticket priority, status, and assignment
- **Delete:** remove tickets (admin only)

Role-based access control is enforced for all write operations.

---

## 🗓️ Week 9 – Multi-Page Application, RBAC & Analytics

The final phase focused on application structure, security, and analytics.

### Application Structure
- Multi-page Streamlit application
- Custom top navigation bar
- Default Streamlit sidebar hidden
- Consistent layout and styling across all pages

### Role-Based Access Control (RBAC)

User access is controlled according to assigned roles:

- **User:** limited access (dashboard and settings)
- **Analyst:** access to dashboards and analytics (read-only data)
- **Admin:** full access including CRUD operations

Unauthorized access attempts are blocked and redirected to the login page.

### Analytics & Visualisation
- Cybersecurity dashboards with interactive charts
- Phishing incident trend analysis
- Dataset storage and archiving insights
- IT ticket status, priority, and staff performance analytics
- Key metrics displayed using `st.metric`
- CSV export functionality for incident data

---

## 📂 Project Structure

.
├── main.py
├── pages/
│ ├── 01_Login.py
│ ├── 02_Dashboard.py
│ ├── 03_Analytics.py
│ ├── 04_Manage_Data.py
│ └── 05_Settings.py
├── app/
│ ├── data/
│ │ ├── db.py
│ │ ├── schema.py
│ │ ├── users.py
│ │ ├── incidents.py
│ │ ├── datasets.py
│ │ └── tickets.py
│ └── services/
│ ├── user_service.py
│ └── csv_loader.py
├── DATA/
│ ├── intelligence_platform.db
│ ├── cyber_incidents.csv
│ ├── datasets_metadata.csv
│ ├── it_tickets.csv
│ ├── lockouts.txt
│ ├── sessions.txt
│ └── users.txt
├── requirements.txt
├── README.md
└── .gitignore

---