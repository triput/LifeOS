"""Dashboard page — KPIs, recent activity, today's agenda widget."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.work_state import WorkState
from lifeos.state.agenda_state import AgendaState
from lifeos.state.base_state import AppState
from lifeos.components.template import page_template
from lifeos.components.badges import status_badge, priority_badge


def kpi_card(label: str, value, color: str = COLORS["text"], icon: str = "activity") -> rx.Component:
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


def recent_tasks_list() -> rx.Component:
    """List of recent tasks."""
    return rx.box(
        rx.hstack(
            rx.text(
                "Recent Tasks",
                font_size="16px",
                font_weight="700",
                color=COLORS["text"],
                font_family="'Cabinet Grotesk', sans-serif",
            ),
            rx.spacer(),
            rx.link(
                rx.button(
                    "View All",
                    variant="ghost",
                    color_scheme="gray",
                    size="1",
                ),
                href="/work",
                text_decoration="none",
            ),
            align="center",
            width="100%",
            margin_bottom="12px",
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
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        flex="1",
        min_width="300px",
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
    """Mini today's agenda widget."""
    return rx.box(
        rx.hstack(
            rx.text(
                "Today's Agenda",
                font_size="16px",
                font_weight="700",
                color=COLORS["text"],
                font_family="'Cabinet Grotesk', sans-serif",
            ),
            rx.spacer(),
            rx.link(
                rx.button(
                    "Full View",
                    variant="ghost",
                    color_scheme="teal",
                    size="1",
                ),
                href="/agenda",
                text_decoration="none",
            ),
            align="center",
            width="100%",
            margin_bottom="12px",
        ),
        rx.vstack(
            rx.cond(
                AgendaState.scheduled_tasks.length() == 0,
                rx.box(
                    rx.vstack(
                        rx.icon("calendar-check", size=28, color=COLORS["muted"]),
                        rx.text(
                            "No tasks scheduled today",
                            font_size="13px",
                            color=COLORS["muted"],
                        ),
                        align="center",
                        spacing="2",
                        padding="16px",
                    ),
                ),
                rx.foreach(AgendaState.scheduled_tasks, scheduled_task_mini),
            ),
            spacing="1",
            width="100%",
        ),
        rx.cond(
            AgendaState.due_today.length() > 0,
            rx.box(
                rx.text(
                    "DUE TODAY",
                    font_size="11px",
                    font_weight="600",
                    color=COLORS["warning"],
                    letter_spacing="0.05em",
                    margin_top="12px",
                    margin_bottom="6px",
                ),
                rx.foreach(AgendaState.due_today, due_today_mini),
                width="100%",
            ),
            rx.fragment(),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        min_width="300px",
        flex="1",
    )


def quick_add_section() -> rx.Component:
    """Quick-add task input."""
    return rx.box(
        rx.hstack(
            rx.input(
                placeholder="Quick add epic title...",
                value=WorkState.quick_add_title,
                on_change=WorkState.set_quick_add_title,
                background_color=COLORS["surface"],
                border_color=COLORS["border"],
                color=COLORS["text"],
                flex="1",
                _placeholder={"color": COLORS["muted"]},
            ),
            rx.button(
                rx.icon("plus", size=16),
                "Add Epic",
                color_scheme="teal",
                on_click=WorkState.quick_add_epic,
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        margin_bottom="20px",
    )


@rx.page(
    route="/",
    title="Dashboard — LifeOS",
    on_load=[AppState.load_settings, WorkState.load_work, AgendaState.load_agenda],
)
def dashboard_page() -> rx.Component:
    """Dashboard page component."""
    return page_template(
        rx.vstack(
            # Welcome message
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Welcome to LifeOS",
                        font_size="24px",
                        font_weight="700",
                        color=COLORS["text"],
                        font_family="'Cabinet Grotesk', sans-serif",
                    ),
                    rx.text(
                        "Your personal productivity OS",
                        font_size="14px",
                        color=COLORS["muted"],
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                align="center",
                width="100%",
                margin_bottom="24px",
            ),

            # KPI cards
            rx.hstack(
                kpi_card("TOTAL TASKS", WorkState.tasks.length(), COLORS["text"], "list-checks"),
                kpi_card("EPICS", WorkState.epics.length(), COLORS["accent"], "zap"),
                kpi_card("PROJECTS", WorkState.projects.length(), COLORS["warning"], "folder-open"),
                kpi_card("SUBTASKS", WorkState.subtasks.length(), COLORS["primary"], "git-branch"),
                spacing="4",
                width="100%",
                flex_wrap="wrap",
                margin_bottom="24px",
            ),

            # Quick add
            quick_add_section(),

            # Main content: recent tasks + agenda
            rx.hstack(
                recent_tasks_list(),
                agenda_widget(),
                spacing="4",
                width="100%",
                align="start",
                flex_wrap="wrap",
            ),

            spacing="0",
            width="100%",
            align="start",
        ),
        title="Dashboard",
    )
