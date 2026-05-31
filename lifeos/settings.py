# ==============================================================================
# File: lifeos/settings.py
# Description: Configuration and Profile Management for LifeOS.
# Component: Frontend UI (Settings Page)
# Version: 1.1 (Gold Master)
# Created: 2026-04-23
# Last Update: 2026-05-02
# ==============================================================================

import reflex as rx
from lifeos.states.observatory import ObservatoryState

def settings_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.link(rx.icon(tag="arrow-left"), href="/"),
                rx.heading("System Settings", size="8"),
                spacing="4",
                align="center",
            ),
            rx.divider(),
            
            # --- Section: Location Profiles ---
            rx.vstack(
                rx.heading("Active Profile", size="4"),
                rx.text("Select your current base of operations to sync the Observatory.", size="2", color_scheme="gray"),
                rx.segmented_control.root(
                    rx.segmented_control.item("Monroe", value="Monroe"),
                    rx.segmented_control.item("Bangkok", value="Bangkok"),
                    rx.segmented_control.item("Austin", value="Austin"),
                    value=ObservatoryState.active_profile,
                    on_change=ObservatoryState.set_active_profile,
                    size="3",
                ),
                align="start",
                spacing="3",
                padding_y="4",
            ),
            
            # --- Section: Measurement Units ---
            rx.vstack(
                rx.heading("Measurement System", size="4"),
                rx.text("Toggle between Imperial (°F, miles) and Metric (°C, km).", size="2", color_scheme="gray"),
                rx.segmented_control.root(
                    rx.segmented_control.item("Imperial", value="Imperial"),
                    rx.segmented_control.item("Metric", value="Metric"),
                    value=ObservatoryState.unit_system,
                    on_change=ObservatoryState.set_unit_system,
                    size="3",
                ),
                align="start",
                spacing="3",
                padding_y="4",
            ),
            
            # --- Section: Visual Preferences (Future Sprint) ---
            rx.vstack(
                rx.heading("Visual Theme", size="4"),
                rx.text("Adjust jewel tones and interface contrast.", size="2", color_scheme="gray"),
                rx.button("Coming Soon", variant="soft", disabled=True),
                align="start",
                spacing="3",
            ),
            
            spacing="7",
            width="100%",
        ),
        padding="6",
    )