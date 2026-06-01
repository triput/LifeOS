"""Base app state with settings loading and seed data."""

import reflex as rx
from sqlmodel import select, SQLModel

from lifeos.models import (
    Settings, Epic, Project, Task, Specialization, Certification
)
from lifeos.utils import today_str


def _ensure_tables():
    """Create all tables if they don't exist."""
    try:
        engine = rx.model.get_engine()
        SQLModel.metadata.create_all(engine)
    except Exception:
        pass


def _seed_database():
    """Insert seed data if the database is empty (Settings row missing)."""
    _ensure_tables()
    with rx.session() as session:
        existing = session.exec(select(Settings)).first()
        if existing is not None:
            return

        # Create default settings
        settings = Settings(
            label_epic="Epic",
            label_project="Project",
            label_task="Task",
            label_subtask="Subtask",
            label_specialization="Specialization",
            label_course="Course",
            label_module="Module",
            habitat_name="Monroe Observatory",
            habitat_location="Monroe, WA",
        )
        session.add(settings)

        # Seed one Epic
        epic = Epic(
            title="Product Launch Q3",
            description="Launch the LifeOS MVP to early users.",
            status="In Progress",
            priority=3,
            domain="Product",
            created_at=today_str(),
        )
        session.add(epic)
        session.commit()
        session.refresh(epic)

        # Seed one Project
        project = Project(
            epic_id=epic.id,
            title="Backend Setup",
            description="Set up Neon PostgreSQL and Reflex backend.",
            status="In Progress",
            priority=3,
            domain="Engineering",
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        # Seed one Task
        task = Task(
            project_id=project.id,
            title="Configure database models",
            description="Define all SQLModel tables.",
            status="Completed",
            priority=2,
            domain="Engineering",
            estimated_minutes=60,
            actual_minutes=45,
        )
        session.add(task)

        # Seed Agentic AI Architectures specialization
        spec = Specialization(
            title="Agentic AI Architectures",
            provider="Coursera / DeepLearning.AI",
            status="In Progress",
            notes="Focus on LLM agents, tool use, and multi-agent systems.",
        )
        session.add(spec)

        # Seed PMP certification
        pmp = Certification(
            title="PMP",
            issuer="PMI",
            status="Active",
            pdus_required=60,
            pdus_completed=12,
            seus_required=0,
            seus_completed=0,
            notes="Renewal due every 3 years. Need 60 PDUs.",
        )
        session.add(pmp)

        # Seed CSM certification
        csm = Certification(
            title="CSM",
            issuer="Scrum Alliance",
            status="Active",
            pdus_required=0,
            pdus_completed=0,
            seus_required=20,
            seus_completed=5,
            notes="Renewal requires 20 SEUs.",
        )
        session.add(csm)

        session.commit()


class AppState(rx.State):
    """Base application state. Loads settings and handles seed data."""

    settings: dict = {}
    _initialized: bool = False

    @rx.event
    async def load_settings(self):
        """Load settings from DB and seed if first run."""
        if not self._initialized:
            _seed_database()
            self._initialized = True

        with rx.session() as session:
            s = session.exec(select(Settings)).first()
            if s:
                self.settings = {
                    "label_epic": s.label_epic,
                    "label_project": s.label_project,
                    "label_task": s.label_task,
                    "label_subtask": s.label_subtask,
                    "label_specialization": s.label_specialization,
                    "label_course": s.label_course,
                    "label_module": s.label_module,
                    "skedpal_webhook_url": s.skedpal_webhook_url,
                    "notion_access_token": s.notion_access_token,
                    "google_calendar_token": s.google_calendar_token,
                    "accent_color": s.accent_color,
                }
            else:
                self.settings = {
                    "label_epic": "Epic",
                    "label_project": "Project",
                    "label_task": "Task",
                    "label_subtask": "Subtask",
                    "label_specialization": "Specialization",
                    "label_course": "Course",
                    "label_module": "Module",
                    "skedpal_webhook_url": "",
                    "notion_access_token": "",
                    "google_calendar_token": "",
                    "accent_color": "teal",
                }

    @rx.event
    async def save_settings(self, form_data: dict):
        """Save settings to DB."""
        with rx.session() as session:
            s = session.exec(select(Settings)).first()
            if not s:
                s = Settings()
                session.add(s)
            s.habitat_name = form_data.get("habitat_name", s.habitat_name)
            s.habitat_location = form_data.get("habitat_location", s.habitat_location)
            s.label_epic = form_data.get("label_epic", s.label_epic)
            s.label_project = form_data.get("label_project", s.label_project)
            s.label_task = form_data.get("label_task", s.label_task)
            s.label_subtask = form_data.get("label_subtask", s.label_subtask)
            s.label_specialization = form_data.get("label_specialization", s.label_specialization)
            s.label_course = form_data.get("label_course", s.label_course)
            s.label_module = form_data.get("label_module", s.label_module)
            s.skedpal_webhook_url = form_data.get("skedpal_webhook_url", s.skedpal_webhook_url)
            s.notion_access_token = form_data.get("notion_access_token", s.notion_access_token)
            s.google_calendar_token = form_data.get("google_calendar_token", s.google_calendar_token)
            s.google_calendar_id = form_data.get("google_calendar_id", s.google_calendar_id)
            s.accent_color = form_data.get("accent_color", s.accent_color)
            session.commit()

        # Reload settings into state
        yield AppState.load_settings
