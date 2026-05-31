# ==============================================================================
# File: lifeos/views/habits_dashboard.py
# Description: The Macro Dashboard for forging and managing Habit Blueprints.
# Component: Habit Engine (UI Layer)
# Version: 1.0 (Gold Master)
# Created: 2026-04-26
# Last Update: 2026-04-26
# ==============================================================================

import reflex as rx
from lifeos.state import State
from lifeos.models.habitat import LifeHabit
from lifeos.states.habits import HabitState

def habit_blueprint_row(habit: LifeHabit) -> rx.Component:
    """Renders a single blueprint in the management grid."""
    
    # The Universal Taxonomy Engine
    domain_color = rx.match(
        habit.domain,
        ("HOME", "grass"),
        ("TECH", "slate"),
        ("ACADEMY", "sky"),
        ("THEATER", "plum"),
        ("GOVERNANCE", "amber"),
        "gray"
    )

    return rx.table.row(
        rx.table.cell(rx.text(habit.title, weight="medium")),
        rx.table.cell(rx.badge(habit.domain, color_scheme=domain_color, variant="surface")),
        rx.table.cell(
            rx.cond(
                habit.is_numeric,
                rx.badge(f"Target: {habit.target_value} {habit.unit_label}", color_scheme="blue", variant="soft"),
                rx.badge("Binary (Done/Not Done)", color_scheme="gray", variant="outline")
            )
        ),
        rx.table.cell(
            rx.cond(
                habit.is_active,
                rx.badge("Active", color_scheme="grass"),
                rx.badge("Archived", color_scheme="gray")
            )
        ),
    )

@rx.page(route="/habits", title="Habit Engine", on_load=HabitState.load_telemetry)
def habits_dashboard_view() -> rx.Component:
    return rx.container(
        rx.vstack(
            # --- HEADER & NAVIGATION ---
            rx.hstack(
                rx.heading("Habit Engine", size="7"),
                rx.spacer(),
                rx.button(
                    rx.icon(tag="satellite", size=18),
                    "Mission Control",
                    on_click=rx.redirect("/"),
                    color_scheme="grass", variant="ghost", size="3", cursor="pointer",
                ),
                width="100%", align_items="center"
            ),
            
            # --- THE FORGE (Creation Form) ---
            rx.card(
                rx.vstack(
                    rx.heading("Forge New Blueprint", size="4", margin_bottom="2"),
                    rx.hstack(
                        rx.input(placeholder="Habit Title (e.g., Tenor Sax Practice)", value=State.new_habit_title, on_change=State.set_new_habit_title, width="40%"),
                        rx.select(["HOME", "TECH", "ACADEMY", "THEATER", "GOVERNANCE"], value=State.new_habit_domain, on_change=State.set_new_habit_domain, width="20%"),
                        rx.checkbox("Track Numbers?", checked=State.new_habit_is_numeric, on_change=State.set_new_habit_is_numeric, color_scheme="blue"),
                        width="100%", align_items="center", spacing="3"
                    ),
                    # Conditional Numeric Inputs
                    rx.cond(
                        State.new_habit_is_numeric,
                        rx.hstack(
                            rx.input(placeholder="Target Value (e.g., 45)", value=State.new_habit_target_str, on_change=State.set_new_habit_target_str, width="150px"),
                            rx.input(placeholder="Unit (e.g., minutes, peppers)", value=State.new_habit_unit, on_change=State.set_new_habit_unit, width="200px"),
                            spacing="3"
                        )
                    ),
                    rx.button("Forge Blueprint", on_click=State.save_new_habit, color_scheme="grass", margin_top="2"),
                    align_items="start", width="100%"
                ),
                width="100%", variant="surface", padding="4", margin_bottom="4"
            ),

            # --- THE BLUEPRINT MANIFEST (Grid) ---
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Blueprint Title"),
                        rx.table.column_header_cell("Domain"),
                        rx.table.column_header_cell("Telemetry Type"),
                        rx.table.column_header_cell("Status"),
                    )
                ),
                rx.table.body(
                    rx.foreach(State.active_habits, habit_blueprint_row)
                ),
                width="100%", variant="surface"
            ),
            
            width="100%", spacing="4",
        ),
        padding="2rem", max_width="1200px",
    )