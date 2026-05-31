# ==============================================================================
# File: lifeos/views/triage_inbox.py
# Description: Rapid-capture UI for dumping items into the Backlog.
# Component: View Layer
# ==============================================================================

import reflex as rx
from lifeos.states.management import ManagementState

def rapid_capture_bar() -> rx.Component:
    """A frictionless input bar to capture Epics, Projects, or Tasks."""
    return rx.card(
        rx.vstack(
            rx.text("Rapid Capture", weight="bold", size="3", color_scheme="gray"),
            rx.hstack(
                # The Main Input
                rx.input(
                    placeholder="What needs to get done? (Press Enter to capture)",
                    value=ManagementState.capture_title,
                    on_change=ManagementState.set_capture_title,
                    width="100%",
                    size="3"
                ),
                
                # Classification Dropdown
                rx.select(
                    ["Task", "Project", "Epic"],
                    value=ManagementState.capture_entity_type,
                    on_change=ManagementState.set_capture_entity_type,
                    color_scheme="indigo",
                    size="3", width="120px"
                ),
                
                # --- NEW: The Epic Selector (Only appears for Projects!) ---
                rx.cond(
                    ManagementState.capture_entity_type == "project",
                    rx.select(
                        ManagementState.active_epic_titles,
                        value=ManagementState.capture_epic_title,
                        on_change=ManagementState.set_capture_epic_title,
                        placeholder="Assign Epic...",
                        size="3", 
                        width="200px" # Keeps the inline bar from getting too wide
                    )
                ),
                
                # Priority Dropdown
                rx.select(
                    ["Low", "Medium", "High", "Critical"],
                    value=ManagementState.new_item_priority,
                    on_change=ManagementState.set_new_item_priority,
                    size="3", width="120px"
                ),
                # Submit Button
                rx.button(
                    rx.icon(tag="zap"), "Capture", 
                    color_scheme="indigo", size="3",
                    on_click=ManagementState.capture_triage_item
                ),
            ),
            width="100%", spacing="3"
        ),
        width="100%", variant="surface", padding="4", margin_bottom="5"
    )