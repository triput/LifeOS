"""Collapsible work tree: Epic → Project → Task → Subtask."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.work import WorkState
from lifeos.components.badges import status_badge, priority_badge


def subtask_row(subtask: dict) -> rx.Component:
    """Render a single subtask row."""
    return rx.hstack(
        rx.checkbox(
            checked=subtask["is_completed"],
            on_change=WorkState.toggle_subtask(subtask["id"]),  # type: ignore
            color_scheme="teal",
        ),
        rx.text(
            subtask["title"],
            font_size="13px",
            color=rx.cond(
                subtask["is_completed"],
                COLORS["muted"],
                COLORS["text"],
            ),
            text_decoration=rx.cond(
                subtask["is_completed"],
                "line-through",
                "none",
            ),
            flex="1",
        ),
        rx.icon_button(
            rx.icon("pencil", size=12),
            size="1",
            variant="ghost",
            color_scheme="gray",
            on_click=WorkState.open_drawer("subtask", subtask["id"]),
        ),
        align="center",
        spacing="2",
        padding="6px 8px",
        border_radius="4px",
        _hover={"background_color": COLORS["surface2"]},
        width="100%",
    )


def subtasks_for_task(task: dict) -> rx.Component:
    """Show subtasks that belong to a given task."""
    return rx.box(
        rx.foreach(
            WorkState.subtasks,
            lambda st: rx.cond(
                st["task_id"] == task["id"],
                subtask_row(st),
                rx.fragment(),
            ),
        ),
        padding_left="32px",
        border_left=f"1px solid {COLORS['border']}",
        margin_left="16px",
    )


def task_row(task: dict) -> rx.Component:
    """Render a task row with its subtasks."""
    return rx.box(
        rx.hstack(
            rx.icon("circle-dot", size=14, color=COLORS["primary"]),
            rx.text(
                task["title"],
                font_size="14px",
                color=COLORS["text"],
                flex="1",
                font_weight="500",
            ),
            status_badge(task["status"]),
            priority_badge(task["priority"]),
            rx.cond(
                task["due_date"] != "",
                rx.text(
                    task["due_date"],
                    font_size="12px",
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
        ),
        subtasks_for_task(task),
        width="100%",
    )


def tasks_for_project(project: dict) -> rx.Component:
    """Show tasks that belong to a given project."""
    return rx.box(
        rx.foreach(
            WorkState.tasks,
            lambda task: rx.cond(
                task["project_id"] == project["id"],
                task_row(task),
                rx.fragment(),
            ),
        ),
        padding_left="16px",
        border_left=f"2px solid {COLORS['border']}",
        margin_left="20px",
        margin_top="4px",
    )


def project_card(project: dict) -> rx.Component:
    """Render a project with its tasks."""
    return rx.box(
        # Project header
        rx.hstack(
            rx.icon("folder-open", size=16, color=COLORS["warning"]),
            rx.text(
                project["title"],
                font_size="15px",
                font_weight="600",
                color=COLORS["text"],
                flex="1",
            ),
            status_badge(project["status"]),
            priority_badge(project["priority"]),
            rx.icon_button(
                rx.icon("plus", size=12),
                size="1",
                variant="ghost",
                color_scheme="teal",
                title="Add Task",
                on_click=WorkState.open_new_drawer("task", project["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=12),
                size="1",
                variant="ghost",
                color_scheme="gray",
                on_click=WorkState.open_drawer("project", project["id"]),
            ),
            align="center",
            spacing="2",
            padding="8px 12px",
            border_radius="6px",
            background_color=COLORS["surface2"],
            _hover={"background_color": "#252e42"},
            width="100%",
        ),
        tasks_for_project(project),
        width="100%",
        margin_bottom="8px",
    )


def projects_for_epic(epic: dict) -> rx.Component:
    """Show projects that belong to a given epic."""
    return rx.box(
        rx.foreach(
            WorkState.projects,
            lambda proj: rx.cond(
                proj["epic_id"] == epic["id"],
                project_card(proj),
                rx.fragment(),
            ),
        ),
        padding_left="16px",
        border_left=f"2px solid {COLORS['accent']}",
        margin_left="8px",
        margin_top="8px",
        padding_top="4px",
    )


def epic_section(epic: dict) -> rx.Component:
    """Render an Epic section with all its projects and tasks."""
    return rx.box(
        # Epic header
        rx.hstack(
            rx.icon("zap", size=18, color=COLORS["accent"]),
            rx.text(
                epic["title"],
                font_size="16px",
                font_weight="700",
                color=COLORS["text"],
                flex="1",
                font_family="'Cabinet Grotesk', sans-serif",
            ),
            status_badge(epic["status"]),
            priority_badge(epic["priority"]),
            rx.cond(
                epic["domain"] != "",
                rx.badge(
                    epic["domain"],
                    color_scheme="gray",
                    variant="surface",
                    size="1",
                ),
                rx.fragment(),
            ),
            rx.icon_button(
                rx.icon("plus", size=14),
                size="2",
                variant="ghost",
                color_scheme="teal",
                title="Add Project",
                on_click=WorkState.open_new_drawer("project", epic["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=14),
                size="2",
                variant="ghost",
                color_scheme="gray",
                on_click=WorkState.open_drawer("epic", epic["id"]),
            ),
            align="center",
            spacing="2",
            padding="12px 16px",
            border_radius="8px",
            background_color=COLORS["surface"],
            border=f"1px solid {COLORS['border']}",
            width="100%",
        ),

        # Projects under epic
        projects_for_epic(epic),

        width="100%",
        margin_bottom="16px",
        padding="8px",
        border_radius="8px",
        background_color="rgba(251, 113, 133, 0.04)",
    )


def work_tree() -> rx.Component:
    """Full collapsible work hierarchy tree."""
    return rx.box(
        rx.foreach(
            WorkState.epics,
            epic_section,
        ),
        width="100%",
    )


def kanban_task_card(task: dict) -> rx.Component:
    """A single task card in kanban view."""
    return rx.box(
        rx.hstack(
            rx.text(
                task["title"],
                font_size="13px",
                color=COLORS["text"],
                flex="1",
            ),
            rx.icon_button(
                rx.icon("pencil", size=10),
                size="1",
                variant="ghost",
                color_scheme="gray",
                on_click=WorkState.open_drawer("task", task["id"]),
            ),
            align="start",
            spacing="2",
        ),
        rx.hstack(
            status_badge(task["status"]),
            priority_badge(task["priority"]),
            spacing="2",
            margin_top="8px",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="6px",
        padding="10px 12px",
        margin_bottom="8px",
        _hover={"border_color": COLORS["primary"]},
        cursor="pointer",
    )


def kanban_column(status: str) -> rx.Component:
    """Single Kanban column for a given status."""
    return rx.box(
        rx.text(
            status.upper(),
            font_size="12px",
            font_weight="700",
            color=COLORS["muted"],
            letter_spacing="0.06em",
            margin_bottom="12px",
        ),
        rx.foreach(
            WorkState.tasks,
            lambda task: rx.cond(
                task["status"] == status,
                kanban_task_card(task),
                rx.fragment(),
            ),
        ),
        min_width="240px",
        flex="1",
        background_color=COLORS["surface2"],
        border_radius="8px",
        padding="12px",
        min_height="400px",
    )


def kanban_board() -> rx.Component:
    """Kanban board view of tasks by status."""
    return rx.hstack(
        kanban_column("In Progress"),
        kanban_column("Planned"),
        kanban_column("Completed"),
        kanban_column("Blocked"),
        kanban_column("On Hold"),
        spacing="4",
        width="100%",
        overflow_x="auto",
        align="start",
    )
