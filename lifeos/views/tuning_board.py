# ==============================================================================
# File: lifeos/views/tuning_board.py
# Description: Visual interface for the Blueprint Factory cadences.
# Component: Frontend / UI Layer
# Version: 1.1 (Gold Master)
# Created: 2026-05-04
# ==============================================================================

import reflex as rx
from lifeos.states.blueprints import BlueprintState, BlueprintItem

# TYPE UPGRADE: Use BlueprintItem instead of dict
def blueprint_row(bp: BlueprintItem) -> rx.Component:
    """Renders a single automated cadence with inline editing."""
    return rx.hstack(
        rx.vstack(
            # Switched to dot notation: bp.title
            rx.text(bp.title, weight="bold", size="3"),
            
            rx.hstack(
                rx.badge(bp.target_type, color_scheme="blue", variant="soft", size="1"),
                rx.text("Every", size="1", color_scheme="gray", weight="medium"),
                rx.input(
                    value=bp.frequency_interval,
                    on_change=lambda v: BlueprintState.update_blueprint_interval(bp.id, v),
                    width="50px", size="1", variant="surface"
                ),
                rx.select(
                    ["Days", "Weeks", "Months", "Quarters", "Years"],
                    value=bp.frequency_unit,
                    on_change=lambda v: BlueprintState.update_blueprint_unit(bp.id, v),
                    variant="surface", size="1"
                ),
                spacing="2", align="center"
            ),
            align_items="start", spacing="1"
        ),
        rx.spacer(),
        
        rx.switch(
            checked=bp.is_active,
            on_change=lambda v: BlueprintState.toggle_active(bp.id, v),
            color_scheme="grass", size="3"
        ),
        width="100%", align="center", padding_y="3", border_bottom="1px solid var(--gray-5)"
    )

def tuning_board_modal() -> rx.Component:
    """The pop-up factory floor for managing recurring tasks."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon(tag="settings-2", size=18), 
                "Tuning Board", 
                variant="soft", color_scheme="gray", size="2"
            )
        ),
        rx.dialog.content(
            rx.dialog.title("Blueprint Factory", size="6"),
            rx.dialog.description("Manage active automation cadences and recurring habits.", padding_bottom="4"),
            
            rx.card(
                rx.scroll_area(
                    rx.cond(
                        BlueprintState.tuning_board_list.length() > 0,
                        rx.vstack(
                            rx.foreach(BlueprintState.tuning_board_list, blueprint_row),
                            width="100%"
                        ),
                        rx.text("No active blueprints found.", color_scheme="gray")
                    ),
                    style={"height": "500px", "padding_right": "15px"}
                ),
                variant="surface", width="100%", padding="4"
            ),
            
            rx.hstack(
                rx.dialog.close(
                    rx.button("Close Factory", variant="soft", color_scheme="gray", size="2")
                ),
                justify="end", padding_top="4", width="100%"
            ),
            max_width="600px"
        )
    )