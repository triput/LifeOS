# ==============================================================================
# File: lifeos/states/tasks.py
# Description: State management for Agile tasks, triage, and backlog operations.
# Component: State Management Layer
# Version: 1.0 (Gold Master)
# Created: 2026-05-02
# ==============================================================================

import reflex as rx
from typing import List
from datetime import datetime, timezone
from sqlmodel import select

from lifeos.state import State
from lifeos.models.habitat import LifeTask

class TaskState(State):
    """Handles all logic for Mission Control Task Management."""
    
    # --- UI DICTIONARIES ---
    triage_list: list[dict[str,str]] = []
    
    # --- QUICK CAPTURE STATE ---
    new_task_title: str = ""
    new_task_desc: str = ""
    new_task_domain: str = "HOME"
    new_task_start_date: str = ""
    new_task_due_date: str = ""
    
    # --- QUICK CAPTURE SETTERS ---
    def set_new_task_title(self, val: str): self.new_task_title = val
    def set_new_task_desc(self, val: str): self.new_task_desc = val
    def set_new_task_domain(self, val: str): self.new_task_domain = val
    def set_new_task_start_date(self, val: str): self.new_task_start_date = val
    def set_new_task_due_date(self, val: str): self.new_task_due_date = val
    
    # --- FILTER & SORT STATE ---
    filter_domain: str = "All"
    filter_status: str = "All"
    sort_mode: str = "Priority"
    
    # --- FILTER & SORT SETTERS ---
    def set_filter_domain(self, val: str):
        self.filter_domain = val
        self.load_tasks()

    def set_filter_status(self, val: str):
        self.filter_status = val
        self.load_tasks()

    def set_sort_mode(self, val: str):
        self.sort_mode = val
        self.load_tasks()

    # --- COMPUTED COUNTERS ---
    @rx.var
    def critical_tasks_count(self) -> int:
        return len([t for t in self.triage_list if t.get("status") == "Critical"])

    @rx.var
    def triage_tasks_count(self) -> int:
        return len([t for t in self.triage_list if t.get("status") == "Triage"])

    @rx.var
    def active_tasks_count(self) -> int:
        return len([t for t in self.triage_list if t.get("status") == "Active"])

    @rx.var
    def blocked_tasks_count(self) -> int:
        return len([t for t in self.triage_list if t.get("status") == "Blocked"])

    # --- CORE OPERATIONS ---
    def load_tasks(self):
        """Fetches, filters, sorts, and sanitizes tasks for the UI."""
        with rx.session() as session:
            all_tasks = session.exec(select(LifeTask)).all()

            # --- 1. APPLY FILTERS ---
            filtered_tasks = []
            for t in all_tasks:
                if self.filter_domain != "All" and t.domain != self.filter_domain:
                    continue
                if self.filter_status != "All" and t.status != self.filter_status:
                    continue
                if self.filter_status == "All" and t.status == "Done":
                    continue
                filtered_tasks.append(t)

            # --- 2. APPLY SORTING ---
            if self.sort_mode == "Priority":
                def get_prio_val(task):
                    p = str(task.priority).strip() if task.priority else ""
                    if p in ["1", "Critical"]: return 1
                    if p in ["2", "High"]: return 2
                    if p in ["3", "Medium"]: return 3
                    if p in ["4", "Low"]: return 4
                    return 3 
                filtered_tasks.sort(key=get_prio_val)

            elif self.sort_mode == "Due Date":
                max_date = datetime(2099, 1, 1)
                filtered_tasks.sort(key=lambda x: x.due_date_local or max_date)

            else: # Age
                filtered_tasks.sort(key=lambda x: x.id, reverse=True)

            # --- 3. PURE PYTHON TRANSLATION LAYER ---
            ui_ready = []
             # Standard Python dictionary lookup with a safe default ("Medium")
            p_map = {
                "1": "Critical", "2": "High", "3": "Medium", "4": "Low",
                "Critical": "Critical", "High": "High", "Medium": "Medium", "Low": "Low"
                }
                            # Standard Python dictionary lookup with a safe default ("Triage")
            s_map = {
                "Triage": "Triage", "Active": "Active", "Blocked": "Blocked", "Done": "Done",
                "Inbox": "Triage"
                }
            
            for t in filtered_tasks:
                raw_priority = str(t.priority).strip() if t.priority else ""
                safe_priority = p_map.get(raw_priority, "Medium")

                raw_status = str(t.status).strip() if t.status else ""
                safe_status = s_map.get(raw_status, "Triage")

                ui_ready.append({
                    "id": str(t.id),
                    "title": t.title,
                    "domain": t.domain,
                    "status": safe_status,
                    "priority": safe_priority,
                    "start_date": t.start_date_local.strftime("%b %d") if getattr(t, "start_date_local", None) else "",
                    "due_date": t.due_date_local.strftime("%b %d") if getattr(t, "due_date_local", None) else "",
                    "age": "0d" 
                })
            
            self.triage_list = ui_ready

    def save_new_task(self):
        """Ingests a new task from the Quick Capture modal."""
        if not self.new_task_title.strip():
            return rx.window_alert("Signal missing a title!")

        start_dt = datetime.strptime(self.new_task_start_date, "%Y-%m-%d") if self.new_task_start_date else None
        due_dt = datetime.strptime(self.new_task_due_date, "%Y-%m-%d") if self.new_task_due_date else None

        with rx.session() as session:
            new_task = LifeTask(
                title=self.new_task_title,
                description=self.new_task_desc,
                para_category="Inbox",
                domain=self.new_task_domain,
                status="Triage",
                start_date_local=start_dt,
                due_date_local=due_dt,
                last_modified_local=datetime.now(timezone.utc)
            )
            session.add(new_task)
            session.commit()
        
        # Reset form state
        self.new_task_title = ""
        self.new_task_desc = ""
        self.new_task_domain = "HOME"
        self.new_task_start_date = ""
        self.new_task_due_date = ""
        
        self.load_tasks()
        
    def update_task_field(self, task_id_str: str, field_name: str, new_value: str):
        """Universal mutator for inline Agile task updates."""
        with rx.session() as session:
            task = session.get(LifeTask, int(task_id_str))
            if not task:
                return
            
            # Handle Temporal Boundaries
            if field_name in ["start_date_local", "due_date_local"]:
                if new_value.strip():
                    try:
                        dt_val = datetime.strptime(new_value.strip(), "%Y-%m-%d")
                        setattr(task, field_name, dt_val)
                    except ValueError:
                        return rx.window_alert("Invalid date format. Expected YYYY-MM-DD.")
                else:
                    # Allow clearing the date
                    setattr(task, field_name, None)
                    
            # Handle Standard Fields (Status, Priority, Domain)
            else:
                setattr(task, field_name, new_value)
                
            # Always bump the modification timestamp to keep sorting accurate
            task.last_modified_local = datetime.now(timezone.utc)
            
            session.add(task)
            session.commit()
            
        return self.load_tasks()