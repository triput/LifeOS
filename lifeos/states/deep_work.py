# ==============================================================================
# File: lifeos/states/deep_work.py
# Description: State management for isolated Epic/Project focus views.
# Component: State Management Layer
# ==============================================================================

import reflex as rx
from typing import List, Dict
from sqlmodel import select
from lifeos.state import State
from lifeos.models.habitat import LifeTask
from datetime import datetime, timezone


class DeepWorkState(State):
    """Handles the focused view for a single Project or Epic."""
    

    
    # The active project data
    active_project_title: str = "Loading..."
    active_project_domain: str = ""
    
    # The tasks belonging strictly to this project
    project_tasks: List[Dict[str, str]] = []

    def load_project_data(self):
        """Fetches the specific project and its nested tasks based on the URL parameter."""
        if not self.project_id:
            return
            
        with rx.session() as session:
            # 1. Fetch the Parent Project
            # Assuming project_id is an integer in the DB, we cast it safely
            try:
                p_id = int(self.project_id)
                project = session.get(LifeTask, p_id)
                
                if project:
                    self.active_project_title = project.title
                    self.active_project_domain = project.domain
                else:
                    self.active_project_title = "Project Not Found"
                    return
                    
            except ValueError:
                self.active_project_title = "Invalid Project ID"
                return

            # 2. Fetch the Child Tasks
            # Assuming your LifeTask model uses a 'parent_id' or similar to nest tasks
            # Adjust this query based on how your tasks are linked to projects!
            statement = select(LifeTask).where(LifeTask.project_id == p_id).order_by(LifeTask.id)
            children = session.exec(statement).all()
            
            ui_ready_tasks = []
            for t in children:
                ui_ready_tasks.append({
                    "id": str(t.id),
                    "title": t.title,
                    "status": t.status or "Triage",
                    "priority": t.priority or "Medium"
                })
                
            self.project_tasks = ui_ready_tasks

    @rx.var
    def completion_percentage(self) -> int:
        """Calculates how close this specific project is to being done."""
        if not self.project_tasks:
            return 0
        done_tasks = len([t for t in self.project_tasks if t.get("status") == "Done"])
        return int((done_tasks / len(self.project_tasks)) * 100)
    
    def update_project_task(self, task_id_str: str, field_name: str, new_value: str):
        """Universal mutator for inline task updates inside the Deep Work view."""
  
        with rx.session() as session:
            task = session.get(LifeTask, int(task_id_str))
            if not task:
                return
                
            # Standard Fields (Status, Priority)
            setattr(task, field_name, new_value)
                
            # Bump the modification timestamp
            task.last_modified_local = datetime.now(timezone.utc)
            
            session.add(task)
            session.commit()
            
        # 🔄 Re-run the query so the UI (and the progress bar!) updates instantly
        return self.load_project_data()
    
    # --- SHORT TERM MEMORY ---
    # Maps task_id -> the status it had before we clicked "Complete"
    previous_statuses: dict[str, str] = {}

    def toggle_task_completion(self, task_id_str: str, current_status: str):
        """Smart toggle that remembers the previous status for accurate rollbacks."""
        from datetime import datetime, timezone
        from lifeos.models.habitat import LifeTask
        
        with rx.session() as session:
            task = session.get(LifeTask, int(task_id_str))
            if not task:
                return
                
            if current_status == "Done":
                # It's currently Done. Revert to the saved status, or default to Active if we don't have one.
                new_status = self.previous_statuses.get(task_id_str, "Active")
            else:
                # We are completing it! Save the current status to memory first.
                self.previous_statuses[task_id_str] = current_status
                new_status = "Done"
                
            # Update DB
            task.status = new_status
            task.last_modified_local = datetime.now(timezone.utc)
            
            session.add(task)
            session.commit()
            
        # Re-fetch data to update the UI
        return self.load_project_data()