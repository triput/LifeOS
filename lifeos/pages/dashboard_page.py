
# ==============================================================================
# File: lifeos/pages/dashboard_page.py
# Description: Main Mission Control dashboard layout and widget assembly
# Component: Frontend / Page
# Version: 1.0 (Gold Master)
# Created: 2026-06-01
# Last Update: 2026-06-01
# ==============================================================================

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.work_state import WorkState
from lifeos.state.agenda_state import AgendaState
from lifeos.state.base_state import AppState
from lifeos.state.academy_state import AcademyState
from lifeos.state.habitat_state import HabitatState
from lifeos.components.template import page_template
from lifeos.components.badges import status_badge, priority_badge
from lifeos.state.habitat_state import HabitatState
from lifeos.pages.agenda_page import google_calendar_widget
from lifeos.components.quick_add import universal_quick_add_widget




def observatory_hud() -> rx.Component:
    """The dynamic environment tracking widget."""
    return rx.box(

        rx.hstack(
            # Left Side: Current Weather & Temperature
            rx.vstack(
                rx.text(
                    HabitatState.habitat_name,
                    font_size="10px",
                    font_weight="700",
                    color=COLORS["muted"],
                    letter_spacing="0.1em",
                ),
                rx.hstack(
                    rx.icon(
                        # Dynamically swap icon based on day/night
                        rx.cond(HabitatState.is_day, "sun", "moon"), 
                        size=32, 
                        # Dynamic color (Warning/Amber for Sun, Primary/Teal for Moon)
                        color=rx.cond(HabitatState.is_day, COLORS["warning"], COLORS["primary"])
                    ),
                    rx.vstack(
                        rx.text(
                            HabitatState.current_temp, 
                            font_size="28px", 
                            font_weight="800", 
                            color=COLORS["text"], 
                            font_family="'Cabinet Grotesk', sans-serif", 
                            line_height="1"
                        ),
                        rx.text(HabitatState.weather_condition, font_size="12px", color=COLORS["muted"]),
                        spacing="0",
                    ),
                    spacing="3",
                    align="center",
                ),
                spacing="2",
                align="start",
            ),
            
            rx.spacer(),
            
            # Right Side: Celestial Tracking
            rx.hstack(
                # Sunrise
                rx.vstack(
                    rx.icon("sunrise", size=16, color=COLORS["muted"]),
                    rx.text(HabitatState.sunrise, font_size="12px", color=COLORS["text"], font_weight="600"),
                    align="center",
                    spacing="1",
                ),
                # Sunset
                rx.vstack(
                    rx.icon("sunset", size=16, color=COLORS["muted"]),
                    rx.text(HabitatState.sunset, font_size="12px", color=COLORS["text"], font_weight="600"),
                    align="center",
                    spacing="1",
                ),
                # Moon Phase
                rx.vstack(
                    rx.icon("moon-star", size=16, color=COLORS["muted"]),
                    rx.text(HabitatState.moon_phase, font_size="12px", color=COLORS["text"], font_weight="600"),
                    align="center",
                    spacing="1",
                ),
                spacing="6",
            ),
            width="100%",
            align="center",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        width="100%",
        margin_bottom="24px",
    )
def kpi_card(label: str, value, color: str = COLORS["text"], icon: str = "activity", item_type: str = "") -> rx.Component:
    """Single KPI metric card."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=20, color=color),
                rx.text(
                    label,
                    font_size="12px",
                    color=COLORS["muted"],
                    font_weight="600",
                    letter_spacing="0.05em",
                ),
                align="center",
                spacing="2",
            ),
            rx.text(
                value,
                font_size="32px",
                font_weight="800",
                color=color,
                font_family="'Cabinet Grotesk', sans-serif",
            ),
            align="start",
            spacing="2",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        flex="1",
        min_width="160px",
        
        # --- NEW: Make it interactive ---
        cursor="pointer",
        _hover={
            "border_color": color,
            "transform": "translateY(-2px)",
            "box_shadow": f"0 4px 12px rgba(0,0,0,0.15)"
        },
        transition="all 0.2s ease",
        on_click=lambda:WorkState.open_kpi_drawer(item_type), 
        )
        


def task_row_item(task: dict) -> rx.Component:
    """A single task row for the recent tasks list."""
    return rx.hstack(
        rx.icon("circle-dot", size=14, color=COLORS["primary"]),
        rx.text(
            task["title"],
            font_size="14px",
            color=COLORS["text"],
            flex="1",
        ),
        status_badge(task["status"]),
        priority_badge(task["priority"]),
        rx.cond(
            task["due_date"] != "",
            rx.text(
                task["due_date"],
                font_size="11px",
                color=COLORS["muted"],
            ),
            rx.fragment(),
        ),
        rx.icon_button(
            rx.icon("pencil", size=12),
            size="1",
            variant="ghost",
            color_scheme="gray",
            on_click=WorkState.open_drawer("task", task["id"]),
        ),
        align="center",
        spacing="2",
        padding="8px 12px",
        border_radius="6px",
        _hover={"background_color": COLORS["surface2"]},
        width="100%",
        border_bottom=f"1px solid {COLORS['border']}",
    )

def feed_filter_menu() -> rx.Component:
    """Popover menu for multi-select feed filtering."""
    return rx.popover.root(
        rx.popover.trigger(
            rx.icon_button(rx.icon("filter", size=16), variant="ghost", color_scheme="gray", size="1")
        ),
        rx.popover.content(
            rx.vstack(
                rx.text("STATUS", font_size="11px", font_weight="700", color=COLORS["muted"]),
                rx.checkbox(
                    "In Progress", 
                    checked=~WorkState.hidden_statuses.contains("In Progress"), 
                    on_change=lambda val: WorkState.toggle_status_filter("In Progress", val)
                ),
                rx.checkbox(
                    "Completed", 
                    checked=~WorkState.hidden_statuses.contains("Completed"), 
                    on_change=lambda val: WorkState.toggle_status_filter("Completed", val)
                ),
                
                rx.divider(margin_y="2"),
                
                rx.text("PRIORITY", font_size="11px", font_weight="700", color=COLORS["muted"]),
                rx.checkbox(
                    "Critical", 
                    checked=~WorkState.hidden_priorities.contains(1), 
                    on_change=lambda val: WorkState.toggle_priority_filter(1, val)
                ),
                rx.checkbox(
                    "High", 
                    checked=~WorkState.hidden_priorities.contains(2), 
                    on_change=lambda val: WorkState.toggle_priority_filter(2, val)
                ),
                rx.checkbox(
                    "Normal", 
                    checked=~WorkState.hidden_priorities.contains(3), 
                    on_change=lambda val: WorkState.toggle_priority_filter(3, val)
                ),
                rx.checkbox(
                    "Low", 
                    checked=~WorkState.hidden_priorities.contains(4), 
                    on_change=lambda val: WorkState.toggle_priority_filter(4, val)
                ),
                
                align="start",
                width="150px",
                padding="12px",
            ),
            align="end",
            background_color=COLORS["surface"],
            border=f"1px solid {COLORS['border']}",
        )
    )


def recent_tasks_list() -> rx.Component:
    """List of recent tasks."""

    return rx.box(
        # Standardized Recent Tasks Header
            rx.hstack(
                rx.icon("list-todo", size=18, color=COLORS["primary"]),
                rx.text(
                    "RECENT TASKS",
                    font_size="12px",
                    font_weight="700",
                    color=COLORS["muted"],
                    letter_spacing="0.08em",
                ),
                rx.spacer(),
                
                # Right-aligned controls
                rx.hstack(
                    feed_filter_menu(),
                    rx.select.root(
                        rx.select.trigger(width="110px", size="1", variant="ghost"),
                        rx.select.content(
                            rx.select.item("Recent", value="recent"),
                            rx.select.item("Priority", value="priority"),
                            rx.select.item("Status", value="status"),
                            rx.select.item("Due Date", value="due_date"),
                            background_color=COLORS["surface"],
                        ),
                        value=WorkState.feed_sort_order,
                        on_change=WorkState.set_feed_sort_order,
                    ),
                    rx.link(
                        "View All",
                        href="/work",
                        font_size="12px",
                        color=COLORS["accent"],
                        _hover={"color": COLORS["primary"]},
                    ),
                    align="center",
                    spacing="4",
                ),
                align="center",
                width="100%",
                padding_bottom="12px",
                border_bottom=f"1px solid {COLORS['border']}",
            ),
            
        rx.cond(
            WorkState.tasks.length() == 0,
            rx.box(
                rx.vstack(
                    rx.icon("inbox", size=32, color=COLORS["muted"]),
                    rx.text("No tasks yet", font_size="14px", color=COLORS["muted"]),
                    align="center",
                    spacing="2",
                    padding="24px",
                ),
            ),
            rx.vstack(
                rx.foreach(WorkState.tasks, task_row_item),
                spacing="0",
                width="100%",
                align="start",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="16px",
        width="100%",
        margin_bottom="8px"
    )

def academy_feed_widget() -> rx.Component:
    """Dashboard widget displaying active Academy items."""
    return rx.box(
        rx.vstack(
            # Feed Header with Sorting
            rx.hstack(
                rx.icon("graduation-cap", size=18, color=COLORS["primary"]),
                rx.text(
                    "ACADEMY QUEUE",
                    font_size="12px",
                    font_weight="700",
                    color=COLORS["muted"],
                    letter_spacing="0.08em",
                ),
                rx.spacer(),
                
                # The New Sorting Dropdown (Item 8)
                rx.select.root(
                    rx.select.trigger(width="110px", size="1", variant="ghost"),
                    rx.select.content(
                        rx.select.item("Recent", value="recent"),
                        rx.select.item("Priority", value="priority"),
                        rx.select.item("Status", value="status"),
                        rx.select.item("Due Date", value="due_date"),
                        background_color=COLORS["surface"],
                    ),
                    value=WorkState.feed_sort_order,
                    on_change=WorkState.set_feed_sort_order,
                ),
                
                align="center",
                width="100%",
                padding_bottom="12px",
                border_bottom=f"1px solid {COLORS['border']}",
            ),
            
            # The Academy List (Assumes AcademyState has an 'items' or 'courses' list)
            # Update 'AcademyState.items' to match your actual variable name!
            rx.cond(
                AcademyState.tasks.length() > 0,
                rx.foreach(
                    AcademyState.tasks,
                    lambda item: rx.hstack(
                        rx.checkbox(color_scheme="teal"),
                        rx.text(item.title, font_size="14px", color=COLORS["text"], font_weight="500"),
                        rx.spacer(),
                        rx.badge(item.status, variant="soft", color_scheme="blue"),
                        rx.icon_button(
                            rx.icon("pencil", size=14),
                            variant="ghost",
                            color_scheme="gray",
                            size="1",
                            on_click=lambda: AcademyState.open_drawer(item.id),
                        ),
                        align="center",
                        width="100%",
                        padding="8px 0",
                        border_bottom=f"1px solid {COLORS['bg']}",
                    )
                ),
                rx.text("No active training items.", font_size="12px", color=COLORS["muted"], padding_top="12px")
            ),
            
            spacing="2",
            width="100%",
            align="start",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        width="100%",
        margin_top="16px",
    )

def scheduled_task_mini(task: dict) -> rx.Component:
    """Mini scheduled task entry in the agenda widget."""
    return rx.hstack(
        rx.text(
            task["scheduled_at"],
            font_size="11px",
            color=COLORS["muted"],
            min_width="50px",
            font_weight="600",
        ),
        rx.text(
            task["title"],
            font_size="13px",
            color=COLORS["text"],
            flex="1",
        ),
        status_badge(task["status"]),
        align="center",
        spacing="2",
        padding="6px 8px",
        border_radius="4px",
        _hover={"background_color": COLORS["surface2"]},
        width="100%",
    )


def due_today_mini(task: dict) -> rx.Component:
    """Mini due-today task entry."""
    return rx.hstack(
        rx.icon("triangle-alert", size=13, color=COLORS["warning"]),
        rx.text(
            task["title"],
            font_size="13px",
            color=COLORS["text"],
            flex="1",
        ),
        status_badge(task["status"]),
        align="center",
        spacing="2",
        padding="6px 8px",
        border_radius="4px",
        _hover={"background_color": COLORS["surface2"]},
        width="100%",
    )


def agenda_widget() -> rx.Component:
    """Dashboard widget for local scheduled tasks."""
    
    # THE FIX: Add the missing helper function to render the rows
    def render_task_row(task):
        is_done = (task["status"] == "Completed")
        
        return rx.hstack(
            rx.checkbox(
                checked=is_done,
                on_change=lambda _: WorkState.fast_complete_item(task["id"], "tasks"),
                color_scheme="teal",
                size="3",
            ),
            rx.text(
                task["title"],
                font_size="14px",
                color=rx.cond(is_done, COLORS["muted"], COLORS["text"]),
                text_decoration=rx.cond(is_done, "line-through", "none"),
                font_weight="500",
            ),
            rx.spacer(),
            rx.icon_button(
                rx.icon("pencil", size=14),
                variant="ghost",
                color_scheme="gray",
                size="1",
                on_click=lambda: WorkState.open_drawer("task", task["id"]), 
            ),
            align="center",
            width="100%",
            padding="8px 0",
            border_bottom=f"1px solid {COLORS['bg']}", # Uses the background color for a subtle divider
        )

    return rx.box(
        rx.vstack(
            # Standardized Agenda Header
            rx.hstack(
                rx.icon("calendar", size=18, color=COLORS["primary"]),
                rx.text(
                    "TODAY'S AGENDA",
                    font_size="12px",
                    font_weight="700",
                    color=COLORS["muted"],
                    letter_spacing="0.08em",
                ),
                rx.spacer(),
                rx.link(
                    "Full View",
                    href="/agenda",
                    font_size="12px",
                    color=COLORS["accent"],
                    _hover={"color": COLORS["primary"]},
                ),
                align="center",
                width="100%",
                padding_bottom="12px",
                border_bottom=f"1px solid {COLORS['border']}",
            ),
            
            # Content
            rx.cond(
                AgendaState.due_today.length() > 0,
                rx.vstack(
                    rx.foreach(AgendaState.due_today, lambda task: render_task_row(task)),
                    width="100%",
                    spacing="2",
                    padding_top="8px",
                ),
                # Empty State
                rx.center(
                    rx.vstack(
                        rx.icon("calendar-x-2", size=32, color=COLORS["muted"]),
                        rx.text("No tasks scheduled today", font_size="13px", color=COLORS["muted"]),
                        align="center",
                        spacing="2",
                    ),
                    width="100%",
                    height="100px", 
                )
            ),
            
            spacing="2",
            width="100%",
            align="start",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        width="100%",
        min_height="180px", 
    )
    
def quick_add_section() -> rx.Component:
    """Universal Quick-add task input."""
    

def kpi_action_drawer() -> rx.Component:
    """Slide-out drawer for fast-completing items."""

        
    # Helper to render individual rows with a checkbox
    def render_action_row(item, item_type: str):
        # Determine status boolean (Reflex Var)
        is_done = (item.status == "Completed")
        
        return rx.hstack(
            rx.checkbox(
                checked=is_done,
                on_change=lambda _: WorkState.fast_complete_item(item.id, item_type),
                color_scheme="teal",
                size="3",
            ),
            rx.text(
                item.title,
                font_size="14px",
                
                # THE FIX: Both of these must use rx.cond, absolutely no "if / else" here!
                color=rx.cond(is_done, COLORS["muted"], COLORS["text"]),
                text_decoration=rx.cond(is_done, "line-through", "none"),
                
                font_weight="500",
            ),
            rx.spacer(),
            rx.icon_button(
                rx.icon("pencil", size=14),
                variant="ghost",
                color_scheme="gray",
                size="1",
                on_click=lambda: WorkState.open_drawer(item_type[:-1], item.id), 
            ),
            align="center",
            width="100%",
            padding="12px 0",
            border_bottom=f"1px solid {COLORS['border']}",
        )
    return rx.drawer.root(
        rx.drawer.overlay(background_color="rgba(0,0,0,0.4)"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.text(
                            "FAST ACTION: ",
                            rx.text(WorkState.kpi_drawer_type.upper(), color=COLORS["primary"], as_="span"),
                            font_size="18px",
                            font_weight="700",
                            color=COLORS["text"],
                            font_family="'Cabinet Grotesk', sans-serif",
                        ),
                        rx.spacer(),
                        rx.drawer.close(
                            rx.icon_button(rx.icon("x", size=18), variant="ghost", color_scheme="gray", on_click=WorkState.close_kpi_drawer)
                        ),
                        align="center",
                        width="100%",
                        padding_bottom="16px",
                        border_bottom=f"1px solid {COLORS['border']}",
                    ),
                    
                    # Dynamic List Content
                    rx.box(
                        rx.match(
                            WorkState.kpi_drawer_type,
                            ("epics", rx.foreach(WorkState.epics, lambda x: render_action_row(x, "epics"))),
                            ("projects", rx.foreach(WorkState.projects, lambda x: render_action_row(x, "projects"))),
                            ("tasks", rx.foreach(WorkState.tasks, lambda x: render_action_row(x, "tasks"))),
                            ("subtasks", rx.foreach(WorkState.subtasks, lambda x: render_action_row(x, "subtasks"))),
                            rx.text("Loading...", color=COLORS["muted"])
                        ),
                        width="100%",
                        overflow_y="auto",
                        flex="1",
                        padding_top="8px",
                    ),
                    
                    height="100%",
                    width="100%",
                    align="start",
                ),
                background_color=COLORS["surface"],
                padding="24px",
                width="400px",
                height="100%",
            ),
        ),
        direction="right",
        open=WorkState.kpi_drawer_open,
        on_open_change=WorkState.handle_kpi_drawer_change,
    )

@rx.page(
    route="/",
    title="Dashboard — LifeOS",
    on_load=[
        AppState.load_settings, 
        WorkState.load_work, 
        AcademyState.load_academy,
        AgendaState.load_agenda, 
        HabitatState.sync_environment,
        AgendaState.sync_external_calendar # <-- Make sure this is here!
    ],
)
def dashboard_page() -> rx.Component:
    """Dashboard page component."""
    return page_template(
        rx.vstack(
            observatory_hud(),
            kpi_action_drawer(),

            # KPI cards (Item 2: Reordered Hierarchically)
            rx.hstack(
                kpi_card("EPICS", WorkState.epics.length(), COLORS["accent"], "zap", "epics"),
                kpi_card("PROJECTS", WorkState.projects.length(), COLORS["warning"], "folder-open", "projects"),
                kpi_card("TOTAL TASKS", WorkState.tasks.length(), COLORS["text"], "list-checks", "tasks"),
                kpi_card("SUBTASKS", WorkState.subtasks.length(), COLORS["primary"], "git-branch", "subtasks"),
                spacing="4",
                width="100%",
                flex_wrap="wrap",
                margin_bottom="24px",
            ),

            universal_quick_add_widget(),  # The new universal quick-add widget at the top of the dashboard,

            # Main content blocks
           # Main content blocks
            rx.hstack(
                # Left Column: The Work & Academy Feed
                rx.vstack(
                    recent_tasks_list(),
                    academy_feed_widget(), 
                    width="100%",
                    flex="2", 
                    height="100%", # Ensure column fills space
                ),
                
                # Right Column: The Agenda & Calendar 
                rx.vstack(
                    agenda_widget(),
                    google_calendar_widget(), 
                    width="100%",
                    flex="1", 
                    height="100%", # Ensure column fills space
                ),
                
                spacing="6",
                width="100%",
                align="stretch", # THE FIX: Forces both columns to match heights
            ),
        ),
        title="Dashboard",
    )