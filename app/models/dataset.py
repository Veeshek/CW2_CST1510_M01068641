"""
Dataset entity class for Data Science domain
Week 11: OOP implementation
"""

from dataclasses import dataclass

@dataclass
class Dataset:
    """Represents a dataset in the Data Science domain"""
    dataset_id: int
    name: str
    source: str
    size_mb: float
    rows: int
    quality_score: float
    status: str
    
    def is_large(self) -> bool:
        """Check if dataset exceeds archiving threshold"""
        return self.size_mb > 500 or self.rows > 1000000
    
    def quality_status(self) -> str:
        """Get quality status category"""
        if self.quality_score >= 0.8:
            return "Excellent"
        elif self.quality_score >= 0.7:
            return "Good"
        elif self.quality_score >= 0.6:
            return "Acceptable"
        else:
            return "Poor"
    
    def needs_quality_review(self) -> bool:
        """Check if dataset needs quality review"""
        return self.quality_score < 0.7
    
    def to_prompt_context(self) -> str:
        """Format dataset for AI assistant context"""
        return (
            f"Dataset: {self.name}\n"
            f"Source: {self.source}\n"
            f"Size: {self.size_mb} MB\n"
            f"Rows: {self.rows:,}\n"
            f"Quality Score: {self.quality_score:.2f}\n"
            f"Status: {self.status}"
        )
    
    def short_label(self) -> str:
        """Get short display label"""
        return f"{self.name} ({self.size_mb:.0f} MB)"