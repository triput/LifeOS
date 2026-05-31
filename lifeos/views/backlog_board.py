# ==============================================================================
# File: lifeos/views/backlog_board.py
# Description: Visual rendering of the Inbox and Structured Backlog.
# Component: View Layer
# ==============================================================================

import reflex as rx
from lifeos.states.management import ManagementState, ActiveProjectItem, NestedTaskItem, LIFE_DOMAINS

def focus_filter_bar() -> rx.Component:
    """A row of pill buttons to instantly filter the board."""
    # We dynamically combine "All" with your global domains list
    FILTER_OPTIONS = ["All"] + LIFE_DOMAINS
    
    return rx.hstack(
        rx.foreach(
            FILTER_OPTIONS,
            lambda domain: rx.button(
                domain,
                # Solid color if it's the active filter, soft if inactive
                variant=rx.cond(ManagementState.active_filter == domain, "solid", "soft"),
                # Indigo if active, gray if inactive
                color_scheme=rx.cond(ManagementState.active_filter == domain, "indigo", "gray"),
                on_click=lambda: ManagementState.set_active_filter(domain),
                border_radius="full",
                size="2",
                cursor="pointer",
            )
        ),
        width="100%",
        padding_y="4",
        padding_x="1",
        spacing="3",
        overflow_x="auto", # Allows the row to scroll horizontally on small screens!
        border_bottom="1px solid var(--gray-4)",
        margin_bottom="4"
    )

def render_inbox_task(task: dict) -> rx.Component:
    """Renders a single unassigned task card in the inbox."""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(task["title"], weight="bold", size="2"),
                rx.badge(task["priority"], color_scheme=rx.cond(task["priority"] == "High", "orange", "gray")),
                align_items="start", spacing="1"
            ),
            rx.spacer(),
            # The Action Button (We will wire this up next!)
            rx.icon_button(
                rx.icon(tag="arrow-right"), 
                size="1", variant="ghost", color_scheme="blue", 
                on_click=lambda: ManagementState.open_assignment_modal(task["id"])
            ),  
            width="100%", align="center"
        ),
        width="100%", padding="2", margin_bottom="2", variant="surface"
    )

def render_project_task(task: NestedTaskItem) -> rx.Component:
    """Renders a single task inside a project with Sorting, Inspector, and Archive controls."""
    return rx.hstack(
        # 1. The Task Icon and Title
        rx.icon(tag="circle", size=14, color_scheme="gray"),
        rx.text(task.title, size="2", weight="medium"),
        
        # Pushes all buttons to the right edge
        rx.spacer(),
        
        # 2. The Sorting Controls
        rx.icon_button(
            rx.icon(tag="arrow-up", size=16), 
            size="1", variant="ghost", color_scheme="gray", 
            on_click=lambda: ManagementState.move_task_up(task.id)
        ),
        rx.icon_button(
            rx.icon(tag="arrow-down", size=16), 
            size="1", variant="ghost", color_scheme="gray", 
            on_click=lambda: ManagementState.move_task_down(task.id)
        ),
        
        # 3. The Inspector Button (Blue)
        rx.icon_button(
            rx.icon(tag="settings-2", size=16), 
            size="1", variant="ghost", color_scheme="blue", 
            margin_left="2",
            on_click=lambda: ManagementState.open_inspector(task.id, "task")
        ),
        
        # 4. The Archive Button (Green)
        rx.icon_button(
            rx.icon(tag="check", size=16), 
            size="1", variant="soft", color_scheme="green", 
            margin_left="2",
            on_click=lambda: ManagementState.archive_task(task.id)
        ),
        
        # Container Styling
        width="100%", align="center", padding_y="2", border_bottom="1px solid var(--gray-4)"
    )

def render_project(project: ActiveProjectItem) -> rx.Component:
    """Renders an active project container with its sorted tasks."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="folder", color_scheme="indigo"),
                rx.link(
                    rx.text(project.title, weight="bold", size="2"),
                    href=f"/project/{project.id}"
                ), # <-- project.title
                rx.spacer(),
                # --- NEW: Project Inspector Button! ---
                rx.icon_button(
                    rx.icon(tag="settings-2", size=16), 
                    size="1", variant="ghost", color_scheme="blue", 
                    margin_right="2",
                    on_click=lambda: ManagementState.open_inspector(project.id, "project")
                ),
                rx.badge("Project", color_scheme="indigo", variant="soft"),
                width="100%", align="center"
            ),
            
            rx.box(
                rx.foreach(project.tasks, render_project_task), # <-- project.tasks (The compiler loves this!)
                width="100%", padding_left="4", margin_top="2"
            ),
            width="100%", align_items="start"
        ),
        width="100%", padding="3", margin_bottom="3", border_left="3px solid var(--indigo-9)"
    )

def render_epic(epic: dict) -> rx.Component:
    """Renders a massive Epic container."""
    return rx.card(
        rx.hstack(
            rx.icon(tag="mountain", color_scheme="purple"),
            rx.text(epic["title"], weight="bold", size="3"),
            rx.spacer(),
            rx.badge("Epic", color_scheme="purple", variant="soft"),
            width="100%", align="center"
        ),
        width="100%", padding="3", margin_bottom="3", border_left="4px solid var(--purple-9)", background_color="var(--purple-2)"
    )

def backlog_grooming_board() -> rx.Component:
    """The main split-view board for organizing tasks."""
    
    return rx.vstack(
        focus_filter_bar(),
        
        rx.hstack(
                
            # --- LEFT COLUMN: THE INBOX ---
            rx.vstack(
                rx.heading("Triage Inbox", size="4", weight="bold", color_scheme="gray"),
                rx.text("Unassigned items requiring review.", size="1", color_scheme="gray", margin_bottom="2"),
                
                rx.cond(
                    ManagementState.raw_inbox_tasks.length() > 0,
                    rx.vstack(
                        rx.foreach(ManagementState.raw_inbox_tasks, render_inbox_task),
                        width="100%"
                    ),
                    rx.text("Inbox Zero! Great job.", color_scheme="green", size="2")
                ),
                width="45%", align_items="start", padding_right="4", border_right="1px solid var(--gray-5)"
            ),
            
            # --- RIGHT COLUMN: THE STRUCTURED BACKLOG ---
            rx.vstack(
                rx.heading("Active Epics & Projects", size="4", weight="bold", color_scheme="gray"),
                rx.text("Your structured hierarchy.", size="1", color_scheme="gray", margin_bottom="2"),
                
                # Epics
                rx.foreach(ManagementState.active_epics, render_epic),
                
                # Projects
                rx.foreach(ManagementState.active_projects, render_project),
                
                width="55%", align_items="start", padding_left="4"
            ),
        width="100%", align_items="start", margin_top="5"
        )
    )