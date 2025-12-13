"""
ITTicket Entity (Week 11 - OOP)

Represents an IT operations ticket.
Adds behaviour methods:
- is_open()
- sla_priority_score()
- to_prompt_context()
"""

from dataclasses import dataclass


@dataclass
class ITTicket:
    ticket_id: int
    created_at: str
    priority: str
    status: str
    assigned_to: str
    title: str
    description: str

    def is_open(self) -> bool:
        """Return True if the ticket is not resolved/closed."""
        return str(self.status).strip().lower() not in {"resolved", "closed", "done"}

    def sla_priority_score(self) -> int:
        """
        Example of OOP behaviour:
        Convert priority to a numeric score for comparisons/decisions.
        """
        p = str(self.priority).strip().lower()
        if p == "critical":
            return 4
        if p == "high":
            return 3
        if p == "medium":
            return 2
        return 1

    def short_label(self) -> str:
        return f"{self.ticket_id} | {self.priority} | {self.status} | {self.assigned_to}"

    def to_prompt_context(self) -> str:
        return (
            f"Ticket ID: {self.ticket_id}\n"
            f"Created At: {self.created_at}\n"
            f"Priority: {self.priority}\n"
            f"Status: {self.status}\n"
            f"Assigned To: {self.assigned_to}\n"
            f"Title: {self.title}\n"
            f"Description: {self.description}\n"
            f"SLA Priority Score (basic rule): {self.sla_priority_score()}\n"
        )
