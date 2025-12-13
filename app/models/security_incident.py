"""
SecurityIncident Entity (Week 11 - OOP)

This class represents a cybersecurity incident from the database.

We include:
- attributes matching DB fields (id, severity, category, status, etc.)
- useful business logic methods:
  - is_unresolved()
  - risk_level()
  - to_prompt_context()  -> used by Week 10 AI to inject context
"""

from dataclasses import dataclass


@dataclass
class SecurityIncident:
    incident_id: int
    timestamp: str
    severity: str
    category: str
    status: str
    description: str

    def is_unresolved(self) -> bool:
        """Return True if the incident is not resolved."""
        return str(self.status).strip().lower() != "resolved"

    def risk_level(self) -> str:
        """
        Very simple risk assessment method.
        This is an example of 'behaviour inside the object' (OOP).
        """
        sev = str(self.severity).strip().lower()
        if sev == "critical":
            return "Very High"
        if sev == "high":
            return "High"
        if sev == "medium":
            return "Medium"
        return "Low"

    def short_label(self) -> str:
        """Small label used in dropdowns."""
        return f"{self.incident_id} | {self.severity} | {self.category} | {self.status}"

    def to_prompt_context(self) -> str:
        """
        Convert the object into a clean context block for AI prompts.
        This shows good design: the entity knows how to represent itself.
        """
        return (
            f"Incident ID: {self.incident_id}\n"
            f"Timestamp: {self.timestamp}\n"
            f"Severity: {self.severity}\n"
            f"Category: {self.category}\n"
            f"Status: {self.status}\n"
            f"Description: {self.description}\n"
            f"Risk Level (basic rule): {self.risk_level()}\n"
        )
