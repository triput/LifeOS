"""Academy tree: Specialization → Course → Module → Task."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.academy_state import AcademyState
from lifeos.components.badges import status_badge, activity_type_badge

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
# 2. HIERARCHICAL TREE COMPONENTS
# ==============================================================================

def learning_task_row(task: dict) -> rx.Component:
    """Single learning task row with rich data."""
    # Note: Assuming your DB column is 'is_completed' or 'status'. Adjust if needed!
    is_done = task.contains("is_completed") & task["is_completed"]
    
    return rx.hstack(
        rx.checkbox(
            checked=is_done,
            # Assuming toggle_learning_task expects the ID
            on_change=lambda val: AcademyState.toggle_learning_task(task["id"].to(int)),
            color_scheme="teal",
        ),
        rx.text(
            task["title"],
            font_size="14px", font_weight="500", flex="1",
            color=rx.cond(is_done, COLORS["muted"], COLORS["text"]),
            text_decoration=rx.cond(is_done, "line-through", "none")
        ),
        activity_type_badge(task["activity_type"]),
        time_metrics_badges(task), # INJECTED RICH DATA
        rx.icon_button(
            rx.icon("pencil", size=12), size="1", variant="ghost", color_scheme="gray",
            # Assuming your drawer type for these is 'task' or 'learning_task'
            on_click=AcademyState.open_drawer("learning_task", task["id"].to(int)), 
        ),
        align="center", spacing="2", padding="8px 12px", border_radius="6px",
        _hover={"background_color": COLORS["surface2"]}, width="100%",
    )

def tasks_for_module(module: dict) -> rx.Component:
    """Loops through tasks and renders only those belonging to this Module."""
    return rx.box(
        rx.foreach(
            # Make sure your AcademyState has a variable named 'tasks' (or 'learning_tasks')!
            AcademyState.tasks, 
            lambda t: rx.cond(t["module_id"] == module["id"], learning_task_row(t), rx.fragment()),
        ),
        padding_left="32px", border_left=f"1px solid {COLORS['border']}", margin_left="16px",
    )

def module_card(module: dict) -> rx.Component:
    """Renders a Module and its nested Tasks."""
    return rx.box(
        rx.hstack(
            rx.icon("book-open", size=14, color=COLORS["primary"]),
            rx.text(module["title"], font_size="14px", font_weight="600", color=COLORS["text"], flex="1"),
            time_metrics_badges(module), # INJECTED RICH DATA
            status_badge(module["status"]),
            rx.icon_button(
                rx.icon("plus", size=12), size="1", variant="ghost", color_scheme="teal",
                on_click=AcademyState.open_new_drawer("task", module["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=12), size="1", variant="ghost", color_scheme="gray",
                on_click=AcademyState.open_drawer("module", module["id"]),
            ),
            align="center", spacing="2", padding="8px 12px", border_radius="6px",
            background_color=COLORS["surface2"], _hover={"background_color": "#252e42"}, width="100%",
        ),
        # THE FIX: Nested tasks now successfully render!
        tasks_for_module(module), 
        width="100%", margin_bottom="8px",
    )

def modules_for_course(course: dict) -> rx.Component:
    """Loops through modules and renders only those belonging to this Course."""
    return rx.box(
        rx.foreach(
            AcademyState.modules,
            lambda mod: rx.cond(mod["course_id"] == course["id"], module_card(mod), rx.fragment()),
        ),
        padding_left="16px", border_left=f"2px solid {COLORS['border']}",
        margin_left="20px", margin_top="4px",
    )

def course_card(course: dict) -> rx.Component:
    """Renders a Course and its nested Modules."""
    return rx.box(
        rx.hstack(
            rx.icon("layers", size=16, color=COLORS["warning"]),
            rx.text(course["title"], font_size="15px", font_weight="600", color=COLORS["text"], flex="1"),
            time_metrics_badges(course), # INJECTED RICH DATA
            status_badge(course["status"]),
            rx.icon_button(
                rx.icon("plus", size=12), size="1", variant="ghost", color_scheme="teal",
                on_click=AcademyState.open_new_drawer("module", course["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=12), size="1", variant="ghost", color_scheme="gray",
                on_click=AcademyState.open_drawer("course", course["id"]),
            ),
            align="center", spacing="2", padding="8px 12px", border_radius="6px",
            background_color=COLORS["surface"], border=f"1px solid {COLORS['border']}", width="100%",
        ),
        modules_for_course(course),
        width="100%", margin_bottom="12px",
    )

def courses_for_specialization(spec: dict) -> rx.Component:
    """Loops through courses and renders only those belonging to this Specialization."""
    return rx.box(
        rx.foreach(
            AcademyState.courses,
            lambda course: rx.cond(course["specialization_id"] == spec["id"], course_card(course), rx.fragment()),
        ),
        padding_left="16px", border_left=f"2px solid {COLORS['accent']}",
        margin_left="8px", margin_top="8px", padding_top="4px",
    )

def specialization_section(spec: dict) -> rx.Component:
    """Renders a Specialization and its nested Courses."""
    return rx.box(
        rx.hstack(
            rx.icon("award", size=18, color=COLORS["accent"]),
            rx.text(
                spec["title"], font_size="16px", font_weight="700", color=COLORS["text"], flex="1",
                font_family="'Cabinet Grotesk', sans-serif",
            ),
            time_metrics_badges(spec), # INJECTED RICH DATA
            status_badge(spec["status"]),
            rx.cond(
                spec["provider"] != "",
                rx.badge(spec["provider"], color_scheme="teal", variant="soft", size="1"),
                rx.fragment(),
            ),
            rx.icon_button(
                rx.icon("plus", size=14), size="2", variant="ghost", color_scheme="teal",
                on_click=AcademyState.open_new_drawer("course", spec["id"]),
            ),
            rx.icon_button(
                rx.icon("pencil", size=14), size="2", variant="ghost", color_scheme="gray",
                on_click=AcademyState.open_drawer("specialization", spec["id"]),
            ),
            align="center", spacing="2", padding="12px 16px", border_radius="8px",
            background_color=COLORS["surface"], border=f"1px solid {COLORS['border']}", width="100%",
        ),
        courses_for_specialization(spec),
        width="100%", margin_bottom="16px", padding="8px", border_radius="8px",
        background_color="rgba(45, 212, 191, 0.04)", # Academy Teal tint
    )

def academy_tree() -> rx.Component:
    """Full academy hierarchy tree."""
    return rx.box(
        rx.foreach(AcademyState.specializations, specialization_section),
        width="100%",
    )