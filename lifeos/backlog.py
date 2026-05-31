# ==============================================================================
# File: lifeos/backlog.py
# Description: The Management Hub for high-density Agile grooming.
# Component: Frontend UI (Page)
# Version: 1.0 (Gold Master)
# Created: 2026-05-04
# ==============================================================================

import reflex as rx
from lifeos.states.tasks import TaskState

def backlog_row(task: dict) -> rx.Component:
    """Renders a single row in the grooming table."""
    return rx.table.row(
        # Title (Read-Only for now, clicking could open a future edit modal)
        rx.table.cell(rx.text(task["title"], weight="bold")),
        
        # Domain Dropdown
        rx.table.cell(
            rx.select(
                ["HOME", "TECH", "ACADEMY", "THEATER", "GOVERNANCE"], 
                value=task["domain"], 
                on_change=lambda v: TaskState.update_task_field(task["id"], "domain", v),
                variant="surface", size="1"
            )
        ),
        
        # Priority Dropdown
        rx.table.cell(
            rx.select(
                ["Critical", "High", "Medium", "Low"], 
                value=task["priority"], 
                on_change=lambda v: TaskState.update_task_field(task["id"], "priority", v),
                variant="soft", size="1"
            )
        ),
        
        # Status Dropdown
        rx.table.cell(
            rx.select(
                ["Triage", "Active", "Blocked", "Done"], 
                value=task["status"], 
                on_change=lambda v: TaskState.update_task_field(task["id"], "status", v),
                variant="soft", size="1"
            )
        ),
        
        # Due Date
        rx.table.cell(rx.text(task["due_date"], color_scheme="gray", size="2")),
        
        align="center"
    )

def backlog_page() -> rx.Component:
    """The Master Grooming Suite."""
    return rx.container(
        rx.vstack(
            # --- Header ---
            rx.hstack(
                rx.link(rx.icon(tag="arrow-left"), href="/", color_scheme="gray"),
                rx.heading("Management Hub // Backlog Grooming", size="7", weight="bold"),
                rx.spacer(),
                rx.text(f"Total Items: {TaskState.triage_list.length()}", color_scheme="gray", weight="medium"),
                width="100%", align="center", padding_bottom="4", border_bottom="1px solid var(--gray-5)"
            ),
            
            # --- Reused Control Bar ---
            # We use the exact same filters from the Command Center!
            rx.hstack(
                rx.select(["All", "HOME", "TECH", "ACADEMY", "THEATER", "GOVERNANCE"], value=TaskState.filter_domain, on_change=TaskState.set_filter_domain, variant="surface"),
                rx.select(["All", "Triage", "Active", "Blocked", "Done"], value=TaskState.filter_status, on_change=TaskState.set_filter_status, variant="surface"),
                rx.spacer(),
                rx.select(["Priority", "Due Date", "Age"], value=TaskState.sort_mode, on_change=TaskState.set_sort_mode, variant="soft", color_scheme="gray"),
                width="100%", padding_y="4"
            ),
            
            # --- High Density Data Table ---
            rx.card(
                rx.scroll_area(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Task Definition"),
                                rx.table.column_header_cell("Domain"),
                                rx.table.column_header_cell("Priority"),
                                rx.table.column_header_cell("Status"),
                                rx.table.column_header_cell("Due Date"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(TaskState.triage_list, backlog_row)
                        ),
                        size="2", variant="surface", width="100%"
                    ),
                    style={"height": "70vh"}
                ),
                width="100%", padding="1"
            ),
            spacing="4", width="100%"
        ),
        size="4", padding="6"
    )