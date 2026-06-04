# ==============================================================================
# File: lifeos/state/work_state.py
# Description: Engine for managing work items, hierarchy, and UI state.
# Component: State Engine
# Version: 1.0 (Gold Master)
# Created: 2026-06-01
# Last Update: 2026-06-01
# ==============================================================================

from typing import Optional
import reflex as rx
from sqlmodel import select
import re
from lifeos.utils import parse_time_to_minutes, format_minutes_to_time
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
    
    filter_status: str = "all"
    filter_priority: int = 0
    view_mode: str = "tree"

# --- Item Drawer State ---
    drawer_open: bool = False
    drawer_type: str = ""              # THE FIX: Explicitly declare the type tracker
    drawer_item: dict = {}             # Tracks the actual item being edited
    drawer_staged_children: list[str] = []  # Temporary state for managing child items in the drawer
    drawer_estimated_str: str = ""          # Human-readable string for estimated time
    drawer_actual_str: str = ""             # Human-readable string for actual time
    drawer_adjustment_str: str = ""         # Human-readable string for time adjustment
    drawer_duration_str: str = ""               # Human-readable string for scheduled duration
    drawer_title_str: str = ""
    drawer_description_str: str = ""
    
    
    # Quick-add form
    quick_add_title: str = ""
    quick_add_type: str = "task"
    quick_add_parent_id: str = ""         # For Subtasks (Requires Task ID)
    quick_add_parent_epic_id: str = ""    # For Projects (Optional Epic ID)
    quick_add_parent_project_id: str = "" # For Tasks (Optional Project ID)

    # Notification
    toast_message: str = ""
    
    # --- Relational Context State ---
    drawer_parent: dict = {}
    drawer_children: list[dict] = []
    drawer_new_child_title: str = ""

    # --- Feed Sorting State ---
    feed_sort_order: str = "recent"  # Options: 'recent', 'priority', 'status', 'due_date'
    
    # --- Feed Filtering State ---
    hidden_statuses: list[str] = []
    hidden_priorities: list[int] = []  # Assuming 1=High, 2=Normal, 3=Low
    
    
    @rx.event
    def toggle_status_filter(self, status: str, show: bool):
        """If show is False (unchecked), add to hidden. If True, remove."""
        if not show and status not in self.hidden_statuses:
            self.hidden_statuses.append(status)
        elif show and status in self.hidden_statuses:
            self.hidden_statuses.remove(status)
        yield WorkState.load_work

    @rx.event
    def toggle_priority_filter(self, priority: int, show: bool):
        """If show is False (unchecked), add to hidden. If True, remove."""
        if not show and priority not in self.hidden_priorities:
            self.hidden_priorities.append(priority)
        elif show and priority in self.hidden_priorities:
            self.hidden_priorities.remove(priority)
        yield WorkState.load_work
    
    @rx.event
    def set_drawer_title_str(self, value: str):
        self.drawer_title_str = value

    @rx.event
    def set_drawer_description_str(self, value: str):
        self.drawer_description_str = value
    
    @rx.event
    def set_drawer_duration_str(self, value: str):
        """Update the human-readable scheduled duration string."""
        self.drawer_duration_str = value
        
    @rx.event
    def set_drawer_estimated_str(self, value: str):
        """Update the human-readable estimated time string."""
        self.drawer_estimated_str = value
        
    @rx.event
    def set_drawer_actual_str(self, value: str):
        """Update the human-readable actual time string."""
        self.drawer_actual_str = value
        
    @rx.event
    def set_drawer_adjustment_str(self, value: str):
        """Update the human-readable time adjustment string."""
        self.drawer_adjustment_str = value
    
    @rx.event
    def set_drawer_new_child_title(self, value: str):
        """Explicit manual setter to bypass framework auto-generation failures."""
        self.drawer_new_child_title = value

    @rx.event
    def set_feed_sort_order(self, order: str):
        """Update the sort order and reload the work lists."""
        self.feed_sort_order = order
        yield WorkState.load_work
    
    @rx.event
    async def handle_key_down(self, key: str):
        """Native Reflex handler for keyboard events."""
        if key == "Enter":
            yield WorkState.quick_add_submit

    @rx.event
    async def load_work(self):
        """Load all work data from the database."""
        with rx.session() as session:
            tasks_query = select(Task)
            
            # --- THE NEW FILTER LOGIC ---
            if self.hidden_statuses:
                tasks_query = tasks_query.where(Task.status.notin_(self.hidden_statuses))
                
            if self.hidden_priorities:
                tasks_query = tasks_query.where(Task.priority.notin_(self.hidden_priorities))

            
            # --- THE NEW SORTING LOGIC ---
            if self.feed_sort_order == "priority":
                tasks_query = tasks_query.order_by(Task.priority)
            elif self.feed_sort_order == "status":
                tasks_query = tasks_query.order_by(Task.status)
            elif self.feed_sort_order == "due_date":
                # Sort ascending so the most urgent/closest dates appear at the top
                tasks_query = tasks_query.order_by(Task.due_date) 
            else:
                # THE FIX: Use the primary key ID to determine what is most recent!
                tasks_query = tasks_query.order_by(Task.id.desc())
                
# 1. Update the Tasks serialization at the bottom of your sorting block:
            raw_tasks = session.exec(tasks_query).all()
            rich_tasks = []
            for task in raw_tasks:
                task_dict = task.model_dump()  # Start with the basic fields from the model
                
            # 1. Inject Formatted Time Strings
            task_dict["estimated_str"] = format_minutes_to_time(getattr(task, "estimated_minutes", 0))
            task_dict["actual_str"] = format_minutes_to_time(getattr(task, "actual_minutes", 0))
            
            # 2. Inject Parent Context (Looking UP)
            parent_title = ""
            # Assuming Task belongs to Project, Project belongs to Epic, etc.
            if hasattr(task, "project_id") and task.project_id:
                parent = session.get(Project, task.project_id)
                if parent: parent_title = parent.title
            elif hasattr(task, "epic_id") and task.epic_id:
                parent = session.get(Epic, task.epic_id)
                if parent: parent_title = parent.title
                
            task_dict["parent_title"] = parent_title
            
            rich_tasks.append(task_dict)
            
            # Assign the enriched list to your state variable
            self.tasks = rich_tasks
            # 2. Update the other lists (if you added them):
            self.epics = [epic.model_dump() for epic in session.exec(select(Epic)).all()]
            self.projects = [proj.model_dump() for proj in session.exec(select(Project)).all()]
            self.subtasks = [sub.model_dump() for sub in session.exec(select(Subtask)).all()]

    @rx.event
    def delete_drawer_item(self):
        """Deletes the currently opened item and closes the drawer."""
        if not self.drawer_item or not self.drawer_type:
            return
            
        with rx.session() as session:
            model_map = {"epic": Epic, "project": Project, "task": Task, "subtask": Subtask}
            model = model_map.get(self.drawer_type)
            
            if model:
                db_item = session.get(model, self.drawer_item["id"])
                if db_item:
                    session.delete(db_item)
                    session.commit()
                    
        self.drawer_open = False
        yield WorkState.load_work


    @rx.event
    async def open_drawer(self, item_type: str, item_id: int):
        """Open the drawer and load all relational context."""
        self.drawer_type = item_type
        self.drawer_open = True
        
        # Reset context on open
        self.drawer_parent = {}
        self.drawer_children = []
        self.drawer_new_child_title = ""
        
        with rx.session() as session:
            # 1. Fetch the main item (Make sure you are querying the right SQLModel class!)
            if item_type == "epic": item = session.get(Epic, item_id)
            elif item_type == "project": item = session.get(Project, item_id)
            elif item_type == "task": item = session.get(Task, item_id)
            elif item_type == "subtask": item = session.get(Subtask, item_id)
            else: return

            if not item: return
            self.drawer_item = item.model_dump()
            self.drawer_estimated_str = format_minutes_to_time(item.estimated_minutes)
            self.drawer_actual_str = format_minutes_to_time(item.actual_minutes)
            self.drawer_adjustment_str = format_minutes_to_time(item.time_adjustment)
            self.drawer_title_str = getattr(item, "title", "") or ""
            self.drawer_description_str = getattr(item, "description", "") or ""
            
            self.drawer_staged_children = []  # Clear any previously staged children when opening a new drawer
            
            # 2. Fetch the Parent (Looking UP)
            if item_type == "project" and getattr(item, "epic_id", None):
                parent = session.get(Epic, item.epic_id)
                if parent: self.drawer_parent = {"id": parent.id, "title": parent.title, "type": "epic"}
            
            elif item_type == "task" and getattr(item, "project_id", None):
                parent = session.get(Project, item.project_id)
                if parent: self.drawer_parent = {"id": parent.id, "title": parent.title, "type": "project"}
                
            elif item_type == "subtask" and getattr(item, "task_id", None):
                parent = session.get(Task, item.task_id)
                if parent: self.drawer_parent = {"id": parent.id, "title": parent.title, "type": "task"}

            # 3. Fetch the Children (Looking DOWN)
            if item_type == "epic":
                kids = session.exec(select(Project).where(Project.epic_id == item.id)).all()
                self.drawer_children = [{"id": k.id, "title": k.title, "status": k.status, "type": "project"} for k in kids]
                
            elif item_type == "project":
                kids = session.exec(select(Task).where(Task.project_id == item.id)).all()
                self.drawer_children = [{"id": k.id, "title": k.title, "status": k.status, "type": "task"} for k in kids]
                
            elif item_type == "task":
                kids = session.exec(select(Subtask).where(Subtask.task_id == item.id)).all()
                # Using getattr in case your subtasks don't use statuses
                self.drawer_children = [{"id": k.id, "title": k.title, "status": getattr(k, "status", "In Progress"), "type": "subtask"} for k in kids]

    # --- 4. STAGED CHILDREN METHODS ---
    @rx.event
    def stage_new_child(self):
        """Instantly add a child to the local staging queue without DB lag."""
        if self.drawer_new_child_title.strip():
            self.drawer_staged_children.append(self.drawer_new_child_title.strip())
            self.drawer_new_child_title = ""

    @rx.event
    def remove_staged_child(self, index: int):
        """Remove an item from the staging queue."""
        self.drawer_staged_children.pop(index)

    @rx.event
    async def commit_staged_children(self):
        """Batch save all staged children to the database."""
        if not self.drawer_staged_children: return
        
        parent_id = self.drawer_item["id"]
        
        with rx.session() as session:
            for title in self.drawer_staged_children:
                if self.drawer_type == "epic":
                    session.add(Project(title=title, epic_id=parent_id, status="In Progress", priority=3))
                elif self.drawer_type == "project":
                    session.add(Task(title=title, project_id=parent_id, status="In Progress", priority=3))
                elif self.drawer_type == "task":
                    session.add(Subtask(title=title, task_id=parent_id))
            session.commit()
            
        self.drawer_staged_children = []
        
        # Refresh the UI once after the batch
        yield WorkState.open_drawer(self.drawer_type, parent_id)
        yield WorkState.load_work
        
    @rx.event
    async def quick_add_drawer_child(self):
        """Bonus: Rapidly add a child item directly from the parent's drawer."""
        if not self.drawer_new_child_title.strip():
            return
            
        parent_id = self.drawer_item["id"]
        
        with rx.session() as session:
            if self.drawer_type == "epic":
                new_item = Project(title=self.drawer_new_child_title, epic_id=parent_id, status="In Progress", priority=3)
            elif self.drawer_type == "project":
                new_item = Task(title=self.drawer_new_child_title, project_id=parent_id, status="In Progress", priority=3)
            elif self.drawer_type == "task":
                new_item = Subtask(title=self.drawer_new_child_title, task_id=parent_id)
            else:
                return # Subtasks don't have children
                
            session.add(new_item)
            session.commit()
            
        # Clear the input
        self.drawer_new_child_title = ""
        
        # Refresh the drawer context and main dashboard lists simultaneously
        yield WorkState.open_drawer(self.drawer_type, parent_id)
        yield WorkState.load_work   


    @rx.event
    async def open_new_drawer(self, item_type: str, parent_id: int = 0):
        """Open drawer to create a new item."""
        self.selected_type = item_type
        self.selected_item = {
            "id": None,
            "title": "",
            "description": "",
            "status": "In Progress",
            "priority": 3,
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
        item_id.title = self.drawer_title_str
        item_id.description = self.drawer_description_str

        # Parse minute fields from human-readable strings
        for field in ["estimated_minutes", "actual_minutes", "time_adjustment, scheduled_duration"]:
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
                est_min = form_data.get("estimated_minutes")
                item.estimated_minutes = parse_time_to_minutes(est_min) if est_min else None
                act_min = form_data.get("actual_minutes")
                item.actual_minutes = parse_time_to_minutes(act_min) if act_min else None
                time_adj = form_data.get("time_adjustment")
                item.time_adjustment = parse_time_to_minutes(time_adj)
                item.due_date = form_data.get("due_date") or None
                item.scheduled_at = form_data.get("scheduled_at") or None
                sched_dur = form_data.get("scheduled_duration")
                item.scheduled_duration = parse_time_to_minutes(sched_dur) if sched_dur else None
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
            
            # --- THE TIME PARSING BRIDGE ---
            # Translate the human strings back into machine minutes before saving
            
            # if hasattr(form_data, "estimated_minutes"):
            #     form_data.estimated_minutes = parse_time_to_minutes(self.drawer_estimated_str)
                
            # if hasattr(form_data, "actual_minutes"):
            #     form_data.actual_minutes = parse_time_to_minutes(self.drawer_actual_str)
                
            # if hasattr(form_data, "scheduled_duration"):
            #     # Make sure to use your exact column name here!
            #     form_data.scheduled_duration = parse_time_to_minutes(self.drawer_duration_str)
                
            # if hasattr(form_data, "time_adjustment"):
            #     form_data.time_adjustment = parse_time_to_minutes(self.drawer_adjustment_str)

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
    def set_quick_add_parent_id(self, value: str):
        self.quick_add_parent_id = value

    @rx.event
    def set_quick_add_parent_epic_id(self, value: str):
        self.quick_add_parent_epic_id = value

    @rx.event
    def set_quick_add_parent_project_id(self, value: str):
        self.quick_add_parent_project_id = value
        
    @rx.event
    def set_quick_add_type(self, value: str):
        """Update the quick add dropdown selection."""
        self.quick_add_type = value
# --- KPI Drawer State ---
    kpi_drawer_open: bool = False
    kpi_drawer_type: str = "tasks" # Tracks which list to display

    @rx.event
    def open_kpi_drawer(self, item_type: str):
        """Slide open the interactive KPI list."""
        self.kpi_drawer_type = item_type
        self.kpi_drawer_open = True

    @rx.event
    def close_kpi_drawer(self):
        """Close the KPI list."""
        self.kpi_drawer_open = False

    @rx.event
    def handle_kpi_drawer_change(self, is_open: bool):
        """Explicitly manage the KPI drawer state to prevent UI desync."""
        self.kpi_drawer_open = is_open

    @rx.event
    async def toggle_drawer_child(self, is_checked: bool, child_id: int, child_type: str):
        """Explicitly toggles a child item's status directly from the checkbox payload."""
        new_status = "Completed" if is_checked else "In Progress"
        
        with rx.session() as session:
            model_map = {"epic": Project, "project": Task, "task": Subtask}
            model = model_map.get(child_type)
            
            if model:
                db_item = session.get(model, child_id)
                if db_item:
                    # Subtasks might not have a status column depending on your schema
                    if hasattr(db_item, "status"):
                        db_item.status = new_status
                    session.add(db_item)
                    session.commit()
                    
        yield WorkState.load_work
        yield WorkState.open_drawer(self.drawer_type, self.drawer_item["id"])

    @rx.event
    async def fast_complete_item(self, item_id: int, item_type: str):
        """Instantly mark an item as Completed from the KPI drawer."""
        with rx.session() as session:
            if item_type == "epics":
                item = session.get(Epic, item_id)
            elif item_type == "projects":
                item = session.get(Project, item_id)
            elif item_type == "tasks":
                item = session.get(Task, item_id)
            elif item_type == "subtasks":
                item = session.get(Subtask, item_id)
                
            if item:
                # If it's already completed, un-check it. Otherwise, mark it done.
                if hasattr(item, "status"):
                    item.status = "In Progress" if item.status == "Completed" else "Completed"
                session.add(item)
                session.commit()
                
        # Reload the data so the UI updates instantly
        yield WorkState.load_work
        
        # THE FIX: Also reload the drawer if it's currently open!
        if self.drawer_open and self.drawer_item:
            yield WorkState.open_drawer(self.drawer_type, self.drawer_item["id"])
            
    @rx.event
    async def quick_add_submit(self):
        """Dynamically add an item based on the selected quick-add type."""
        if not self.quick_add_title.strip():
            return
            
        with rx.session() as session:
            title = self.quick_add_title.strip()
            
            if self.quick_add_type == "epic":
                item = Epic(title=title, status="In Progress", priority=3, created_at=today_str())
            
            elif self.quick_add_type == "project":
                # Check for optional parent epic
                if self.quick_add_parent_epic_id and self.quick_add_parent_epic_id != "":
                    item = Project(title=title, epic_id=int(self.quick_add_parent_epic_id), status="In Progress", priority=3)
                else:
                    item = Project(title=title, status="In Progress", priority=3)
            
            elif self.quick_add_type == "task":
                # Check for optional parent project
                if self.quick_add_parent_project_id and self.quick_add_parent_project_id != "":
                    item = Task(title=title, project_id=int(self.quick_add_parent_project_id), status="In Progress", priority=3)
                else:
                    item = Task(title=title, status="In Progress", priority=3)
            
            elif self.quick_add_type == "subtask":
                # Required parent task
                if self.quick_add_parent_id and self.quick_add_parent_id != "":
                    item = Subtask(title=title, task_id=int(self.quick_add_parent_id))
                else:
                    print("Habitat Error: Subtasks require a parent task selection.")
                    return
                
            session.add(item)
            session.commit()
            
        # Explicitly clear all inputs and dropdowns so the UI resets
        self.quick_add_title = ""
        self.quick_add_parent_id = ""
        self.quick_add_parent_epic_id = ""
        self.quick_add_parent_project_id = ""
        
        yield WorkState.load_work
        
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
                priority=3,
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
                priority=3,
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
                priority=3,
            )
            session.add(task)
            session.commit()
        yield WorkState.load_work
