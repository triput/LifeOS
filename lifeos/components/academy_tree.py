"""Academy tree: Specialization → Course → Module → Learning Task."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.academy_state import AcademyState
from lifeos.components.badges import status_badge, activity_type_badge


def learning_task_row(lt: dict) -> rx.Component:
    """Single learning task row."""
    return rx.hstack(
        rx.checkbox(
            checked=lt["is_completed"],
            on_change=AcademyState.toggle_learning_task(lt["id"]),
            color_scheme="teal",
        ),
        activity_type_badge(lt["activity_type"]),
        rx.text(
            lt["title"],
            font_size="13px",
            color=rx.cond(lt["is_completed"], COLORS["muted"], COLORS["text"]),
            text_decoration=rx.cond(lt["is_completed"], "line-through", "none"),
            flex="1",
        ),
        rx.text(
            lt["estimated_minutes"].to_string() + "m",
            font_size="11px",
            color=COLORS["muted"],
        ),
        rx.icon_button(
            rx.icon("pencil", size=11),
            size="1",
            variant="ghost",
            color_scheme="gray",
            on_click=AcademyState.open_drawer("learning_task", lt["id"]),
        ),
        align="center",
        spacing="2",
        padding="6px 8px",
        border_radius="4px",
        _hover={"background_color": COLORS["surface2"]},
        width="100%",
    )


def tasks_for_module(module: dict) -> rx.Component:
    """Show learning tasks for a module."""
    return rx.box(
        rx.foreach(
            AcademyState.learning_tasks,
            lambda lt: rx.cond(
                lt["module_id"] == module["id"],
                learning_task_row(lt),
                rx.fragment(),
            ),
        ),
        padding_left="16px",
        border_left=f"1px solid {COLORS['border']}",
        margin_left="12px",
        margin_top="4px",
    )


def module_section(module: dict) -> rx.Component:
    """Module with its learning tasks."""
    return rx.box(
        rx.hstack(
            rx.icon("layers", size=14, color=COLORS["warning"]),
            rx.text(
                module["title"],
                font_size="14px",
                font_weight="600",
                color=COLORS["text"],
                flex="1",
            ),
            status_badge(module["status"]),
            rx.icon_button(
                rx.icon("plus", size=11),
                size="1",
                variant="ghost",
                color_scheme="teal",
                on_click=AcademyState.open_new_drawer("learning_task", module["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=11),
                size="1",
                variant="ghost",
                color_scheme="gray",
                on_click=AcademyState.open_drawer("module", module["id"]),
            ),
            align="center",
            spacing="2",
            padding="6px 10px",
            border_radius="6px",
            background_color=COLORS["surface2"],
            _hover={"background_color": "#252e42"},
            width="100%",
        ),
        tasks_for_module(module),
        width="100%",
        margin_bottom="6px",
    )


def modules_for_course(course: dict) -> rx.Component:
    """Show modules for a course."""
    return rx.box(
        rx.foreach(
            AcademyState.modules,
            lambda mod: rx.cond(
                mod["course_id"] == course["id"],
                module_section(mod),
                rx.fragment(),
            ),
        ),
        padding_left="16px",
        border_left=f"2px solid {COLORS['border']}",
        margin_left="16px",
        margin_top="6px",
    )


def course_section(course: dict) -> rx.Component:
    """Course with its modules."""
    return rx.box(
        rx.hstack(
            rx.icon("book-open", size=15, color=COLORS["primary"]),
            rx.text(
                course["title"],
                font_size="15px",
                font_weight="600",
                color=COLORS["text"],
                flex="1",
            ),
            status_badge(course["status"]),
            rx.cond(
                course["provider"] != "",
                rx.badge(
                    course["provider"],
                    color_scheme="gray",
                    variant="surface",
                    size="1",
                ),
                rx.fragment(),
            ),
            rx.icon_button(
                rx.icon("plus", size=12),
                size="1",
                variant="ghost",
                color_scheme="teal",
                on_click=AcademyState.open_new_drawer("module", course["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=12),
                size="1",
                variant="ghost",
                color_scheme="gray",
                on_click=AcademyState.open_drawer("course", course["id"]),
            ),
            align="center",
            spacing="2",
            padding="8px 12px",
            border_radius="6px",
            background_color=COLORS["surface"],
            border=f"1px solid {COLORS['border']}",
            width="100%",
        ),
        modules_for_course(course),
        width="100%",
        margin_bottom="10px",
    )


def courses_for_specialization(spec: dict) -> rx.Component:
    """Show courses for a specialization."""
    return rx.box(
        rx.foreach(
            AcademyState.courses,
            lambda course: rx.cond(
                course["specialization_id"] == spec["id"],
                course_section(course),
                rx.fragment(),
            ),
        ),
        padding_left="16px",
        border_left=f"2px solid {COLORS['primary']}",
        margin_left="8px",
        margin_top="8px",
        padding_top="4px",
    )


def specialization_block(spec: dict) -> rx.Component:
    """Full specialization block with courses, modules, and tasks."""
    return rx.box(
        rx.hstack(
            rx.icon("star", size=18, color=COLORS["primary"]),
            rx.text(
                spec["title"],
                font_size="16px",
                font_weight="700",
                color=COLORS["text"],
                flex="1",
                font_family="'Cabinet Grotesk', sans-serif",
            ),
            status_badge(spec["status"]),
            rx.cond(
                spec["provider"] != "",
                rx.badge(spec["provider"], color_scheme="teal", variant="soft", size="1"),
                rx.fragment(),
            ),
            rx.icon_button(
                rx.icon("plus", size=14),
                size="2",
                variant="ghost",
                color_scheme="teal",
                on_click=AcademyState.open_new_drawer("course", spec["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=14),
                size="2",
                variant="ghost",
                color_scheme="gray",
                on_click=AcademyState.open_drawer("specialization", spec["id"]),
            ),
            align="center",
            spacing="2",
            padding="12px 16px",
            border_radius="8px",
            background_color=COLORS["surface"],
            border=f"1px solid {COLORS['border']}",
            width="100%",
        ),
        courses_for_specialization(spec),
        width="100%",
        margin_bottom="16px",
        padding="8px",
        border_radius="8px",
        background_color="rgba(45, 212, 191, 0.04)",
    )


def academy_tree() -> rx.Component:
    """Full academy hierarchy tree."""
    return rx.box(
        rx.foreach(
            AcademyState.specializations,
            specialization_block,
        ),
        width="100%",
    )
