"""Collapsible work tree and Kanban views: Epic → Project → Task → Subtask."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.work_state import WorkState
from lifeos.components.badges import status_badge, priority_badge


# ==============================================================================
# 1. REUSABLE RICH DATA WIDGETS
# ==============================================================================

def time_metrics_badges(item: dict) -> rx.Component:
    """Reusable block to safely render time badges if the data exists."""
    return rx.hstack(
        rx.cond(
            item.contains("estimated_str") & (item["estimated_str"] != ""),
            rx.badge(rx.icon("clock", size=12), item["estimated_str"], variant="surface", color_scheme="blue"),
            rx.fragment()
        ),
        rx.cond(
            item.contains("actual_str") & (item["actual_str"] != ""),
            rx.badge(rx.icon("circle-check", size=12), item["actual_str"], variant="surface", color_scheme="green"),
            rx.fragment()
        ),
        spacing="2",
        align="center"
    )


# ==============================================================================
# 2. KANBAN BOARD COMPONENTS
# ==============================================================================

def render_kanban_card(task: dict) -> rx.Component:
    """A compact, vertically stacked card for the Kanban view."""
    is_done = (task["status"] == "Completed")
    
    return rx.box(
        # Header: Checkbox, Title, Edit Button
        rx.hstack(
            rx.checkbox(
                checked=is_done,
                on_change=lambda val: WorkState.fast_complete_item(task["id"].to(int), "tasks"),
                color_scheme="teal"
            ),
            rx.text(
                task["title"], 
                font_weight="600", font_size="13px",
                color=rx.cond(is_done, COLORS["muted"], COLORS["text"]),
                text_decoration=rx.cond(is_done, "line-through", "none"),
                flex="1"
            ),
            rx.icon_button(
                rx.icon("pencil", size=12), 
                variant="ghost", size="1", color_scheme="gray",
                on_click=lambda: WorkState.open_drawer("task", task["id"].to(int))
            ),
            align="start", width="100%"
        ),
        
        # Parent Context
        rx.cond(
            task.contains("parent_title") & (task["parent_title"] != ""),
            rx.hstack(
                rx.icon("corner-left-up", size=10, color=COLORS["primary"]),
                rx.text(task["parent_title"], font_size="10px", color=COLORS["primary"], font_weight="bold"),
                margin_top="4px", margin_bottom="8px"
            ),
            rx.box(height="8px") # Spacer if no parent
        ),
        
        # Footer: Badges & Time Metrics
        rx.hstack(
            status_badge(task["status"]),
            priority_badge(task["priority"]),
            rx.spacer(),
            time_metrics_badges(task),
            width="100%",
            align="center"
        ),
        
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}", border_radius="6px",
        padding="10px 12px", margin_bottom="8px",
        box_shadow="0 1px 3px rgba(0,0,0,0.1)",
        _hover={"border_color": COLORS["primary"]},
    )    

def kanban_column(status: str) -> rx.Component:
    """Single Kanban column for a given status."""
    return rx.box(
        rx.text(
            status.upper(), font_size="12px", font_weight="700",
            color=COLORS["muted"], letter_spacing="0.06em", margin_bottom="12px",
        ),
        rx.foreach(
            WorkState.tasks,
            lambda task: rx.cond(
                task["status"] == status,
                render_kanban_card(task), # Uses the newly unified card!
                rx.fragment(),
            ),
        ),
        min_width="260px", flex="1",
        background_color=COLORS["surface2"], border_radius="8px",
        padding="12px", min_height="400px",
    )

def kanban_board() -> rx.Component:
    """Kanban board view of tasks by status."""
    return rx.hstack(
        kanban_column("To Do"), # Case matches your DB status strings
        kanban_column("In Progress"),
        kanban_column("Planned"),
        kanban_column("Completed"),
        kanban_column("Blocked"),
        kanban_column("On Hold"),
        spacing="4", width="100%", overflow_x="auto", align="start",
    )


# ==============================================================================
# 3. HIERARCHICAL TREE COMPONENTS
# ==============================================================================

def subtask_row(subtask: dict) -> rx.Component:
    return rx.hstack(
        rx.checkbox(
            checked=subtask["is_completed"],
            on_change=WorkState.toggle_subtask(subtask["id"]), # type: ignore
            color_scheme="teal",
        ),
        rx.text(
            subtask["title"], font_size="13px",
            color=rx.cond(subtask["is_completed"], COLORS["muted"], COLORS["text"]),
            text_decoration=rx.cond(subtask["is_completed"], "line-through", "none"),
            flex="1",
        ),
        rx.icon_button(
            rx.icon("pencil", size=12), size="1", variant="ghost", color_scheme="gray",
            on_click=WorkState.open_drawer("subtask", subtask["id"]),
        ),
        align="center", spacing="2", padding="6px 8px", border_radius="4px",
        _hover={"background_color": COLORS["surface2"]}, width="100%",
    )

def subtasks_for_task(task: dict) -> rx.Component:
    return rx.box(
        rx.foreach(
            WorkState.subtasks,
            lambda st: rx.cond(st["task_id"] == task["id"], subtask_row(st), rx.fragment()),
        ),
        padding_left="32px", border_left=f"1px solid {COLORS['border']}", margin_left="16px",
    )

def task_row(task: dict) -> rx.Component:
    is_done = (task["status"] == "Completed")
    return rx.box(
        rx.hstack(
            rx.checkbox(
                checked=is_done,
                on_change=lambda val: WorkState.fast_complete_item(task["id"].to(int), "tasks"),
                color_scheme="teal"
            ),
            rx.text(
                task["title"], font_size="14px", font_weight="500", flex="1",
                color=rx.cond(is_done, COLORS["muted"], COLORS["text"]),
                text_decoration=rx.cond(is_done, "line-through", "none")
            ),
            time_metrics_badges(task), # INJECTED RICH DATA
            status_badge(task["status"]),
            priority_badge(task["priority"]),
            rx.icon_button(
                rx.icon("pencil", size=12), size="1", variant="ghost", color_scheme="gray",
                on_click=WorkState.open_drawer("task", task["id"]),
            ),
            align="center", spacing="2", padding="8px 12px", border_radius="6px",
            _hover={"background_color": COLORS["surface2"]}, width="100%",
        ),
        subtasks_for_task(task),
        width="100%",
    )

def tasks_for_project(project: dict) -> rx.Component:
    return rx.box(
        rx.foreach(
            WorkState.tasks,
            lambda task: rx.cond(task["project_id"] == project["id"], task_row(task), rx.fragment()),
        ),
        padding_left="16px", border_left=f"2px solid {COLORS['border']}",
        margin_left="20px", margin_top="4px",
    )

def project_card(project: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("folder-open", size=16, color=COLORS["warning"]),
            rx.text(project["title"], font_size="15px", font_weight="600", color=COLORS["text"], flex="1"),
            time_metrics_badges(project), # INJECTED RICH DATA
            status_badge(project["status"]),
            priority_badge(project["priority"]),
            rx.icon_button(
                rx.icon("plus", size=12), size="1", variant="ghost", color_scheme="teal",
                on_click=WorkState.open_new_drawer("task", project["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=12), size="1", variant="ghost", color_scheme="gray",
                on_click=WorkState.open_drawer("project", project["id"]),
            ),
            align="center", spacing="2", padding="8px 12px", border_radius="6px",
            background_color=COLORS["surface2"], _hover={"background_color": "#252e42"}, width="100%",
        ),
        tasks_for_project(project),
        width="100%", margin_bottom="8px",
    )

def projects_for_epic(epic: dict) -> rx.Component:
    return rx.box(
        rx.foreach(
            WorkState.projects,
            lambda proj: rx.cond(proj["epic_id"] == epic["id"], project_card(proj), rx.fragment()),
        ),
        padding_left="16px", border_left=f"2px solid {COLORS['accent']}",
        margin_left="8px", margin_top="8px", padding_top="4px",
    )

def epic_section(epic: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("zap", size=18, color=COLORS["accent"]),
            rx.text(
                epic["title"], font_size="16px", font_weight="700", color=COLORS["text"], flex="1",
                font_family="'Cabinet Grotesk', sans-serif",
            ),
            time_metrics_badges(epic), # INJECTED RICH DATA
            status_badge(epic["status"]),
            priority_badge(epic["priority"]),
            rx.icon_button(
                rx.icon("plus", size=14), size="2", variant="ghost", color_scheme="teal",
                on_click=WorkState.open_new_drawer("project", epic["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=14), size="2", variant="ghost", color_scheme="gray",
                on_click=WorkState.open_drawer("epic", epic["id"]),
            ),
            align="center", spacing="2", padding="12px 16px", border_radius="8px",
            background_color=COLORS["surface"], border=f"1px solid {COLORS['border']}", width="100%",
        ),
        projects_for_epic(epic),
        width="100%", margin_bottom="16px", padding="8px", border_radius="8px",
        background_color="rgba(251, 113, 133, 0.04)",
    )

def work_tree() -> rx.Component:
    return rx.box(
        rx.foreach(WorkState.epics, epic_section),
        width="100%",
    )