# ==============================================================================
# File: lifeos/views/telemetry.py
# Description: Daily tracking and automated process monitoring.
# Component: Frontend / UI Layer
# Version: 1.1 (Gold Master)
# Created: 2026-05-02
# Last Update: 2026-05-03
# ==============================================================================

import reflex as rx
from lifeos.states.habits import HabitState

def daily_habit_row(habit: dict) -> rx.Component:
    """Renders a single actionable habit item."""
    return rx.hstack(
        rx.checkbox(
            checked=habit["is_completed"],
            on_change=lambda _: HabitState.toggle_habit(habit["id"]),
            size="2", color_scheme="grass"
        ),
        rx.text(habit["title"], size="2", weight="medium", text_decoration=rx.cond(habit["is_completed"], "line-through", "none")),
        width="100%", align="center", padding_y="1"
    )

def telemetry_widget() -> rx.Component:
    """The daily check-in board."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                # NEW: Visual Icon added to the header
                rx.icon(tag="list-checks", color="var(--grass-9)"),
                rx.text("Daily Telemetry", weight="bold", size="3"),
                align="center",
            ),
            rx.divider(),
            rx.cond(
                HabitState.telemetry_data.length() > 0,
                rx.vstack(rx.foreach(HabitState.telemetry_data, daily_habit_row), width="100%", spacing="1"),
                rx.text("No daily habits configured.", color_scheme="gray", size="2")
            ),
            width="100%"
        ),
        width="100%"
    )