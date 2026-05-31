# ==============================================================================
# File: lifeos/views/modals.py
# Description: Pop-up interfaces for rapid data entry.
# Component: Frontend / UI Layer
# Version: 1.0 (Gold Master)
# ==============================================================================

import reflex as rx
from lifeos.states.tasks import TaskState

def quick_add_modal() -> rx.Component:
    """The 'Front Door' Lightning Capture with Temporal Boundaries."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(rx.icon(tag="plus", size=24), "Capture", color_scheme="grass", position="fixed", bottom="2rem", right="2rem", padding="1.5rem", border_radius="full", z_index="100")
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Lightning Capture"),
                rx.input(placeholder="Title...", on_change=TaskState.set_new_task_title, value=TaskState.new_task_title, width="100%"),
                rx.select(
                    ["HOME", "TECH", "ACADEMY", "THEATER", "GOVERNANCE"],
                    placeholder="Select Domain",
                    on_change=TaskState.set_new_task_domain, 
                    color_scheme="grass", width="100%",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Start Date", size="1", color_scheme="gray"),
                        rx.input(type="date", on_change=TaskState.set_new_task_start_date, value=TaskState.new_task_start_date, width="100%"),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Due Date", size="1", color_scheme="gray"),
                        rx.input(type="date", on_change=TaskState.set_new_task_due_date, value=TaskState.new_task_due_date, width="100%"),
                        width="100%",
                    ),
                    spacing="3", width="100%",
                ),
                rx.text_area(placeholder="Notes...", on_change=TaskState.set_new_task_desc, value=TaskState.new_task_desc, width="100%"),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancel", variant="soft")),
                    rx.button("Save to Triage", color_scheme="grass", on_click=TaskState.save_new_task),
                    justify="end", width="100%"
                ),
                spacing="4",
            ),
            max_width="450px",
        ),
    )