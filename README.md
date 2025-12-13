# CST1510 – Coursework 2  
## Multi-Domain Intelligence Platform

**Module:** CST1510 – Programming for Data Communication and Networks  
**Student Name:** Veeshek Bhagoban  
**Student ID:** M01068641  
**Institution:** Middlesex University Mauritius  
**Assessment:** Coursework 2  

---

## 📌 Project Overview

This project is a **Multi-Domain Intelligence Platform** developed using **Python, Streamlit, SQLite, and Pandas**.  
It integrates multiple concepts taught throughout the module, including:

- Secure user authentication
- Database design and CRUD operations
- Data analytics and visualisation
- Multi-page Streamlit applications
- AI-assisted decision support (Week 10)

The system supports **three operational domains**:
- 🛡️ Cybersecurity  
- 📊 Data Science  
- ⚙️ IT Operations  

Each domain has its own datasets, analytics, and management interfaces.

---

## 🗂️ Project Structure

├── main.py
├── pages/
│ ├── 01_Login.py
│ ├── 02_Dashboard.py
│ ├── 03_Analytics.py
│ ├── 04_Manage_Data.py
│ ├── 05_Settings.py
│ └── 06_AI_Assistant.py
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
│ ├── csv_loader.py
│ └── ai_assistant.py
├── DATA/
│ ├── intelligence_platform.db
│ ├── cyber_incidents.csv
│ ├── datasets_metadata.csv
│ ├── it_tickets.csv
│ ├── lockouts.txt
│ ├── sessions.txt
│ └── users.txt
├── requirements.txt
├── .gitignore
└── README.md

---

## 🗓️ Week 6 – Git & Project Setup

- GitHub repository created and maintained
- Clear project structure with separation of concerns
- `.gitignore` configured to exclude secrets and unnecessary files
- Incremental development using Git commits

---

## 🗓️ Week 7 – Authentication & Security

A secure authentication system was implemented with the following features:

- User registration and login
- Password hashing using **bcrypt**
- Password strength validation
- Account lockout after multiple failed login attempts
- Session management using `st.session_state`
- Role-based access control (user / analyst / admin)
- Protection against unauthorized page access

All authentication logic is isolated from UI components to improve maintainability and security.

---

## 🗓️ Week 8 – Database Design & CRUD Operations

The platform uses **SQLite** as its database backend.

### Key features:
- Centralised database connection (`db.py`)
- Structured schema creation (`schema.py`)
- Domain-specific data modules:
  - `users.py`
  - `incidents.py`
  - `datasets.py`
  - `tickets.py`
- Full **CRUD functionality** (Create, Read, Update, Delete)
- Initial data loading from CSV files
- Clean separation between database logic and Streamlit UI

---

## 🗓️ Week 9 – Data Analytics & Visualisation

Interactive dashboards were created using **Pandas** and **Plotly**.

### Implemented features:
- Multi-page Streamlit application
- Interactive filters (severity, category, status)
- Key performance metrics using `st.metric`
- Data visualisations:
  - Line charts (incident trends)
  - Bar charts (severity and status)
  - Pie charts (category distribution)
- CSV export functionality
- Domain-specific insights and interpretations
- Unified and consistent UI across all pages

---

## 🗓️ Week 10 – AI Integration

An **AI Assistant** was integrated to support decision-making across all domains.

### AI Features:
- Integration with the **OpenAI API**
- Secure API key handling via `secrets.toml`
- Domain-specific system prompts:
  - Cybersecurity analysis
  - Data quality and analytics suggestions
  - IT ticket prioritisation and SLA recommendations
- Streamlit chat interface with:
  - Conversation history
  - Streaming responses
  - Clear chat functionality
- Optional database context injection:
  - Incidents
  - Datasets
  - IT tickets
- AI integration directly embedded into the Cybersecurity Dashboard

### Important Note:
> A valid OpenAI API key is required to generate live AI responses.  
> If no key is provided, the AI interface, integration logic, and error handling remain fully functional for assessment purposes.

---

## 🔐 Security & Best Practices

- No API keys or secrets are hardcoded
- Sensitive files are excluded via `.gitignore`
- Graceful error handling throughout the application
- Modular and maintainable codebase
- Clear inline comments for academic clarity

---

## ▶️ How to Run the Project

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run main.py
