# ==============================================================================
# File: lifeos/models/mixins.py
# Description: Shared foundational data models (SQLModel Mixins).
# Component: Data Layer Core
# ==============================================================================

from sqlmodel import SQLModel, Field
from typing import Optional

class TimeTrackableItem(SQLModel):
    """
    A foundational mixin providing standard time-tracking, deadlines, 
    status, and sorting fields for any LifeOS entity.
    """
    status: str = Field(default="Not Started")
    priority: str = Field(default="Medium")  # NEW: Low, Medium, High, Critical
    domain: str = Field(default="Unassigned")
    
    # Deadlines and scheduling
    start_date: Optional[str] = Field(default=None)
    due_date: Optional[str] = Field(default=None)
    
    # Timeboxing
    estimated_minutes: int = Field(default=0)
    actual_minutes: int = Field(default=0)
    
    # NEW: State Management & Sorting
    is_archived: bool = Field(default=False)
    order_index: int = Field(default=0)  # Used for drag-and-drop or strict ranking