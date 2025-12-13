"""
User Entity (Week 11 - OOP)

This class represents a system user.
We keep it simple but "correct" for OOP:
- attributes: username, role, password_hash
- methods: helpers to check role, display, etc.

Note:
- Password hashing/verification is handled in the service layer (user_service)
  because it depends on external libs (bcrypt) + DB logic.
- Entity classes should stay "business-oriented" and easy to test.
"""

from dataclasses import dataclass


@dataclass
class User:
    """
    Represents one user account in the platform.

    Attributes:
        username (str): the unique user name
        role (str): user role: "user", "analyst", "admin"
        password_hash (str): stored hashed password (bcrypt)
    """
    username: str
    role: str
    password_hash: str = ""

    def is_admin(self) -> bool:
        """Return True if this user is an admin."""
        return self.role.lower() == "admin"

    def is_analyst(self) -> bool:
        """Return True if this user is an analyst."""
        return self.role.lower() == "analyst"

    def display_label(self) -> str:
        """Nice label used in UI."""
        return f"{self.username} ({self.role})"
