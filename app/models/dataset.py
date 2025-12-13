"""
Dataset Entity (Week 11 - OOP)

Represents a dataset metadata record in the Data Science domain.
Includes small business methods:
- is_active()
- estimated_storage_risk()
- to_prompt_context()
"""

from dataclasses import dataclass


@dataclass
class Dataset:
    dataset_id: int
    name: str
    source: str
    size_mb: float
    rows: int
    quality_score: float
    status: str

    def is_active(self) -> bool:
        """Return True if dataset is active/available."""
        return str(self.status).strip().lower() in {"active", "available", "in use"}

    def estimated_storage_risk(self) -> str:
        """
        Simple example rule: big datasets + low quality can be risky.
        It's not perfect, but it's OOP behaviour and shows thinking.
        """
        try:
            if float(self.size_mb) > 500 and float(self.quality_score) < 60:
                return "High"
            if float(self.size_mb) > 200 and float(self.quality_score) < 70:
                return "Medium"
        except Exception:
            pass
        return "Low"

    def short_label(self) -> str:
        return f"{self.dataset_id} | {self.name} | {self.source} | {self.size_mb}MB | {self.status}"

    def to_prompt_context(self) -> str:
        return (
            f"Dataset ID: {self.dataset_id}\n"
            f"Name: {self.name}\n"
            f"Source: {self.source}\n"
            f"Size (MB): {self.size_mb}\n"
            f"Rows: {self.rows}\n"
            f"Quality Score: {self.quality_score}\n"
            f"Status: {self.status}\n"
            f"Storage Risk (basic rule): {self.estimated_storage_risk()}\n"
        )
