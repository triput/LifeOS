"""AgendaState — day view with scheduled tasks and due-today list."""

from datetime import date, timedelta
import reflex as rx
from sqlmodel import select

from lifeos.models import Task
from lifeos.state.base_state import AppState
from lifeos.utils import today_str, models_to_dicts


class AgendaState(AppState):
    """State for the Agenda page."""

    selected_date: str = ""
    scheduled_tasks: list[dict] = []
    due_today: list[dict] = []
    all_tasks_for_day: list[dict] = []

    @rx.event
    async def load_agenda(self):
        """Load scheduled and due-today tasks for selected_date."""
        if not self.selected_date:
            self.selected_date = today_str()

        day = self.selected_date

        with rx.session() as session:
            all_tasks = session.exec(select(Task)).all()

        scheduled = []
        due = []
        for t in all_tasks:
            t_dict = {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "domain": t.domain,
                "due_date": t.due_date,
                "scheduled_at": t.scheduled_at,
                "scheduled_duration": t.scheduled_duration,
                "estimated_minutes": t.estimated_minutes,
                "actual_minutes": t.actual_minutes,
                "project_id": t.project_id,
                "notion_url": t.notion_url,
                "notes": t.notes,
            }
            if t.scheduled_at and t.scheduled_at.startswith(day):
                scheduled.append(t_dict)
            elif t.due_date == day and t.status != "Completed":
                due.append(t_dict)

        # Sort scheduled tasks by scheduled_at time
        scheduled.sort(key=lambda x: x.get("scheduled_at") or "")

        self.scheduled_tasks = scheduled
        self.due_today = due

    @rx.event
    async def go_to_today(self):
        """Jump to today."""
        self.selected_date = today_str()
        yield AgendaState.load_agenda

    @rx.event
    async def prev_day(self):
        """Go to the previous day."""
        current = date.fromisoformat(self.selected_date) if self.selected_date else date.today()
        self.selected_date = (current - timedelta(days=1)).isoformat()
        yield AgendaState.load_agenda

    @rx.event
    async def next_day(self):
        """Go to the next day."""
        current = date.fromisoformat(self.selected_date) if self.selected_date else date.today()
        self.selected_date = (current + timedelta(days=1)).isoformat()
        yield AgendaState.load_agenda

    @rx.event
    async def set_date(self, date_str: str):
        """Set a specific date."""
        self.selected_date = date_str
        yield AgendaState.load_agenda

    @rx.event
    async def mark_task_complete(self, task_id: int):
        """Mark a task as completed from the agenda view."""
        with rx.session() as session:
            task = session.get(Task, task_id)
            if task:
                task.status = "Completed"
                session.commit()
        yield AgendaState.load_agenda
