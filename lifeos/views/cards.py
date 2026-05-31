# ==============================================================================
# File: lifeos/views/cards.py
# Description: Visual components for Task management and Habitat Health.
# Component: Frontend / UI Layer
# Version: 1.1 (Gold Master)
# Created: 2026-05-02
# Last Update: 2026-05-03
# ==============================================================================

import reflex as rx
from lifeos.states.tasks import TaskState

def habitat_stat_item(label: str, value: rx.Var, color: str) -> rx.Component:
    """A high-visibility signal for the Habitat Health card."""
    return rx.vstack(
        rx.text(label, size="1", weight="bold", color_scheme="gray", margin_bottom="-1"),
        rx.heading(value.to_string(), size="6", color_scheme=color, weight="bold"),
        spacing="1", align="center",
    )

def habitat_health_card() -> rx.Component:
    """The central telemetry readout for active work streams."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="activity", color="var(--grass-9)"),
                rx.text("Habitat Health", weight="bold", size="3"),
                align="center",
            ),
            rx.divider(),
            rx.hstack(
                habitat_stat_item("CRITICAL", TaskState.critical_tasks_count, "ruby"),
                rx.divider(orientation="vertical"),
                habitat_stat_item("TRIAGE", TaskState.triage_tasks_count, "amber"),
                rx.divider(orientation="vertical"),
                habitat_stat_item("ACTIVE", TaskState.active_tasks_count, "grass"),
                rx.divider(orientation="vertical"),
                habitat_stat_item("BLOCKED", TaskState.blocked_tasks_count, "tomato"),
                justify="between", width="100%", padding_x="2"
            ),
            width="100%",
        ),
        width="100%",
    )

def task_card(task: dict) -> rx.Component:
    """The visual rendering of a single Agile work item."""
    
    # --- 1. BULLETPROOF DATA TRANSLATION ---
    # Intercept legacy database strings and force a strict match for Radix UI
    safe_priority = rx.match(
        task["priority"],
        ("1", "Critical"), ("2", "High"), ("3", "Medium"), ("4", "Low"),
        ("Critical", "Critical"), ("High", "High"), ("Medium", "Medium"), ("Low", "Low"),
        "Medium" # Absolute fallback prevents the blank box crash
    )

    safe_status = rx.match(
        task["status"],
        ("Triage", "Triage"), ("Active", "Active"), ("Blocked", "Blocked"), ("Done", "Done"),
        ("Inbox", "Triage"),
        "Triage" # Absolute fallback
    )

    # --- 2. DYNAMIC COLOR ENGINE ---
    priority_color = rx.match(
        safe_priority,
        ("Critical", "ruby"), ("High", "amber"), ("Medium", "blue"), ("Low", "gray"),
        "gray"
    )

    status_color = rx.match(
        safe_status,
        ("Triage", "amber"), ("Active", "grass"), ("Blocked", "tomato"), ("Done", "gray"),
        "gray"
    )

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(task["domain"], color_scheme="blue", variant="soft", size="1"),
                
                # --- 3. SOLID VARIANT DROPDOWNS ---
                rx.select(
                    ["Critical", "High", "Medium", "Low"], 
                    value=safe_priority,
                    on_change=lambda v: TaskState.update_task_field(task["id"], "priority", v),
                    variant="soft", color_scheme=priority_color, size="1"
                ),
                
                rx.cond(
                    task["start_date"] != "",
                    rx.badge(rx.icon(tag="calendar-check", size=12), task["start_date"], color_scheme="blue", size="1"),
                ),
                rx.cond(
                    task["due_date"] != "",
                    rx.badge(rx.icon(tag="calendar-clock", size=12), task["due_date"], color_scheme="ruby", size="1"),
                ),
                rx.spacer(),
                rx.text(task["age"], size="1", color_scheme="gray"),
                width="100%", align="center", padding_bottom="2",
            ),
            rx.text(task["title"], weight="bold", size="4"),
            rx.hstack(
                rx.select(
                    ["Triage", "Active", "Blocked", "Done"], 
                    value=safe_status, 
                    on_change=lambda v: TaskState.update_task_field(task["id"], "status", v),
                    variant="soft", color_scheme=status_color
                ),
                width="100%", justify="between", padding_top="2"
            ),
            align_items="start", width="100%",
        ),
        width="100%",
    )