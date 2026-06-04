"""Database models for LifeOS using SQLModel directly."""

from typing import Optional
from sqlmodel import Field, SQLModel


# ---------------------------------------------------------------------------
# Work Track
# ---------------------------------------------------------------------------

class Epic(SQLModel, table=True):
    """Top-level work container."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    status: str = "In Progress"  # In Progress, Completed, On Hold, Cancelled
    priority: int = 2             # 1=Low, 2=Normal, 3=High, 4=Critical
    domain: str = ""
    notion_url: str = ""
    notes: str = ""
    estimated_minutes: int = 0
    actual_minutes: int = 0
    time_adjustment: int = 0
    created_at: str = ""          # ISO date string


class Project(SQLModel, table=True):
    """Project within an Epic."""
    id: Optional[int] = Field(default=None, primary_key=True)
    epic_id: Optional[int] = Field(default=None)
    title: str
    description: str = ""
    status: str = "In Progress"
    priority: int = 2
    domain: str = ""
    notion_url: str = ""
    notes: str = ""
    estimated_minutes: int = 0
    actual_minutes: int = 0
    time_adjustment: int = 0
    due_date: Optional[str] = Field(default=None)


class Task(SQLModel, table=True):
    """Task within a Project."""
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None)
    title: str
    description: str = ""
    status: str = "In Progress"
    priority: int = 2
    domain: str = ""
    notion_url: str = ""
    notes: str = ""
    estimated_minutes: int = 0
    actual_minutes: int = 0
    time_adjustment: int = 0
    due_date: Optional[str] = Field(default=None)
    scheduled_at: Optional[str] = Field(default=None)
    scheduled_duration: Optional[int] = Field(default=None)


class Subtask(SQLModel, table=True):
    """Subtask within a Task."""
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int
    title: str
    is_completed: bool = False
    estimated_minutes: int = 0
    actual_minutes: int = 0


# ---------------------------------------------------------------------------
# Academy Track
# ---------------------------------------------------------------------------

class Specialization(SQLModel, table=True):
    """Top-level learning path / specialization."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = Field(default="")
    provider: str = ""
    status: str = "In Progress"
    notion_url: str = ""
    notes: str = ""


class Course(SQLModel, table=True):
    """Course within a Specialization."""
    id: Optional[int] = Field(default=None, primary_key=True)
    specialization_id: Optional[int] = Field(default=None)
    title: str
    description: Optional[str] = Field(default="")
    provider: str = ""
    status: str = "Planned"
    notion_url: str = ""
    notes: str = ""


class Module(SQLModel, table=True):
    """Module within a Course."""
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int
    title: str
    description: Optional[str] = Field(default="")
    status: str = "Planned"
    notes: str = ""
    notion_url: str = ""
    order_index: int = 0


class LearningTask(SQLModel, table=True):
    """Learning task / lesson within a Module."""
    id: Optional[int] = Field(default=None, primary_key=True)
    module_id: int
    title: str
    description: Optional[str] = Field(default="")
    activity_type: str = "Video"  # Video, Quiz, Reading, Exercise, Project
    is_completed: bool = False
    estimated_minutes: int = 15
    actual_minutes: int = 0
    notes: str = ""
    notion_url: str = ""


class Certification(SQLModel, table=True):
    """Professional certification with PDU/SEU tracking."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    issuer: str = ""
    issue_date: Optional[str] = Field(default=None)
    next_renewal_date: Optional[str] = Field(default=None)
    status: str = "Active"        # Active, Expired, In Progress
    pdus_required: int = 0
    pdus_completed: int = 0
    seus_required: int = 0
    seus_completed: int = 0
    notes: str = ""


# ---------------------------------------------------------------------------
# Settings (single-row table, id=1)
# ---------------------------------------------------------------------------

class Settings(SQLModel, table=True):
    """App settings — only one row with id=1."""
    id: Optional[int] = Field(default=None, primary_key=True)
    # Label customization
    label_epic: str = "Epic"
    label_project: str = "Project"
    label_task: str = "Task"
    label_subtask: str = "Subtask"
    label_specialization: str = "Specialization"
    label_course: str = "Course"
    label_module: str = "Module"
    # Integrations
    skedpal_webhook_url: str = ""
    notion_access_token: str = ""
    google_calendar_token: str = ""
    google_calendar_id: str = ""
    # Theme accent
    accent_color: str = "teal"
    # Habitat
    habitat_name: str = "Monroe Observatory"
    habitat_location: str = "Monroe, WA"