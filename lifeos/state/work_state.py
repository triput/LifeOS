"""WorkState — manages Epics, Projects, Tasks, and Subtasks."""

from typing import Optional
import reflex as rx
from sqlmodel import select

from lifeos.models import Epic, Project, Task, Subtask
from lifeos.state.base_state import AppState
from lifeos.utils import today_str, model_to_dict, models_to_dicts, parse_mins


class WorkState(AppState):
    """State for the Work track."""

    epics: list[dict] = []
    projects: list[dict] = []
    tasks: list[dict] = []
    subtasks: list[dict] = []

    selected_item: dict = {}
    selected_type: str = "task"
    drawer_open: bool = False

    filter_status: str = "all"
    filter_priority: int = 0
    view_mode: str = "tree"

    # Quick-add form
    quick_add_title: str = ""
    quick_add_type: str = "task"
    quick_add_parent_id: int = 0

    # Notification
    toast_message: str = ""

    @rx.event
    async def load_work(self):
        """Load all work data from the database."""
        with rx.session() as session:
            self.epics = models_to_dicts(session.exec(select(Epic)).all())
            self.projects = models_to_dicts(session.exec(select(Project)).all())
            self.tasks = models_to_dicts(session.exec(select(Task)).all())
            self.subtasks = models_to_dicts(session.exec(select(Subtask)).all())

    @rx.event
    async def open_drawer(self, item_type: str, item_id: int):
        """Open the edit drawer for a specific item."""
        self.selected_type = item_type
        with rx.session() as session:
            if item_type == "epic":
                item = session.get(Epic, item_id)
            elif item_type == "project":
                item = session.get(Project, item_id)
            elif item_type == "task":
                item = session.get(Task, item_id)
            elif item_type == "subtask":
                item = session.get(Subtask, item_id)
            else:
                item = None

            if item:
                self.selected_item = model_to_dict(item)
            else:
                self.selected_item = {}

        self.drawer_open = True

    @rx.event
    async def open_new_drawer(self, item_type: str, parent_id: int = 0):
        """Open drawer to create a new item."""
        self.selected_type = item_type
        self.selected_item = {
            "id": None,
            "title": "",
            "description": "",
            "status": "In Progress",
            "priority": 2,
            "domain": "",
            "notion_url": "",
            "notes": "",
            "estimated_minutes": 0,
            "actual_minutes": 0,
            "time_adjustment": 0,
            "due_date": "",
        }
        if item_type == "project":
            self.selected_item["epic_id"] = parent_id
        elif item_type == "task":
            self.selected_item["project_id"] = parent_id
        elif item_type == "subtask":
            self.selected_item["task_id"] = parent_id
            self.selected_item["is_completed"] = False

        self.drawer_open = True

    @rx.event
    async def close_drawer(self):
        """Close the edit drawer."""
        self.drawer_open = False
        self.selected_item = {}

    @rx.event
    async def save_item(self, form_data: dict):
        """Upsert the selected item based on selected_type."""
        item_id = self.selected_item.get("id")
        itype = self.selected_type

        # Parse minute fields from human-readable strings
        for field in ["estimated_minutes", "actual_minutes", "time_adjustment"]:
            if field in form_data:
                form_data[field] = parse_mins(str(form_data.get(field, 0)))

        with rx.session() as session:
            if itype == "epic":
                if item_id:
                    item = session.get(Epic, item_id)
                else:
                    item = Epic(title="", created_at=today_str())
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.description = form_data.get("description", item.description)
                item.status = form_data.get("status", item.status)
                item.priority = int(form_data.get("priority", item.priority))
                item.domain = form_data.get("domain", item.domain)
                item.notion_url = form_data.get("notion_url", item.notion_url)
                item.notes = form_data.get("notes", item.notes)
                item.estimated_minutes = form_data.get("estimated_minutes", item.estimated_minutes)
                item.actual_minutes = form_data.get("actual_minutes", item.actual_minutes)
                item.time_adjustment = form_data.get("time_adjustment", item.time_adjustment)

            elif itype == "project":
                if item_id:
                    item = session.get(Project, item_id)
                else:
                    item = Project(title="")
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.description = form_data.get("description", item.description)
                item.status = form_data.get("status", item.status)
                item.priority = int(form_data.get("priority", item.priority))
                item.domain = form_data.get("domain", item.domain)
                item.notion_url = form_data.get("notion_url", item.notion_url)
                item.notes = form_data.get("notes", item.notes)
                item.estimated_minutes = form_data.get("estimated_minutes", item.estimated_minutes)
                item.actual_minutes = form_data.get("actual_minutes", item.actual_minutes)
                item.time_adjustment = form_data.get("time_adjustment", item.time_adjustment)
                item.due_date = form_data.get("due_date") or None
                epic_id = form_data.get("epic_id")
                if epic_id:
                    item.epic_id = int(epic_id)

            elif itype == "task":
                if item_id:
                    item = session.get(Task, item_id)
                else:
                    item = Task(title="")
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.description = form_data.get("description", item.description)
                item.status = form_data.get("status", item.status)
                item.priority = int(form_data.get("priority", item.priority))
                item.domain = form_data.get("domain", item.domain)
                item.notion_url = form_data.get("notion_url", item.notion_url)
                item.notes = form_data.get("notes", item.notes)
                item.estimated_minutes = form_data.get("estimated_minutes", item.estimated_minutes)
                item.actual_minutes = form_data.get("actual_minutes", item.actual_minutes)
                item.time_adjustment = form_data.get("time_adjustment", item.time_adjustment)
                item.due_date = form_data.get("due_date") or None
                item.scheduled_at = form_data.get("scheduled_at") or None
                sched_dur = form_data.get("scheduled_duration")
                item.scheduled_duration = int(sched_dur) if sched_dur else None
                project_id = form_data.get("project_id")
                if project_id:
                    item.project_id = int(project_id)

            elif itype == "subtask":
                if item_id:
                    item = session.get(Subtask, item_id)
                else:
                    task_id = self.selected_item.get("task_id", 0)
                    item = Subtask(task_id=task_id, title="")
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.is_completed = form_data.get("is_completed", item.is_completed)
                item.estimated_minutes = form_data.get("estimated_minutes", item.estimated_minutes)
                item.actual_minutes = form_data.get("actual_minutes", item.actual_minutes)
            else:
                return

            session.commit()

        self.drawer_open = False
        yield WorkState.load_work

    @rx.event
    async def delete_item(self):
        """Delete the currently selected item."""
        item_id = self.selected_item.get("id")
        itype = self.selected_type

        if not item_id:
            self.drawer_open = False
            return

        with rx.session() as session:
            if itype == "epic":
                item = session.get(Epic, item_id)
            elif itype == "project":
                item = session.get(Project, item_id)
            elif itype == "task":
                item = session.get(Task, item_id)
            elif itype == "subtask":
                item = session.get(Subtask, item_id)
            else:
                item = None

            if item:
                session.delete(item)
                session.commit()

        self.drawer_open = False
        yield WorkState.load_work

    @rx.event
    async def toggle_subtask(self, subtask_id: int):
        """Toggle subtask completion status."""
        with rx.session() as session:
            subtask = session.get(Subtask, subtask_id)
            if subtask:
                subtask.is_completed = not subtask.is_completed
                session.commit()

        yield WorkState.load_work

    @rx.event
    async def set_filter_status(self, value: str):
        self.filter_status = value if value else "all"

    @rx.event
    async def set_filter_priority(self, value: str):
        self.filter_priority = int(value) if value else 0

    @rx.event
    async def set_view_mode(self, mode: str):
        self.view_mode = mode

    @rx.event
    async def set_quick_add_title(self, value: str):
        self.quick_add_title = value

    @rx.event
    async def quick_add_epic(self):
        """Quickly add a new Epic with minimal info."""
        if not self.quick_add_title.strip():
            return
        with rx.session() as session:
            epic = Epic(
                title=self.quick_add_title.strip(),
                status="In Progress",
                priority=2,
                created_at=today_str(),
            )
            session.add(epic)
            session.commit()
        self.quick_add_title = ""
        yield WorkState.load_work

    @rx.event
    async def add_project_to_epic(self, epic_id: int, title: str):
        """Add a project to an epic."""
        if not title.strip():
            return
        with rx.session() as session:
            project = Project(
                epic_id=epic_id,
                title=title.strip(),
                status="In Progress",
                priority=2,
            )
            session.add(project)
            session.commit()
        yield WorkState.load_work

    @rx.event
    async def add_task_to_project(self, project_id: int, title: str):
        """Add a task to a project."""
        if not title.strip():
            return
        with rx.session() as session:
            task = Task(
                project_id=project_id,
                title=title.strip(),
                status="In Progress",
                priority=2,
            )
            session.add(task)
            session.commit()
        yield WorkState.load_work
