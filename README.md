# CST1510 – Coursework 2  
## Multi-Domain Intelligence Platform

**Module:** CST1510 – Programming for Data Communication and Networks  
**Student Name:** Veeshek Bhagoban  
**Student ID:** M01068641  
**Institution:** Middlesex University Mauritius  
**Assessment Type:** Coursework 2  

---

## 📌 Project Overview

This project is a **Multi-Domain Intelligence Platform** developed using **Python**, **Streamlit**, **SQLite**, and **Pandas**.  
It brings together the main concepts covered throughout the module and applies them in a single, coherent application.

The platform is designed to support **three operational domains**:

- 🛡️ **Cybersecurity**
- 📊 **Data Science**
- ⚙️ **IT Operations**

Each domain provides data management, analytics, and decision-support features, all integrated into a secure, multi-page Streamlit application.

---

## 🎯 Learning Objectives Covered

This coursework demonstrates practical understanding of:

- Secure authentication and access control
- Database design and CRUD operations
- Data analysis and visualisation
- Multi-page Streamlit applications
- Object-Oriented Programming (OOP)
- AI-assisted decision support
- Clean software architecture and documentation

---

## 🗓️ Week 6 – Git & Project Setup

During Week 6, the project foundation was established:

- GitHub repository creation and management
- Clear separation of concerns between UI, services, and data layers
- Use of `.gitignore` to exclude virtual environments and secrets
- Incremental commits following good version control practices

---

## 🗓️ Week 7 – Authentication & Security

A secure authentication system was implemented with the following features:

- User registration and login
- Password hashing using **bcrypt**
- Password strength validation
- Account lockout after multiple failed login attempts
- Session management using `st.session_state`
- Role-based access control (user, analyst, admin)
- Protection of pages from unauthorised access

Security-sensitive logic is separated from the UI, ensuring better maintainability and clarity.

---

## 🗓️ Week 8 – Database Design & CRUD Operations

The platform uses **SQLite** as its database backend.

Key features include:

- Centralised database connection handling
- Structured database schema
- Domain-specific data tables for users, incidents, datasets, and IT tickets
- Full CRUD (Create, Read, Update, Delete) functionality
- Initial data loading from CSV files
- Clear separation between database logic and Streamlit UI pages

This ensures data consistency and simplifies future extensions.

---

## 🗓️ Week 9 – Data Analytics & Visualisation

Interactive dashboards and analytics views were developed using **Pandas** and **Plotly**.

Implemented features include:

- Key metrics using `st.metric`
- Interactive filters (severity, category, status)
- Line charts to show trends over time
- Bar charts and pie charts for distribution analysis
- Export of filtered data to CSV
- Domain-specific insights to support decision-making
- A consistent and professional user interface across all pages

---

## 🗓️ Week 10 – AI Integration

An **AI Assistant** was integrated to support intelligent decision-making across all domains.

### AI Features

- Integration with the **OpenAI API**
- Secure API key management using `secrets.toml`
- No API keys hardcoded in the source code
- Domain-specific AI behaviour:
  - Cybersecurity incident analysis
  - Data quality and analytics suggestions
  - IT ticket prioritisation and SLA recommendations
- Streamlit chat interface with:
  - Conversation history
  - Streaming responses
  - Clear chat functionality
- Optional database context injection:
  - Security incidents
  - Datasets
  - IT tickets
- AI functionality embedded directly into the application workflow

### Important Note on API Usage

> A valid OpenAI API key is required to generate live AI responses.  
> If no API key is provided, the AI interface, integration logic, and error handling remain fully functional for assessment purposes.

---

## 🗓️ Week 11 – Object-Oriented Programming (OOP) Refactoring

During Week 11, the project was refactored to apply **Object-Oriented Programming principles**.

### Entity (Model) Classes

Dedicated entity classes were introduced to represent real-world objects:

- User
- SecurityIncident
- Dataset
- ITTicket

Each entity encapsulates:
- Data (attributes mapped from the database)
- Behaviour (methods such as status checks, scoring rules, and context formatting)

This improves code clarity and reduces duplication across the application.

---

### Repository Pattern

A repository layer was introduced to manage database access:

- SQL queries are isolated from the UI
- Repository methods return entity objects instead of raw tuples or dictionaries
- Improves separation of concerns and maintainability
- Demonstrates clean OOP design and refactoring skills

---

### Benefits of OOP Refactoring

- Cleaner and more modular codebase
- Improved readability and structure
- Easier future maintenance and scaling
- Clear distinction between UI, services, and domain logic

---

## 🔐 Security & Best Practices

The project follows good security and development practices:

- No secrets or API keys committed to GitHub
- Sensitive configuration handled via `.streamlit/secrets.toml`
- Graceful error handling throughout the application
- Modular architecture for improved maintainability
- Clear and detailed inline comments for academic clarity

---

## ▶️ How to Run the Project

1. Activate the virtual environment  
2. Install dependencies using `requirements.txt`  
3. Run the application using Streamlit  

The application runs locally and is accessible via a web browser.

---

## ✅ Conclusion

This coursework demonstrates a complete, well-structured, and secure application that integrates:

- Authentication and authorisation
- Database-driven CRUD operations
- Data analytics and visualisation
- AI-assisted decision support
- Object-Oriented Programming principles

The project aligns fully with the learning outcomes of **CST1510** and reflects good software engineering practices.

---

**End of Coursework 2**
