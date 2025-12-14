"""
ITTicket Entity Class (Week 11 - OOP)

Represents an IT support ticket from the IT Operations domain.

This class encapsulates:
- Ticket data (priority, status, assignment, etc.)
- Business logic (is_overdue, urgency_score, etc.)  
- AI context formatting

Week 11 learning: Instead of working with raw database rows,
we create objects that have both data and useful methods.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ITTicket:
    """
    Represents an IT support ticket.
    
    Attributes match the columns from it_tickets table.
    """
    ticket_id: int
    created_at: str
    priority: str
    status: str
    assigned_to: str
    title: str
    description: str

    def is_overdue(self, sla_hours: int = 24) -> bool:
        """
        Check if ticket has exceeded SLA based on priority.
        
        Simple rule: if ticket is older than SLA hours and not resolved,
        it's considered overdue.
        
        Args:
            sla_hours: Service Level Agreement time limit
        
        Returns:
            True if ticket is overdue
        """
        if self.status.lower() == "resolved":
            return False
        
        try:
            created = datetime.fromisoformat(self.created_at)
            now = datetime.now()
            age_hours = (now - created).total_seconds() / 3600
            return age_hours > sla_hours
        except:
            # If date parsing fails, assume not overdue
            return False

    def urgency_score(self) -> int:
        """
        Calculate urgency score for prioritization.
        
        Higher score = more urgent
        This is business logic that belongs in the entity, not the UI.
        """
        score = 0
        
        # Priority contribution
        priority_lower = self.priority.lower()
        if priority_lower == "critical":
            score += 50
        elif priority_lower == "high":
            score += 30
        elif priority_lower == "medium":
            score += 15
        else:  # low
            score += 5
        
        # Status contribution
        status_lower = self.status.lower()
        if status_lower == "open":
            score += 20
        elif status_lower == "in progress":
            score += 10
        
        # Overdue adds urgency
        if self.is_overdue():
            score += 25
        
        return score

    def short_label(self) -> str:
        """
        Create a compact label for UI dropdowns.
        
        Format: "ID | Priority | Title | Status"
        """
        # Truncate title if too long
        title_short = self.title[:40] + "..." if len(self.title) > 40 else self.title
        return (
            f"{self.ticket_id} | {self.priority} | "
            f"{title_short} | {self.status}"
        )

    def to_prompt_context(self) -> str:
        """
        Format ticket information for AI assistant context.
        
        Week 10 integration: This context is injected into ChatGPT prompts
        when user selects a ticket to get specific advice.
        
        Week 11 benefit: Centralized formatting logic - if we need to change
        how tickets are presented to AI, we only change it here.
        """
        overdue_text = " (OVERDUE!)" if self.is_overdue() else ""
        
        return (
            f"Ticket ID: {self.ticket_id}\n"
            f"Title: {self.title}\n"
            f"Created: {self.created_at}{overdue_text}\n"
            f"Priority: {self.priority}\n"
            f"Status: {self.status}\n"
            f"Assigned To: {self.assigned_to}\n"
            f"Description: {self.description}\n"
            f"Urgency Score: {self.urgency_score()}/100\n"
        )

    def get_sla_hours(self) -> int:
        """
        Get SLA time limit based on priority.
        
        Returns expected resolution time in hours.
        """
        priority_lower = self.priority.lower()
        
        if priority_lower == "critical":
            return 4  # 4 hours
        elif priority_lower == "high":
            return 24  # 1 day
        elif priority_lower == "medium":
            return 72  # 3 days
        else:  # low
            return 168  # 1 week