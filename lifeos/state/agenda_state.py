"""AgendaState — day view with scheduled tasks and due-today list."""

from datetime import date, timezone, timedelta
import reflex as rx
from sqlmodel import select
import httpx
import os
import asyncio
from dotenv import load_dotenv

from lifeos.models import Settings
from lifeos.models import Task
from lifeos.state.base_state import AppState
from lifeos.utils import today_str, models_to_dicts


class AgendaState(AppState):
    """State for the Agenda page."""

    selected_date: str = ""
    scheduled_tasks: list[dict] = []
    due_today: list[dict] = []
    all_tasks_for_day: list[dict] = []

# --- New Agnostic Calendar Variables ---
    external_events: list[dict] = []
    calendar_status: str = "Awaiting Sync..."

    @rx.event(background=True)
    async def sync_external_calendar(self):
        """Fetch events from Google Calendar (and eventually Outlook)."""
        load_dotenv()
        api_key = os.environ.get("GOOGLE_CALENDAR_API_KEY", "")
        
        if not api_key:
            async with self:
                self.calendar_status = "Missing API Key in .env"
            return

        # Grab the Calendar ID from the database
        with rx.session() as session:
            settings = session.exec(select(Settings)).first()
            cal_id = settings.google_calendar_id if settings else ""

        if not cal_id:
            async with self:
                self.calendar_status = "No Calendar ID configured in Settings."
            return

        # We want today's events based on the selected_date
        target_date = self.selected_date if self.selected_date else today_str()
        time_min = f"{target_date}T00:00:00Z"
        time_max = f"{target_date}T23:59:59Z"

        # The official Google Calendar v3 REST endpoint
        url = f"https://www.googleapis.com/calendar/v3/calendars/{cal_id}/events?key={api_key}&timeMin={time_min}&timeMax={time_max}&singleEvents=true&orderBy=startTime"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url)

                if resp.status_code == 200:
                    data = resp.json()
                    events = data.get("items", [])
                    
                    formatted_events = []
                    for e in events:
                        # Handle all-day events vs specific time events
                        start_time = e['start'].get('dateTime', e['start'].get('date'))
                        formatted_events.append({
                            "title": e.get("summary", "Busy"),
                            "time": start_time,
                            "source": "Google"
                        })

                    async with self:
                        self.external_events = formatted_events
                        self.calendar_status = "Synced"
                else:
                    async with self:
                        self.calendar_status = f"API Error: {resp.status_code}"
                        
        except Exception as e:
            async with self:
                self.calendar_status = f"Sync Failed: {str(e)}"
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
