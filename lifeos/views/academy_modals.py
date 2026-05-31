# ==============================================================================
# File: lifeos/views/academy_modals.py
# Description: Data entry modals for the Academy domain.
# Component: View Layer (Reusable Components)
# ==============================================================================

import reflex as rx
from lifeos.states.academy import AcademyState

def track_constructor_modal() -> rx.Component:
    """The pop-up form for creating new Specializations or Courses."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Construct Learning Track"),
            rx.dialog.description(
                "Define a new Specialization or standalone Course for the Academy.",
                size="2", mb="4",
            ),
            
            # Form Fields
            rx.flex(
                rx.text("Track Title", as_="div", size="2", mb="1", weight="bold"),
                rx.input(placeholder="e.g., Prompt Engineering for Devs", value=AcademyState.new_track_title, on_change=AcademyState.set_new_track_title),
                
                rx.text("Provider", as_="div", size="2", mb="1", mt="3", weight="bold"),
                rx.input(placeholder="e.g., DeepLearning.AI, Coursera", value=AcademyState.new_track_provider, on_change=AcademyState.set_new_track_provider),
                
                # Two Select Dropdowns side-by-side
                rx.hstack(
                    rx.vstack(
                        rx.text("Track Type", as_="div", size="2", mb="1", weight="bold"),
                        rx.select(
                            ["Specialization", "Standalone Course"],
                            value=AcademyState.new_track_type,
                            on_change=AcademyState.set_new_track_type,
                        ),
                        width="100%", align_items="start"
                    ),
                    rx.vstack(
                        rx.text("Initial Status", as_="div", size="2", mb="1", weight="bold"),
                        rx.select(
                            ["Planned", "In Progress"],
                            value=AcademyState.new_track_status,
                            on_change=AcademyState.set_new_track_status,
                        ),
                        width="100%", align_items="start"
                    ),
                    width="100%", mt="3", spacing="3"
                ),
                direction="column",
                spacing="3",
            ),
            
            # Action Buttons
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancel", color_scheme="gray", variant="soft", on_click=AcademyState.toggle_track_modal),
                ),
                rx.dialog.close(
                    rx.button("Deploy Track", on_click=AcademyState.submit_new_track),
                ),
                spacing="3", mt="4", justify="end",
            ),
            max_width="450px",
        ),
        open=AcademyState.track_modal_open,
        on_open_change=AcademyState.set_track_modal_open,
    )
    
def nested_course_constructor_modal() -> rx.Component:
    """The pop-up form for adding a Course to a Specialization."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Add Course to Specialization"),
            rx.flex(
                rx.text("Course Title", as_="div", size="2", mb="1", weight="bold"),
                rx.input(placeholder="e.g., Prompt Engineering Basics", value=AcademyState.new_nested_course_title, on_change=AcademyState.set_new_nested_course_title),
                
                rx.text("Provider", as_="div", size="2", mb="1", mt="3", weight="bold"),
                rx.input(placeholder="e.g., Coursera", value=AcademyState.new_nested_course_provider, on_change=AcademyState.set_new_nested_course_provider),
                
                direction="column", spacing="3",
            ),
            rx.flex(
                rx.dialog.close(rx.button("Cancel", color_scheme="gray", variant="soft", on_click=AcademyState.close_course_modal)),
                rx.dialog.close(rx.button("Save Course", on_click=AcademyState.submit_new_nested_course)),
                spacing="3", mt="4", justify="end",
            ),
            max_width="400px",
        ),
        open=AcademyState.course_modal_open,
    )
    
def module_constructor_modal() -> rx.Component:
    """The pop-up form for adding a Module to a Course."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Add New Module"),
            rx.flex(
                rx.text("Module Title", as_="div", size="2", mb="1", weight="bold"),
                rx.input(placeholder="e.g., Week 1: Core Concepts", value=AcademyState.new_module_title, on_change=AcademyState.set_new_module_title),
                direction="column", spacing="3",
            ),
            rx.flex(
                rx.dialog.close(rx.button("Cancel", color_scheme="gray", variant="soft", on_click=AcademyState.close_module_modal)),
                rx.dialog.close(rx.button("Save Module", on_click=AcademyState.submit_new_module)),
                spacing="3", mt="4", justify="end",
            ),
            max_width="400px",
        ),
        open=AcademyState.module_modal_open,
    )

def activity_constructor_modal() -> rx.Component:
    """The pop-up form for adding an Activity to a Module."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Add Learning Activity"),
            rx.flex(
                rx.text("Activity Title", as_="div", size="2", mb="1", weight="bold"),
                rx.input(placeholder="e.g., Intro to Neural Networks", value=AcademyState.new_activity_title, on_change=AcademyState.set_new_activity_title),
                
                rx.hstack(
                    rx.vstack(
                        rx.text("Type", as_="div", size="2", mb="1", weight="bold"),
                        rx.select(["Video", "Reading", "Quiz", "Lab"], value=AcademyState.new_activity_type, on_change=AcademyState.set_new_activity_type),
                        width="100%", align_items="start"
                    ),
                    rx.vstack(
                        rx.text("Est. Minutes", as_="div", size="2", mb="1", weight="bold"),
                        rx.input(placeholder="15", value=AcademyState.new_activity_duration, on_change=AcademyState.set_new_activity_duration),
                        width="100%", align_items="start"
                    ),
                    width="100%", mt="3", spacing="3"
                ),
                direction="column", spacing="3",
            ),
            rx.flex(
                rx.dialog.close(rx.button("Cancel", color_scheme="gray", variant="soft", on_click=AcademyState.close_activity_modal)),
                rx.dialog.close(rx.button("Save Activity", on_click=AcademyState.submit_new_activity)),
                spacing="3", mt="4", justify="end",
            ),
            max_width="450px",
        ),
        open=AcademyState.activity_modal_open,
    )