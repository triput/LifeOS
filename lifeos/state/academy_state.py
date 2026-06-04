# ==============================================================================
# File: lifeos/state/academy_state.py
# Description: Engine for managing learning tracks, courses, and modules.
# Component: State Engine
# Version: 1.0 (Gold Master)
# ==============================================================================

import reflex as rx
from sqlmodel import select

from lifeos.models import Specialization, Course, Module, LearningTask, Certification
from lifeos.state.base_state import AppState
# THE FIX: Import our universal time parsers!
from lifeos.utils import format_minutes_to_time, parse_time_to_minutes, models_to_dicts

class AcademyState(AppState):
    """State for the Academy track."""

    # --- UI Lists ---
    specializations: list[dict] = []
    courses: list[dict] = []
    modules: list[dict] = []
    tasks: list[dict] = [] # Maps to the UI's 'AcademyState.tasks' call
    certifications: list[dict] = []

    # --- Drawer State ---
    selected_item: dict = {}
    selected_type: str = "specialization"
    drawer_open: bool = False

    # --- Controlled Drawer Buffers (Matches work_state.py) ---
    drawer_title_str: str = ""
    drawer_description_str: str = ""
    drawer_estimated_str: str = ""
    drawer_actual_str: str = ""
    drawer_duration_str: str = ""
    drawer_status_str: str = "Not Started"

    @rx.event
    def set_drawer_title_str(self, val: str): self.drawer_title_str = val
    @rx.event
    def set_drawer_description_str(self, val: str): self.drawer_description_str = val
    @rx.event
    def set_drawer_estimated_str(self, val: str): self.drawer_estimated_str = val
    @rx.event
    def set_drawer_actual_str(self, val: str): self.drawer_actual_str = val
    @rx.event
    def set_drawer_duration_str(self, val: str): self.drawer_duration_str = val
    @rx.event
    def set_drawer_status_str(self, val: str): self.drawer_status_str = val


    @rx.event
    def load_academy(self):
        """Loads all academy data and injects rich time formats for the UI."""
        with rx.session() as session:
            raw_specs = session.exec(select(Specialization)).all()
            raw_courses = session.exec(select(Course)).all()
            raw_modules = session.exec(select(Module).order_by(Module.order_index)).all()
            raw_tasks = session.exec(select(LearningTask)).all()
            raw_certs = session.exec(select(Certification)).all()

            # THE FIX: Helper to inject human-readable time strings into every item
            def enrich(items):
                res = []
                for item in items:
                    d = item.model_dump()
                    d["estimated_str"] = format_minutes_to_time(getattr(item, "estimated_minutes", 0))
                    d["actual_str"] = format_minutes_to_time(getattr(item, "actual_minutes", 0))
                    res.append(d)
                return res

            self.specializations = enrich(raw_specs)
            self.courses = enrich(raw_courses)
            self.modules = enrich(raw_modules)
            self.tasks = enrich(raw_tasks) 
            self.certifications = models_to_dicts(raw_certs)

    @rx.event
    def open_drawer(self, item_type: str, item_id: int):
        """Opens the drawer and populates the controlled string buffers."""
        self.selected_type = item_type
        
        with rx.session() as session:
            model_map = {
                "specialization": Specialization, 
                "course": Course, 
                "module": Module, 
                "learning_task": LearningTask, 
                "task": LearningTask,
                "certification": Certification
            }
            model = model_map.get(item_type)
            
            if model:
                item = session.get(model, item_id)
                if item:
                    self.selected_item = item.model_dump()
                    
                    # THE FIX: Populate strict string buffers so UI doesn't ghost
                    self.drawer_title_str = getattr(item, "title", "") or ""
                    self.drawer_description_str = getattr(item, "description", "") or ""
                    self.drawer_estimated_str = format_minutes_to_time(getattr(item, "estimated_minutes", 0))
                    self.drawer_actual_str = format_minutes_to_time(getattr(item, "actual_minutes", 0))
                    self.drawer_duration_str = format_minutes_to_time(getattr(item, "scheduled_duration", 0))
                    # Force strict string casting so the UI never receives an Enum or object
                    raw_status = str(getattr(item, "status", "Not Started") or "Not Started")
                    self.drawer_status_str = raw_status.title()
        self.drawer_open = True

    @rx.event
    def open_new_drawer(self, item_type: str, parent_id: int = None):
        """Prepares the drawer for a brand new item."""
        self.selected_type = item_type
        
        new_item = {"id": 0} # 0 indicates new item to the save logic
        
        # THE FIX: Map the incoming parent_id to the correct foreign key
        if parent_id is not None:
            if item_type == "course":
                new_item["specialization_id"] = parent_id
            elif item_type == "module":
                new_item["course_id"] = parent_id
            elif item_type in ["learning_task", "task"]:
                new_item["module_id"] = parent_id
                
        self.selected_item = new_item
            
        # Clear the buffers
        self.drawer_title_str = ""
        self.drawer_description_str = ""
        self.drawer_estimated_str = ""
        self.drawer_actual_str = ""
        self.drawer_duration_str = ""
        self.drawer_status_str = "Not Started"
        
        self.drawer_open = True
        
    @rx.event
    def close_drawer(self):
        """Closes the edit drawer without saving."""
        self.drawer_open = False

    @rx.event
    def save_item(self, form_data: dict):
        """Saves drawer edits, translating human strings back to database integers."""
        item_id = self.selected_item.get("id", 0)
        
        with rx.session() as session:
            model_map = {
                "specialization": Specialization, 
                "course": Course, 
                "module": Module, 
                "learning_task": LearningTask,
                "task": LearningTask,
                "certification": Certification
            }
            model = model_map.get(self.selected_type)
            
            if not model: return

            if item_id == 0:
                # Creating a new item
                item = model()
                
                # THE FIX: Apply the parent foreign keys we tucked into selected_item
                if hasattr(item, "specialization_id") and "specialization_id" in self.selected_item:
                    item.specialization_id = self.selected_item["specialization_id"]
                if hasattr(item, "course_id") and "course_id" in self.selected_item:
                    item.course_id = self.selected_item["course_id"]
                if hasattr(item, "module_id") and "module_id" in self.selected_item:
                    item.module_id = self.selected_item["module_id"]
                
                    
                session.add(item)
            else:
                item = session.get(model, item_id)

            if item:
                # 1. Apply the Text Buffers
                item.title = self.drawer_title_str
                item.description = self.drawer_description_str
                
                # 2. Apply the Time Parsers (Human -> Machine)
                if hasattr(item, "estimated_minutes"):
                    item.estimated_minutes = parse_time_to_minutes(self.drawer_estimated_str)
                if hasattr(item, "actual_minutes"):
                    item.actual_minutes = parse_time_to_minutes(self.drawer_actual_str)
                if hasattr(item, "scheduled_duration"):
                    item.scheduled_duration = parse_time_to_minutes(self.drawer_duration_str)
                # 1. Apply the Text Buffers (Safely checking schema first)
                if hasattr(item, "title"):
                    item.title = self.drawer_title_str
                if hasattr(item, "description"):
                    item.description = self.drawer_description_str
                if hasattr(item, "status"):
                    item.status = self.drawer_status_str

                # 3. Apply remaining raw form data (status, etc.)
                for key, value in form_data.items():
                    # Skip the controlled fields so we don't overwrite our parsed data
                    if key not in ["title", "description", "estimated_minutes", "actual_minutes", "scheduled_duration"]:
                        if hasattr(item, key):
                            setattr(item, key, value)

                session.add(item)
                session.commit()

        self.drawer_open = False
        yield AcademyState.load_academy

    @rx.event
    def delete_item(self):
        """Deletes the currently open item directly from the drawer."""
        item_id = self.selected_item.get("id")
        
        if not item_id:
            self.drawer_open = False
            return

        with rx.session() as session:
            model_map = {
                "specialization": Specialization, 
                "course": Course, 
                "module": Module, 
                "learning_task": LearningTask,
                "task": LearningTask,
                "certification": Certification
            }
            model = model_map.get(self.selected_type)
            
            if model:
                item = session.get(model, item_id)
                if item:
                    session.delete(item)
                    session.commit()

        self.drawer_open = False
        yield AcademyState.load_academy

    @rx.event
    def toggle_learning_task(self, task_id: int):
        """Explicit boolean payload for toggling a task's completion status."""
        with rx.session() as session:
            lt = session.get(LearningTask, task_id)
            if lt:
                lt.is_completed = not lt.is_completed
                
                # Auto-sync status string if your DB uses it
                if hasattr(lt, "status"):
                    lt.status = "Completed" if lt.is_completed else "Not Started"
                    
                session.add(lt)
                session.commit()

        yield AcademyState.load_academy