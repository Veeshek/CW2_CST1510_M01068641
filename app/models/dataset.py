"""
Dataset Entity Class (Week 11 - OOP)

Represents a dataset from the Data Science domain.

This class encapsulates:
- Dataset metadata (name, source, size, quality, etc.)
- Business logic methods (is_large, quality_status, etc.)
- AI context formatting

Week 11 concept: Instead of passing around dictionaries or tuples,
we use proper objects that bundle data + behavior together.
"""

from dataclasses import dataclass


@dataclass
class Dataset:
    """
    Represents a dataset in the data catalog.
    
    Attributes match the columns from datasets_metadata table in the database.
    """
    dataset_id: int
    name: str
    source: str
    size_mb: float
    rows: int
    quality_score: float
    status: str

    def is_large(self) -> bool:
        """
        Check if this dataset is considered 'large' and might need archiving.
        
        Threshold: 500 MB or 1 million rows
        This is a business rule encapsulated in the object.
        """
        return self.size_mb > 500 or self.rows > 1_000_000

    def quality_status(self) -> str:
        """
        Convert numeric quality score to a human-readable category.
        
        This method shows OOP in action: the dataset knows how to
        interpret its own quality score.
        """
        if self.quality_score >= 0.8:
            return "Good"
        elif self.quality_score >= 0.6:
            return "Fair"
        else:
            return "Poor"

    def short_label(self) -> str:
        """
        Create a compact label for UI dropdowns and selectors.
        
        Format: "ID | Name | Source | Size MB | Status"
        """
        return (
            f"{self.dataset_id} | {self.name} | "
            f"{self.source} | {self.size_mb:.1f}MB | {self.status}"
        )

    def to_prompt_context(self) -> str:
        """
        Format dataset information for AI assistant context injection.
        
        This is used in Week 10 AI integration - when a user selects
        a dataset, we can inject its details into the ChatGPT prompt.
        
        Week 11 benefit: The entity knows how to represent itself,
        so the AI page doesn't need to know dataset field details.
        """
        return (
            f"Dataset ID: {self.dataset_id}\n"
            f"Name: {self.name}\n"
            f"Source: {self.source}\n"
            f"Size: {self.size_mb:.2f} MB\n"
            f"Rows: {self.rows:,}\n"
            f"Quality Score: {self.quality_score:.2f} ({self.quality_status()})\n"
            f"Status: {self.status}\n"
            f"Size Category: {'Large (consider archiving)' if self.is_large() else 'Normal'}\n"
        )

    def needs_quality_review(self) -> bool:
        """
        Check if this dataset should be flagged for quality review.
        
        Datasets with quality score below 0.7 need attention.
        """
        return self.quality_score < 0.7