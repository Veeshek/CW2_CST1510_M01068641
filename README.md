# CST1510 Coursework 2
Multi-Domain Intelligence Platform

Student: Veeshek Bhagoban  
Student ID: M01068641

This repository contains the source code and documentation for CW2 Week 6–11.

# Week 7 – Authentication System

Student: Veeshek Bhagoban  
Student ID: M01068641  
Module: CST1510 – Coursework 2

## Description

This week I implemented a simple command-line authentication system.
The goal was to practise secure password handling using bcrypt and
file-based storage.

## Features

- Register new users with unique usernames
- Hash passwords using bcrypt (with automatic salt)
- Verify user login against stored hashes
- Input validation for usernames and passwords
- Text-based menu (Register / Login / Exit)
- Password strength indicator (Weak / Medium / Strong) – Extension Challenge 1

## Implementation details

- User data file: `users.txt` (format: `username,hashed_password`)
- Passwords are never stored in plain text
- Username rules: 3–20 characters, only letters and digits
- Password rules: 6–50 characters
- Strength check based on length and character types
