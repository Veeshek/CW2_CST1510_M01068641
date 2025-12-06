# CST1510 Week 6 – Git & GitHub Practice

This week I worked on learning Git and GitHub.  
The goal was to understand cloning, committing, pushing and pulling, and how to organise files inside a repository.

## What I implemented
- Created a new GitHub repository  
- Cloned the repository into VS Code  
- Added and managed files using Git  
- Created commit messages and pushed changes to GitHub  
- Used pull and sync operations  
- Added .gitignore, README.md and requirements.txt  

## Extra features or challenges
- Tested branch syncing and Git status  
- Practised staging individual files  
- Organised the repository structure for future weeks  

## Project structure
test.py

.gitignore

README.md

requirements.txt

## How to run
Open the folder in VS Code and use the Source Control panel to commit and push.

# CST1510 Week 7 – Authentication System

This week I created a simple authentication system in Python.  
The goal was to learn how real systems store passwords securely and how to validate users during registration and login.

## What I implemented
- Registration of new users  
- Secure storage of passwords using bcrypt hashing  
- Login using hashed password verification  
- Username and password validation  
- Storage of user data inside DATA/users.txt  

## Extra features or challenges
- Password strength checker (weak, medium, strong)  
- User roles (user, admin, analyst)  
- Account lockout after 3 failed attempts (stored in DATA/lockouts.txt)  
- Session token generation after login (stored in DATA/sessions.txt)  

## Project structure
auth.py

DATA/

users.txt

lockouts.txt

sessions.txt

requirements.txt

README.md

## How to run
Install bcrypt:
pip install bcrypt

Run the program:
python auth.py