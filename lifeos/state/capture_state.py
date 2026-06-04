# ==============================================================================
# File: lifeos/state/capture_state.py
# Description: Universal state engine for the Global Capture Bar, handling quick-adds across the app
# Component: Frontend / Layout  
# Version: 1.0 (Gold Master)
# Created: 2026-06-02
# Last Update: 2026-06-02
# ==============================================================================


import reflex as rx
from sqlmodel import Session, select


# Import ALL your models so the router has access to them
from lifeos.models import Epic, Project, Task, Subtask, Specialization, Course, Module
# Import your specific page states so we can trigger feed refreshes
from lifeos.state.work_state import WorkState
from lifeos.state.academy_state import AcademyState

class CaptureState(rx.State):
    """Universal state engine for the Global Capture Bar."""
    
    # The universal input buffers
    capture_title: str = ""
    capture_type: str = ""
    capture_domain: str = "work" # Tracks which page we are on
    # --- Parent Selection State ---
    capture_parent_id: str = ""  # Best to use string for Reflex Select values
    available_parents: list[dict[str, str]] = []  # Holds the dropdown options

    @rx.event
    def set_capture_parent_id(self, value: str):
        """Manual setter for the parent ID."""
        self.capture_parent_id = value

    @rx.event
    def set_capture_type(self, value: str):
        """Manual setter that ALSO triggers the parent list to refresh."""
        self.capture_type = value
        # Instantly fetch the correct parents based on the new type
        yield CaptureState.load_parent_options

    @rx.event
    def set_capture_title(self, title: str):
        """Update the capture title as the user types."""
        self.capture_title = title
        

    @rx.event
    def set_capture_domain(self, domain: str):
        """Allows the UI to tell the engine where the capture bar currently is."""
        self.capture_domain = domain
    
    @rx.event
    @rx.event
    def load_parent_options(self):
        """Queries the database to populate the parent dropdown."""
        self.capture_parent_id = ""
        self.available_parents = []
        
        t = self.capture_type.lower()
        items = []
        
        with rx.session() as session:
            # --- WORK DOMAIN PARENTS ---
            if self.capture_domain == "work":
                if t == "project": items = session.exec(select(Epic)).all()
                elif t == "task": items = session.exec(select(Project)).all()
                elif t == "subtask": items = session.exec(select(Task)).all()
                    
            # --- ACADEMY DOMAIN PARENTS ---
            elif self.capture_domain == "academy":
                if t == "course": items = session.exec(select(Specialization)).all()
                elif t == "module": items = session.exec(select(Course)).all()
                elif t == "task": items = session.exec(select(Module)).all()

        # THE FIX 2: Always show "Standalone" for nested items, even if the DB is empty
        if t in ["epic", "specialization"]:
            self.available_parents = [] # Root items never get the dropdown
        else:
            formatted = [{"label": item.title, "value": str(item.id)} for item in items]
            self.available_parents = [{"label": "— No Parent (Standalone) —", "value": "none"}] + formatted
    
    @rx.event
    def execute_capture(self):
        """The Universal Router: Saves data to the correct DB table based on domain."""
        if not self.capture_title.strip() or not self.capture_type:
            return
            
        title = self.capture_title.strip()
        item_type = self.capture_type.lower()
        
        # THE FIX: Safely parse the ID, handling both empty strings and our new "none" value
        if self.capture_parent_id and self.capture_parent_id != "none":
            parent_id = int(self.capture_parent_id)
        else:
            parent_id = None
        
        
        with rx.session() as session:
            # --- ROUTER: WORK DOMAIN ---
            if self.capture_domain == "work":
                if item_type == "epic":
                    session.add(Epic(title=title, status="In Progress"))
                elif item_type == "project":
                    session.add(Project(title=title, status="In Progress", epic_id=parent_id))
                elif item_type == "task":
                    session.add(Task(title=title, status="In Progress", priority=2, project_id=parent_id))
                elif item_type == "subtask":
                    session.add(Subtask(title=title, task_id=parent_id))
                    
            # --- ROUTER: ACADEMY DOMAIN ---
            elif self.capture_domain == "academy":
                if item_type == "specialization":
                    session.add(Specialization(title=title, status="Not Started"))
                elif item_type == "course":
                    session.add(Course(title=title, status="Not Started", specialization_id=parent_id))
                elif item_type == "module":
                    session.add(Module(title=title, status="Not Started", course_id=parent_id))
                elif item_type == "task": # Academy Task
                    session.add(Task(title=title, status="Not Started", is_academy=True, priority=2, course_id=parent_id)) # Example flag
            
            session.commit()
            
        # 1. Clear the inputs
        self.capture_title = ""
        
        # 2. Fire off the refresh commands to BOTH pages so the UI updates instantly
        yield WorkState.load_work
        yield AcademyState.load_academy