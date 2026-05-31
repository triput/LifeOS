# ==============================================================================
# File: models/habitat.py
# Description: Synchronized database model for PARA tasks with external IDs.
# Component: Data Layer (SQLModel)
# Version: 1.2 (Gold Master)
# Created: 2026-04-23
# Last Update: 2026-04-23
# ==============================================================================

import reflex as rx
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
from typing import List, Optional
from lifeos.models.mixins import TimeTrackableItem

class LifeHabit(rx.Model, table=True):
    """The Blueprint: Defines what you are tracking."""
    title: str
    domain: str = "HOME"           # Uses the same taxonomy: ACADEMY, THEATER, etc.
    is_numeric: bool = False       # True if it tracks numbers, False for pure binary
    target_value: int = 0          # The "baseline" (e.g., 45)
    unit_label: str = ""           # The label (e.g., "minutes", "peppers", "modules")
    is_active: bool = True         # Allows you to archive old habits
    
    created_at_local: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HabitLog(rx.Model, table=True):
    """The Ledger: The daily telemetry points for each habit."""
    habit_id: int = Field(foreign_key="lifehabit.id")
    
    # We store the date as a simple string (YYYY-MM-DD) for lightning-fast UI grouping
    log_date: str 
    
    # The Telemetry
    is_completed: bool = False     # The "Did I do enough to count it?" toggle
    actual_value: int = 0          # The numeric reality (e.g., 70 or 30)
    notes: str = ""                # Optional context (e.g., "Cut short due to call")
    
# --- 1. THE AGILE ENGINE ---

# --- 1. THE AGILE ENGINE ---

# class LifeEpic(rx.Model, table=True):
#     """The Apex Agile Container. Rolls up time from Projects."""
#     title: str
#     domain: str = "TECH"
#     status: str = "Planning"
#     is_active: bool = True
    
#     estimated_minutes: int = 0
#     manual_time_adjustment_minutes: int = 0
    
#     created_at_local: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# class LifeProject(rx.Model, table=True):
#     """The Mid-Level Container. Rolls up time from Tasks/Subtasks."""
#     epic_id: Optional[int] = Field(default=None, foreign_key="lifeepic.id")
    
#     title: str
#     domain: str = "INBOX"           
#     status: str = "Planning"        
#     target_date: str = ""           
#     is_active: bool = True
    
#     estimated_minutes: int = 0
#     manual_time_adjustment_minutes: int = 0 
    
#     created_at_local: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
# ==========================================
# --- LEVEL 1: THE EPIC ---
# Large, overarching initiatives (e.g., "Home Renovation", "Career Pivot")
# ==========================================
class LifeEpic(TimeTrackableItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    
    projects: List["LifeProject"] = Relationship(back_populates="epic")

# ==========================================
# --- LEVEL 2: THE PROJECT ---
# Scoped deliverables within an Epic (e.g., "Remodel Kitchen")
# ==========================================
class LifeProject(TimeTrackableItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    epic_id: Optional[int] = Field(default=None, foreign_key="lifeepic.id")
    title: str
    description: Optional[str] = None
    
    epic: Optional[LifeEpic] = Relationship(back_populates="projects")
    tasks: List["LifeTask"] = Relationship(back_populates="project")

# ==========================================
# --- LEVEL 3: THE TASK ---
# Actionable, assignable units of work (e.g., "Call plumber for quotes")
# ==========================================
# ==========================================
# --- LEVEL 3: THE TASK ---
# Actionable, assignable units of work (e.g., "Call plumber for quotes")
# ==========================================
class LifeTask(TimeTrackableItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="lifeproject.id")
    
    # --- Core Attributes ---
    title: str
    description: Optional[str] = None
    domain: str = "Home"
    status: str = "Triage"
    priority: str = "Medium"
    
    # --- Temporal Boundaries & Audit ---
    start_date_local: Optional[datetime] = None
    due_date_local: Optional[datetime] = None
    last_modified_local: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # --- Relationships ---
    project: Optional[LifeProject] = Relationship(back_populates="tasks")

class LifeSubtask(rx.Model, table=True):
    """Granular execution. STRICTLY requires a parent Task."""
    task_id: int = Field(foreign_key="lifetask.id") 
    
    title: str
    domain: str = "Home" 
    is_completed: bool = False
    
    estimated_minutes: int = 0
    actual_minutes: int = 0


    
# ------------------------------------------------------------------------------
# ENUMS FOR TYPE SAFETY (The Blueprint Engine)
# ------------------------------------------------------------------------------

class BlueprintType(str, Enum):
    """Defines the payload routing for the factory."""
    TASK = "Task"
    HABIT = "Habit"

class CadenceType(str, Enum):
    """Defines the behavioral trigger for the recurrence."""
    FIXED_CALENDAR = "Fixed_Calendar"
    COMPLETION_BASED = "Completion_Based"

class FrequencyUnit(str, Enum):
    """Granular time units for cadence calculations, optimized for low mental friction."""
    DAYS = "Days"
    WEEKS = "Weeks"
    MONTHS = "Months"
    QUARTERS = "Quarters"
    YEARS = "Years"

# ------------------------------------------------------------------------------
# CORE MODELS
# ------------------------------------------------------------------------------

class LifeBlueprint(SQLModel, table=True):
    """
    The Universal Blueprint Engine (Factory Floor).
    Generates instances of LifeTask or HabitLog based on granular recurrence rules.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    domain: str = "HOME"
    is_active: bool = True
    
    # --- Payload Routing ---
    # Dictates what type of entity this factory mints when triggered.
    target_type: BlueprintType 
    
    # --- The Trigger Engine ---
    cadence_type: CadenceType
    frequency_interval: int          # e.g., "every 2..."
    frequency_unit: FrequencyUnit    # e.g., "...Weeks"
    
    # --- Granular Controls ---
    # Stored as comma-separated string (e.g., "Mon,Wed,Fri") for specific execution days
    specific_days: Optional[str] = None     
    # Target execution time (e.g., "09:00") for time-bound reminders
    specific_time: Optional[str] = None     
    
    # --- The Spawner State ---
    # Tracks the temporal history and upcoming execution requirements
    last_spawned_local: Optional[datetime] = None
    next_spawn_local: Optional[datetime] = None
    # Add this configuration block to tell Pydantic to relax its type checking
    model_config = {
        "arbitrary_types_allowed": True,
        "use_enum_values": True  # <--- This is the magic key for Enums!
    }