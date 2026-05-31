# ==============================================================================
# File: lifeos/states/management.py
# Description: State engine for the Triage Inbox and Backlog Grooming.
# Component: State Layer
# ==============================================================================

import reflex as rx
import re
from sqlmodel import select
from lifeos.models.habitat import LifeEpic, LifeProject, LifeTask
from lifeos.utils.conversions import parse_human_time, format_human_time
from pydantic import BaseModel

LIFE_DOMAINS = ["Health", "Career", "Academy", "Operations", "Joy", "Unassigned"]


class NestedTaskItem(BaseModel):
    id: str
    title: str
    order_index: int

class ActiveProjectItem(BaseModel):
    id: str
    title: str
    status: str
    tasks: list[NestedTaskItem]
class ManagementState(rx.State):
    # --- RAPID CAPTURE FORM ---
    new_item_title: str = ""
    new_item_type: str = "Task"
    new_item_priority: str = "Medium"

    # Defensive Setters
    def set_new_item_title(self, value: str): self.new_item_title = value
    def set_new_item_type(self, value: str): self.new_item_type = value
    def set_new_item_priority(self, value: str): self.new_item_priority = value
    
        # --- Focus Mode Filter ---
    active_filter: str = "All"

    def set_active_filter(self, domain: str):
        """Updates the focus mode and immediately refetches the board."""
        self.active_filter = domain
        self.load_backlog()  # This instantly applies the filter!


    # --- UI DATA LISTS ---
    # We use simple lists of dictionaries so the UI can easily render them
    raw_inbox_tasks: list[dict] = []
    active_projects: list[ActiveProjectItem] = []
    active_epics: list[dict] = []
    
    # --- Epic Routing Variables ---
    draft_epic_title: str = "Unassigned"
    capture_epic_title: str = "Unassigned"
    
    # --- Explicit Setters ---
    def set_draft_epic_title(self, title: str):
        self.draft_epic_title = title

    def set_capture_epic_title(self, title: str):
        self.capture_epic_title = title
    
    # --- NEW: Computed Variable ---
    
    
    @rx.var
    def active_project_titles(self) -> list[str]:
        """Automatically extracts a clean list of strings for UI dropdowns."""
        return [p.title for p in self.active_projects]
    
    # --- UI Dropdown List ---
    @rx.var
    def active_epic_titles(self) -> list[str]:
        """Provides a list of Epic titles for the UI dropdowns."""
        with rx.session() as session:
            from sqlmodel import select
            # Note: adjust the import or class name if your Epic class is named differently
            epics = session.exec(select(LifeEpic)).all()
            return ["Unassigned"] + [e.title for e in epics]
    

    def load_backlog(self):
        """Fetches all non-archived items from the database."""
        with rx.session() as session:
            from sqlmodel import select
            # --- NEW: The Auto-Healer ---
            legacy_tasks = session.exec(select(LifeTask).where(LifeTask.order_index == 0)).all()
            for t in legacy_tasks:
                # --- NEW: The Filter Engine Bypass ---
                if self.active_filter != "All" and getattr(t, "domain", "Unassigned") != self.active_filter:
                    continue  # Skip this task! Don't put it on the board!
                if t.id:
                    t.order_index = int(t.id) * 10
                    session.add(t)
            if legacy_tasks:
                session.commit()
            # ----------------------------
            # 1. Fetch unassigned Tasks (Triage items)
            tasks = session.exec(select(LifeTask).where(LifeTask.is_archived == False)).all()
            self.raw_inbox_tasks = [{"id": str(t.id), "title": t.title, "priority": t.priority, "status": t.status} for t in tasks]

            # 2. Fetch Projects
            projects = session.exec(select(LifeProject).where(LifeProject.is_archived == False)).all()
            self.active_projects = []
            
            for p in projects:
                # --- NEW: The Filter Engine Bypass ---
                if self.active_filter != "All" and getattr(p, "domain", "Unassigned") != self.active_filter:
                    continue  # Skip this task! Don't put it on the board!
                p_tasks = session.exec(
                    select(LifeTask)
                    .where(LifeTask.project_id == p.id, LifeTask.is_archived == False)
                    .order_by(LifeTask.order_index.asc())
                ).all()
                
                # Map them into our new strict rx.Base objects!
                task_list = [NestedTaskItem(id=str(t.id), title=t.title, order_index=t.order_index) for t in p_tasks]
                
                self.active_projects.append(
                    ActiveProjectItem(
                        id=str(p.id),
                        title=p.title,
                        status=p.status,
                        tasks=task_list
                    )
                )
            # 3. Fetch Epics
            epics = session.exec(select(LifeEpic).where(LifeEpic.is_archived == False)).all()
            self.active_epics = [{"id": str(e.id), "title": e.title, "priority": e.priority, "status": e.status} for e in epics]

    def capture_triage_item(self):
        """Saves the input bar data to the correct database table."""
        if not self.new_item_title.strip():
            return

        with rx.session() as session:
            if self.new_item_type == "Epic":
                new_item = LifeEpic(title=self.new_item_title, priority=self.new_item_priority)
            elif self.new_item_type == "Project":
                new_item = LifeProject(title=self.new_item_title, priority=self.new_item_priority)
            else:
                new_item = LifeTask(title=self.new_item_title, priority=self.new_item_priority)
            
            session.add(new_item)
            session.commit()

        # Clear the input bar and refresh the lists
        self.new_item_title = ""
        self.load_backlog()
        
    # ==========================================
    # --- TASK ASSIGNMENT STATE ---
    # ==========================================
    assignment_modal_open: bool = False
    active_task_id: str = ""
    target_project_id: str = ""

    def set_target_project_id(self, value: str): 
        self.target_project_id = value

    def open_assignment_modal(self, task_id: str):
        """Triggers when you click the arrow on an inbox task."""
        self.active_task_id = str(task_id)
        self.target_project_id = "" # Reset the dropdown
        self.assignment_modal_open = True

    def close_assignment_modal(self):
        self.assignment_modal_open = False

    def assign_task_to_project(self):
        """Updates the database to link the task to the chosen project."""
        if not self.target_project_id:
            return

        with rx.session() as session:
            from sqlmodel import select
            
            # 1. Reverse-lookup: Find the actual Project record using the Title from the dropdown
            target_proj = session.exec(
                select(LifeProject).where(LifeProject.title == self.target_project_id)
            ).first()
            
            if target_proj:
                # 2. Fetch the specific task we want to move
                task = session.get(LifeTask, int(self.active_task_id))
                
                if task:
                    # 3. Assign the correct INTEGER ID to the task
                    task.project_id = target_proj.id
                    
                    # 4. Give it a valid order_index so it doesn't break our new sorting arrows!
                    if task.order_index == 0:
                        task.order_index = int(task.id) * 10
                        
                    session.add(task)
                    session.commit()
                
        # 5. Refresh the UI lists
        self.load_backlog()
        self.close_assignment_modal()
        
    # -- Task Arranging
    def move_task_up(self, task_id: str):
        self._swap_task_order(int(task_id), "up")

    def move_task_down(self, task_id: str):
        self._swap_task_order(int(task_id), "down")

    def _swap_task_order(self, task_id: int, direction: str):
        """Swaps the order_index of a task with its immediate neighbor."""
        with rx.session() as session:
            from sqlmodel import select, col
            
            task = session.get(LifeTask, task_id)
            if not task or not task.project_id:
                return

            # Find the neighbor to swap with
            if direction == "up":
                # Find the task directly above it (smaller index)
                neighbor = session.exec(
                    select(LifeTask)
                    .where(LifeTask.project_id == task.project_id, LifeTask.order_index < task.order_index)
                    .order_by(col(LifeTask.order_index).desc())
                ).first()
            else:
                # Find the task directly below it (larger index)
                neighbor = session.exec(
                    select(LifeTask)
                    .where(LifeTask.project_id == task.project_id, LifeTask.order_index > task.order_index)
                    .order_by(col(LifeTask.order_index).asc())
                ).first()

            # If a neighbor exists, swap their indexes!
            if neighbor:
                temp_index = task.order_index
                task.order_index = neighbor.order_index
                neighbor.order_index = temp_index
                
                session.add(task)
                session.add(neighbor)
                session.commit()
                
        self.load_backlog()
        
    # --- Universal Inspector Panel State ---
    is_inspector_open: bool = False
    inspector_entity_id: str = ""
    inspector_entity_type: str = ""  # Will store "epic", "project", or "task"
    
    # The Draft Buffer (Shared across all entities!)
    draft_title: str = ""
    draft_domain: str = ""
    draft_estimated_time_str: str = ""
    
    # --- Quick Capture State ---
    is_capture_open: bool = False
    capture_title: str = ""
    
    # --- Explicit Setters ---
    def set_capture_title(self, title: str):
        self.capture_title = title
    
    # --- NEW: Explicit Data Pipeline (Setters) ---
    def set_draft_title(self, title: str):
        self.draft_title = title

    def set_draft_domain(self, domain: str):
        self.draft_domain = domain

    def set_draft_estimated_time_str(self, time_str: str):
        self.draft_estimated_time_str = time_str

    def open_inspector(self, entity_id: str, entity_type: str):
        """Fetches details for any entity type and loads them into the draft buffer."""
        self.inspector_entity_id = str(entity_id)
        self.inspector_entity_type = entity_type
        
        with rx.session() as session:
            # Dynamically select the correct table
            entity = None
            if entity_type == "epic":
                entity = session.get(LifeEpic, int(entity_id))
            elif entity_type == "project":
                entity = session.get(LifeProject, int(entity_id))

                if entity:
                    self.draft_title = entity.title
                    self.draft_domain = getattr(entity, "domain", "Unassigned")
                    self.draft_estimated_time_str = format_human_time(getattr(entity, "estimated_minutes", 0))
                    
                    # --- NEW: Fetch the Epic Title ---
                    if getattr(entity, "epic_id", None):
                        epic = session.get(LifeEpic, entity.epic_id)
                        self.draft_epic_title = epic.title if epic else "Unassigned"
                    else:
                        self.draft_epic_title = "Unassigned"
                    
                    self.is_inspector_open = True
                    
            elif entity_type == "task":
                entity = session.get(LifeTask, int(entity_id))
                
            if entity:
                self.draft_title = entity.title
                # Using getattr ensures it safely defaults if a column is ever missing
                self.draft_domain = getattr(entity, "domain", "Unassigned")
                # Fetch DB minutes and format them nicely for the UI
                db_mins = getattr(entity, "estimated_minutes", 0)
                self.draft_estimated_time_str = format_human_time(db_mins)
                self.is_inspector_open = True

    def close_inspector(self):
        """Discards drafts and hides the panel."""
        self.is_inspector_open = False

    def save_inspector_changes(self):
        """Pushes the drafts safely into the correct database table."""
        if not self.inspector_entity_id:
            return
            
        with rx.session() as session:
            # Dynamically grab the correct record
            entity = None
            if self.inspector_entity_type == "epic":
                entity = session.get(LifeEpic, int(self.inspector_entity_id))
            elif self.inspector_entity_type == "project":
                entity = session.get(LifeProject, int(self.inspector_entity_id))
                if entity:
                    entity.title = self.draft_title
                    entity.domain = self.draft_domain
                    entity.estimated_minutes = parse_human_time(self.draft_estimated_time_str)
                    
                    # --- NEW: Save the Epic ID ---
                    if self.draft_epic_title != "Unassigned":
                        target_epic = session.exec(select(LifeEpic).where(LifeEpic.title == self.draft_epic_title)).first()
                        entity.epic_id = target_epic.id if target_epic else None
                    else:
                        entity.epic_id = None
                        
                    session.add(entity)
                    session.commit()
                    
            elif self.inspector_entity_type == "task":
                entity = session.get(LifeTask, int(self.inspector_entity_id))
                
            if entity:
                entity.title = self.draft_title
                entity.domain = self.draft_domain
                entity.estimated_minutes = parse_human_time(self.draft_estimated_time_str)
                session.add(entity)
                session.commit()
                
        # Refresh the main board to show the new title, and close the panel!
        self.load_backlog()
        self.is_inspector_open = False
        
    def archive_task(self, task_id: str):
        """Marks a task as completed and hides it from the active board."""
        with rx.session() as session:
            # Note: Ensure you import LifeTask if it isn't globally available in the file
            task = session.get(LifeTask, int(task_id))
            if task:
                task.is_archived = True
                task.status = "Completed"  # Automatically update the status!
                session.add(task)
                session.commit()
                
        # Refresh the lists to instantly hide the task
        self.load_backlog()
        
    # --- Engine Controls ---
    def open_capture(self):
        """Clears the buffer and opens the Quick Capture modal."""
        self.capture_title = ""
        self.is_capture_open = True

    def close_capture(self):
        """Discards the capture and hides the modal."""
        self.is_capture_open = False

    capture_title: str = ""
    capture_entity_type: str = "task"  # Controls the toggle and hides the Epic dropdown by default
    capture_epic_title: str = "Unassigned"

    # Explicit Setters
    def set_capture_title(self, title: str):
        self.capture_title = title

    def set_capture_entity_type(self, entity_type: str):
        self.capture_entity_type = entity_type

    def set_capture_epic_title(self, title: str):
        self.capture_epic_title = title

    # The Save Engine
    def save_capture(self):
        """Commits the inline Rapid Capture directly to PostgreSQL."""
        if not self.capture_title.strip():
            return
            
        with rx.session() as session:
            from sqlmodel import select
            
            if self.capture_entity_type == "task":
                # Save as a basic task
                new_task = LifeTask(
                    title=self.capture_title.strip(),
                    domain="Unassigned",
                    estimated_minutes=0,
                    order_index=0
                )
                session.add(new_task)
                
            elif self.capture_entity_type == "project":
                # Save as a Project
                new_project = LifeProject(
                    title=self.capture_title.strip(), 
                    domain="Unassigned", 
                    order_index=0
                )
                
                # Link the Epic if one was selected!
                if self.capture_epic_title != "Unassigned":
                    target_epic = session.exec(select(LifeEpic).where(LifeEpic.title == self.capture_epic_title)).first()
                    new_project.epic_id = target_epic.id if target_epic else None
                    
                session.add(new_project)
                
            session.commit()
            
        # Clear the input bar and refresh the board
        self.capture_title = ""
        self.capture_epic_title = "Unassigned"
        self.load_backlog()
            
        with rx.session() as session:
            # We create a brand new task. 
            # Notice we give it an order_index of 0. 
            # Our Auto-Healing engine will automatically space it out on the next load!
            new_task = LifeTask(
                title=self.capture_title.strip(),
                domain="Unassigned",
                estimated_minutes=0,
                order_index=0,
                # project_id=None (or whatever your default is for the Inbox)
            )
            session.add(new_task)
            session.commit()
            
        # Refresh the board and close the modal
        self.load_backlog()
        self.is_capture_open = False