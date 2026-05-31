# ==============================================================================
# File: lifeos/views/management_modals.py
# Description: Pop-up interfaces for the Management Hub.
# Component: View Layer
# ==============================================================================

import reflex as rx
from lifeos.states.management import ManagementState, LIFE_DOMAINS



def task_assignment_modal() -> rx.Component:
    """The pop-up form that lets you route a task to a specific project."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Route Task"),
            rx.dialog.description("Assign this inbox item to an active project.", size="2", mb="4"),
            
            rx.flex(
                rx.text("Target Project", as_="div", size="2", mb="1", weight="bold"),
                # We dynamically map your active projects into the dropdown!
                rx.select(
                    ManagementState.active_project_titles,
                    value=ManagementState.target_project_id,
                    on_change=ManagementState.set_target_project_id,
                    placeholder="Select a project...",
                    size="3"
                ),
                direction="column", spacing="3",
            ),
            
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancel", color_scheme="gray", variant="soft", on_click=ManagementState.close_assignment_modal)
                ),
                rx.dialog.close(
                    rx.button("Route Task", on_click=ManagementState.assign_task_to_project)
                ),
                spacing="3", mt="4", justify="end",
            ),
            max_width="400px",
        ),
        open=ManagementState.assignment_modal_open,
    )
def task_inspector_panel() -> rx.Component:
    """A universal slide-out panel bound to the Draft Board for safe editing."""
    return rx.cond(
        ManagementState.is_inspector_open,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon(tag="settings-2", size=20, color_scheme="indigo"),
                    
                    # --- NEW POLISH: Dynamic Title! ---
                    rx.text(
                        f"Edit {ManagementState.inspector_entity_type}", 
                        text_transform="capitalize", 
                        weight="bold", 
                        size="4"
                    ),
                    
                    rx.spacer(),
                    rx.icon_button(rx.icon(tag="x"), variant="ghost", color_scheme="gray", on_click=ManagementState.close_inspector),
                    width="100%", align="center", border_bottom="1px solid var(--gray-4)", padding_bottom="3"
                ),
                
                # The Draft Forms
                rx.text("Title", size="2", weight="bold", margin_top="4"),
                rx.input(value=ManagementState.draft_title, on_change=ManagementState.set_draft_title, width="100%"),
                
                rx.text("Life Domain", size="2", weight="bold", margin_top="3"),
                rx.select(
                    LIFE_DOMAINS,
                    value=ManagementState.draft_domain,
                    on_change=ManagementState.set_draft_domain,
                    width="100%"
                ),
                
                rx.text("Estimated Time", size="2", weight="bold", margin_top="3"),
                rx.input(
                    value=ManagementState.draft_estimated_time_str, 
                    on_change=ManagementState.set_draft_estimated_time_str, 
                    placeholder="e.g. 2w, 3d, 4h, 30m",
                    width="100%"
                ),
                
                rx.spacer(),
                
                # Action Buttons
                rx.hstack(
                    rx.button("Discard", variant="soft", color_scheme="gray", on_click=ManagementState.close_inspector, flex="1"),
                    rx.button("Save Changes", color_scheme="indigo", on_click=ManagementState.save_inspector_changes, flex="1"),
                    width="100%", padding_top="4", spacing="3"
                ),
                
                height="100%", width="100%", align_items="start"
            ),
            # Slide-out CSS Styling
            position="fixed", top="0", right="0", height="100vh", width="400px", 
            background_color="var(--color-panel-solid)", box_shadow="-4px 0 15px rgba(0,0,0,0.5)",
            padding="5", z_index="999", border_left="1px solid var(--gray-5)"
        )
    )
def quick_capture_modal() -> rx.Component:
    """A centered, frictionless modal for dumping new tasks into the Inbox."""
    return rx.cond(
        ManagementState.is_capture_open,
        # Background Overlay (Dims the rest of the app)
        rx.box(
            # The Modal Card
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="zap", color_scheme="yellow"),
                    rx.text("Quick Capture", weight="bold", size="4"),
                    rx.spacer(),
                    rx.icon_button(rx.icon(tag="x"), variant="ghost", color_scheme="gray", on_click=ManagementState.close_capture),
                    width="100%", align="center", padding_bottom="3"
                ),
                
                # The Input
                rx.input(
                    placeholder="What's on your mind?",
                    value=ManagementState.capture_title,
                    on_change=ManagementState.set_capture_title,
                    width="100%",
                    size="3", # Make it nice and big!
                ),
                
                # Action Buttons
                rx.hstack(
                    rx.button("Cancel", variant="soft", color_scheme="gray", on_click=ManagementState.close_capture, flex="1"),
                    rx.button("Capture Task", color_scheme="indigo", on_click=ManagementState.save_capture, flex="1"),
                    width="100%", padding_top="4", spacing="3"
                ),
                
                # Modal Card Styling
                background_color="var(--color-panel-solid)",
                padding="5",
                border_radius="md",
                box_shadow="0 4px 20px rgba(0,0,0,0.3)",
                width="400px",
                border="1px solid var(--gray-5)"
            ),
            
            # Overlay Styling (Centers the modal on screen)
            position="fixed", top="0", left="0", width="100vw", height="100vh",
            background_color="rgba(0,0,0,0.5)",
            display="flex", align_items="center", justify_content="center",
            z_index="1000", backdrop_filter="blur(2px)"
        )
    )