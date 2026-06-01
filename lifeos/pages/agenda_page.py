"""Agenda page — day view with scheduled tasks and due-today list."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.agenda_state import AgendaState
from lifeos.state.base_state import AppState
from lifeos.components.template import page_template
from lifeos.components.badges import status_badge, priority_badge


def date_nav_bar() -> rx.Component:
    """Date navigation bar with prev/today/next buttons."""
    return rx.hstack(
        rx.icon_button(
            rx.icon("chevron-left", size=18),
            variant="soft",
            color_scheme="gray",
            on_click=AgendaState.prev_day,
            size="3",
        ),
        rx.button(
            rx.icon("calendar", size=16),
            "Today",
            variant="soft",
            color_scheme="teal",
            on_click=AgendaState.go_to_today,
            size="3",
        ),
        rx.text(
            AgendaState.selected_date,
            font_size="20px",
            font_weight="700",
            color=COLORS["text"],
            font_family="'Cabinet Grotesk', sans-serif",
            padding="0 16px",
        ),
        rx.icon_button(
            rx.icon("chevron-right", size=18),
            variant="soft",
            color_scheme="gray",
            on_click=AgendaState.next_day,
            size="3",
        ),

        # Date input
        rx.input(
            type="date",
            value=AgendaState.selected_date,
            on_change=AgendaState.set_date,
            background_color=COLORS["surface"],
            border_color=COLORS["border"],
            color=COLORS["text"],
            size="2",
            margin_left="16px",
        ),

        align="center",
        spacing="2",
        width="100%",
        margin_bottom="24px",
    )


def scheduled_task_card(task: dict) -> rx.Component:
    """A scheduled task block."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    task["title"],
                    font_size="13px",
                    font_weight="600",
                    color=COLORS["text"],
                ),
                rx.hstack(
                    status_badge(task["status"]),
                    rx.cond(
                        task["scheduled_duration"] != None,
                        rx.text(
                            task["scheduled_duration"].to_string() + "m",
                            font_size="11px",
                            color=COLORS["muted"],
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    task["scheduled_at"],
                    font_size="11px",
                    color=COLORS["muted"],
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.icon_button(
                rx.icon("check", size=14),
                size="1",
                variant="ghost",
                color_scheme="green",
                on_click=AgendaState.mark_task_complete(task["id"]),
            ),
            align="center",
            width="100%",
        ),
        background_color="rgba(45, 212, 191, 0.12)",
        border=f"1px solid {COLORS['primary']}",
        border_left=f"3px solid {COLORS['primary']}",
        border_radius="6px",
        padding="10px 12px",
        margin_bottom="8px",
        width="100%",
    )


def schedule_section() -> rx.Component:
    """Scheduled tasks section."""
    return rx.box(
        rx.text(
            "SCHEDULED",
            font_size="11px",
            font_weight="700",
            color=COLORS["primary"],
            letter_spacing="0.08em",
            margin_bottom="12px",
        ),
        rx.cond(
            AgendaState.scheduled_tasks.length() == 0,
            rx.box(
                rx.vstack(
                    rx.icon("calendar-days", size=32, color=COLORS["muted"]),
                    rx.text(
                        "No tasks scheduled for this day",
                        font_size="14px",
                        color=COLORS["muted"],
                    ),
                    align="center",
                    spacing="2",
                    padding="40px",
                ),
            ),
            rx.vstack(
                rx.foreach(AgendaState.scheduled_tasks, scheduled_task_card),
                spacing="2",
                width="100%",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_left=f"3px solid {COLORS['primary']}",
        border_radius="10px",
        padding="20px",
        flex="1",
        min_height="300px",
    )


def due_today_item(task: dict) -> rx.Component:
    """Single due-today task entry."""
    return rx.box(
        rx.hstack(
            rx.icon("triangle-alert", size=14, color=COLORS["warning"]),
            rx.text(
                task["title"],
                font_size="13px",
                color=COLORS["text"],
                flex="1",
            ),
            priority_badge(task["priority"]),
            rx.icon_button(
                rx.icon("check", size=13),
                size="1",
                variant="ghost",
                color_scheme="green",
                on_click=AgendaState.mark_task_complete(task["id"]),
            ),
            align="center",
            spacing="2",
        ),
        padding="8px 12px",
        border_radius="6px",
        border=f"1px solid {COLORS['border']}",
        _hover={"background_color": COLORS["surface2"]},
        width="100%",
    )


def due_today_panel() -> rx.Component:
    """Panel showing tasks due today."""
    return rx.box(
        rx.text(
            "DUE TODAY",
            font_size="11px",
            font_weight="700",
            color=COLORS["warning"],
            letter_spacing="0.08em",
            margin_bottom="12px",
        ),
        rx.cond(
            AgendaState.due_today.length() == 0,
            rx.box(
                rx.vstack(
                    rx.icon("check-circle-2", size=28, color=COLORS["success"]),
                    rx.text(
                        "All caught up!",
                        font_size="14px",
                        color=COLORS["muted"],
                    ),
                    align="center",
                    spacing="2",
                    padding="24px",
                ),
            ),
            rx.vstack(
                rx.foreach(AgendaState.due_today, due_today_item),
                spacing="2",
                width="100%",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_left=f"3px solid {COLORS['warning']}",
        border_radius="10px",
        padding="20px",
        min_width="280px",
        width="320px",
    )


def google_calendar_widget() -> rx.Component:
    """Displays events pulled from the external calendar engine."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("calendar-clock", size=18, color=COLORS["primary"]),
                rx.text(
                    "EXTERNAL SCHEDULE",
                    font_size="12px",
                    font_weight="700",
                    color=COLORS["muted"],
                    letter_spacing="0.08em",
                ),
                rx.spacer(),
                rx.badge(AgendaState.calendar_status, variant="soft", color_scheme="blue", size="1"),
                align="center",
                width="100%",
                padding_bottom="12px",
                border_bottom=f"1px solid {COLORS['border']}",
            ),
            
            # Loop through the agnostic events list
            rx.cond(
                AgendaState.external_events.length() > 0,
                rx.foreach(
                    AgendaState.external_events,
                    lambda event: rx.hstack(
                        rx.box(width="4px", height="24px", background_color=COLORS["primary"], border_radius="2px"),
                        rx.vstack(
                            rx.text(event["title"], font_size="13px", color=COLORS["text"], font_weight="600"),
                            # We can format the raw ISO time string here or in the backend
                            rx.text(event["time"], font_size="11px", color=COLORS["muted"]),
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.badge(event["source"], variant="soft", color_scheme="gray"),
                        align="center",
                        width="100%",
                        padding_top="8px"
                    )
                ),
                rx.text("No external events scheduled today.", font_size="12px", color=COLORS["muted"], padding_top="12px")
            ),
            
            spacing="2",
            width="100%",
            align="start",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        width="100%",
        margin_top="16px",
    )


@rx.page(
    route="/agenda",
    title="Agenda — LifeOS",
    on_load=[AppState.load_settings, AgendaState.load_agenda, AgendaState.sync_external_calendar],
)
def agenda_page() -> rx.Component:
    """Agenda page component."""
    return page_template(
        rx.vstack(
            date_nav_bar(),

            rx.hstack(
                # Left: scheduled tasks
                schedule_section(),

                # Right: due today + calendar
                rx.vstack(
                    due_today_panel(),
                    google_calendar_widget(),
                    spacing="4",
                    align="start",
                    flex_shrink="0",
                ),

                spacing="6",
                width="100%",
                align="start",
            ),

            spacing="0",
            width="100%",
            align="start",
        ),
        title="Agenda",
    )
