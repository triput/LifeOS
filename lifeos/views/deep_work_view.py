# ==============================================================================
# File: lifeos/views/deep_work_view.py
# Description: The distraction-free focus page for a single Project.
# Component: View Layer
# ==============================================================================

import reflex as rx
from lifeos.states.deep_work import DeepWorkState

def render_focus_task(task: dict) -> rx.Component:
    """Renders a single task inside the Deep Work view."""
    return rx.card(
        rx.hstack(
            # 1. The Interactive "Complete" Toggle Button
            rx.icon_button(
                rx.icon(
                    tag=rx.cond(task["status"] == "Done", "check-circle", "circle"), 
                    size=20
                ),
                variant="ghost",
                color_scheme=rx.cond(task["status"] == "Done", "green", "gray"),
                cursor="pointer",
                # NEW: Pass the ID and the current status to our smart toggle
                on_click=lambda: DeepWorkState.toggle_task_completion(task["id"], task["status"])
            ),
            rx.text(
                task["title"], 
                size="3", 
                weight="medium",
                # Strikethrough if done
                text_decoration=rx.cond(task["status"] == "Done", "line-through", "none"),
                color=rx.cond(task["status"] == "Done", "var(--gray-10)", "inherit")
            ),
            rx.spacer(),
            rx.badge(task["status"], color_scheme="blue", variant="soft"),
            rx.badge(task["priority"], color_scheme="orange", variant="outline"),
            
            width="100%", align="center", padding_y="2"
        ),
        width="100%", margin_bottom="3", variant="surface"
    )

def deep_work_page() -> rx.Component:
    """The master layout for the dynamic /project/[id] route."""
    return rx.container(
        rx.vstack(
            # --- HEADER SECTION ---
            rx.hstack(
                # A quick back button to return to Mission Control
                rx.link(
                    rx.icon_button(rx.icon(tag="arrow-left"), variant="soft", color_scheme="gray"),
                    href="/backlog"
                ),
                rx.vstack(
                    rx.heading(DeepWorkState.active_project_title, size="8", weight="bold"),
                    rx.badge(DeepWorkState.active_project_domain, color_scheme="indigo"),
                    align_items="start", spacing="1"
                ),
                align="center", width="100%", spacing="4", padding_bottom="4", border_bottom="1px solid var(--gray-5)"
            ),
            
            # --- PROGRESS SECTION ---
            rx.vstack(
                rx.hstack(
                    rx.text("Project Completion", weight="bold", color_scheme="gray"),
                    rx.spacer(),
                    rx.text(f"{DeepWorkState.completion_percentage}%", weight="bold", color_scheme="green"),
                    width="100%"
                ),
                rx.progress(value=DeepWorkState.completion_percentage, color_scheme="green", width="100%"),
                width="100%", padding_y="6"
            ),
            
            # --- TASK EXECUTION LIST ---
            rx.heading("Active Tasks", size="4", weight="bold", margin_bottom="4"),
            rx.cond(
                DeepWorkState.project_tasks.length() > 0,
                rx.vstack(
                    rx.foreach(DeepWorkState.project_tasks, render_focus_task),
                    width="100%"
                ),
                rx.box(
                    rx.text("No tasks mapped to this project yet.", color_scheme="gray"),
                    padding="8", width="100%", text_align="center", border="1px dashed var(--gray-5)", border_radius="md"
                )
            ),
            
            width="100%", max_width="800px", margin="0 auto", padding_top="8"
        ),
        size="4"
    )
    
    