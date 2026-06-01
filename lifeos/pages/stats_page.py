"""Stats page — analytics, time tracking, charts."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.stats_state import StatsState
from lifeos.state.base_state import AppState
from lifeos.components.template import page_template
from lifeos.components.badges import status_badge, priority_badge


def stat_card(label: str, value, unit: str = "", color: str = COLORS["text"], icon: str = "bar-chart-2") -> rx.Component:
    """A single stat metric card."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=18, color=color),
                rx.text(
                    label,
                    font_size="11px",
                    color=COLORS["muted"],
                    font_weight="600",
                    letter_spacing="0.05em",
                ),
                align="center",
                spacing="2",
            ),
            rx.hstack(
                rx.text(
                    value,
                    font_size="28px",
                    font_weight="800",
                    color=color,
                    font_family="'Cabinet Grotesk', sans-serif",
                ),
                rx.text(unit, font_size="14px", color=COLORS["muted"]) if unit else rx.fragment(),
                align="baseline",
                spacing="1",
            ),
            align="start",
            spacing="2",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="16px 20px",
        flex="1",
        min_width="140px",
    )


def date_range_picker() -> rx.Component:
    """Date range selection for stats."""
    return rx.hstack(
        rx.text("From:", font_size="13px", color=COLORS["muted"]),
        rx.input(
            type="date",
            value=StatsState.start_date,
            on_change=StatsState.set_start_date,
            background_color=COLORS["surface"],
            border_color=COLORS["border"],
            color=COLORS["text"],
            size="2",
        ),
        rx.text("To:", font_size="13px", color=COLORS["muted"]),
        rx.input(
            type="date",
            value=StatsState.end_date,
            on_change=StatsState.set_end_date,
            background_color=COLORS["surface"],
            border_color=COLORS["border"],
            color=COLORS["text"],
            size="2",
        ),
        rx.button(
            rx.icon("refresh-cw", size=14),
            "Refresh",
            color_scheme="teal",
            variant="soft",
            size="2",
            on_click=StatsState.load_stats,
        ),
        align="center",
        spacing="3",
        padding="12px 16px",
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="8px",
        flex_wrap="wrap",
        margin_bottom="24px",
    )


def kpi_row() -> rx.Component:
    """Main KPI metrics row."""
    return rx.hstack(
        stat_card(
            "TASKS COMPLETED",
            StatsState.completed_tasks,
            color=COLORS["success"],
            icon="check-circle-2",
        ),
        stat_card(
            "IN PROGRESS",
            StatsState.in_progress_tasks,
            color=COLORS["primary"],
            icon="activity",
        ),
        stat_card(
            "OVERDUE",
            StatsState.overdue_tasks,
            color=COLORS["accent"],
            icon="triangle-alert",
        ),
        stat_card(
            "COMPLETION RATE",
            StatsState.completion_rate,
            unit="%",
            color=COLORS["success"],
            icon="trending-up",
        ),
        stat_card(
            "TOTAL TASKS",
            StatsState.total_tasks,
            icon="list-checks",
        ),
        spacing="4",
        width="100%",
        flex_wrap="wrap",
        margin_bottom="24px",
    )


def time_kpi_row() -> rx.Component:
    """Time tracking KPI row."""
    return rx.hstack(
        stat_card(
            "EST. HOURS",
            StatsState.total_estimated_minutes,
            unit="m",
            color=COLORS["warning"],
            icon="clock",
        ),
        stat_card(
            "ACTUAL HOURS",
            StatsState.total_actual_minutes,
            unit="m",
            color=COLORS["primary"],
            icon="timer",
        ),
        stat_card(
            "LEARNING HOURS",
            StatsState.learning_hours,
            unit="h",
            color=COLORS["success"],
            icon="book-open",
        ),
        stat_card(
            "MODULES DONE",
            StatsState.modules_completed,
            color=COLORS["primary"],
            icon="layers",
        ),
        spacing="4",
        width="100%",
        flex_wrap="wrap",
        margin_bottom="24px",
    )


def bar_chart_row(item: dict, key_field: str, value_field: str, max_val: int, color: str) -> rx.Component:
    """Horizontal bar chart row."""
    return rx.hstack(
        rx.text(
            item[key_field],
            font_size="12px",
            color=COLORS["muted"],
            min_width="80px",
            text_align="right",
        ),
        rx.box(
            rx.box(
                width=item[value_field].to_string() + "px",
                height="16px",
                background_color=color,
                border_radius="3px",
                max_width="200px",
            ),
            height="16px",
            background_color=COLORS["border"],
            border_radius="3px",
            flex="1",
            overflow="hidden",
        ),
        rx.text(
            item[value_field].to_string(),
            font_size="12px",
            color=COLORS["text"],
            min_width="30px",
        ),
        align="center",
        spacing="3",
        width="100%",
    )


def status_distribution_card() -> rx.Component:
    """Status distribution display."""
    return rx.box(
        rx.text(
            "Tasks by Status",
            font_size="14px",
            font_weight="700",
            color=COLORS["text"],
            font_family="'Cabinet Grotesk', sans-serif",
            margin_bottom="16px",
        ),
        rx.cond(
            StatsState.status_distribution.length() == 0,
            rx.text("No data available", font_size="13px", color=COLORS["muted"]),
            rx.vstack(
                rx.foreach(
                    StatsState.status_distribution,
                    lambda item: rx.hstack(
                        rx.box(
                            width="12px",
                            height="12px",
                            border_radius="2px",
                            background_color=rx.match(
                                item["status"],
                                ("In Progress", COLORS["primary"]),
                                ("Completed", COLORS["success"]),
                                ("Blocked", COLORS["accent"]),
                                ("On Hold", COLORS["warning"]),
                                COLORS["muted"],
                            ),
                            flex_shrink="0",
                        ),
                        rx.text(item["status"], font_size="13px", color=COLORS["text"], flex="1"),
                        rx.text(
                            item["count"].to_string(),
                            font_size="13px",
                            color=COLORS["primary"],
                            font_weight="600",
                        ),
                        align="center",
                        spacing="3",
                        padding="6px 0",
                        width="100%",
                    ),
                ),
                spacing="1",
                width="100%",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        flex="1",
        min_width="260px",
    )


def priority_distribution_card() -> rx.Component:
    """Priority distribution display."""
    return rx.box(
        rx.text(
            "Tasks by Priority",
            font_size="14px",
            font_weight="700",
            color=COLORS["text"],
            font_family="'Cabinet Grotesk', sans-serif",
            margin_bottom="16px",
        ),
        rx.cond(
            StatsState.priority_distribution.length() == 0,
            rx.text("No data available", font_size="13px", color=COLORS["muted"]),
            rx.vstack(
                rx.foreach(
                    StatsState.priority_distribution,
                    lambda item: rx.hstack(
                        rx.box(
                            width="12px",
                            height="12px",
                            border_radius="2px",
                            background_color=rx.match(
                                item["priority"],
                                ("Low", COLORS["muted"]),
                                ("Normal", COLORS["primary"]),
                                ("High", COLORS["warning"]),
                                ("Critical", COLORS["accent"]),
                                COLORS["muted"],
                            ),
                            flex_shrink="0",
                        ),
                        rx.text(item["priority"], font_size="13px", color=COLORS["text"], flex="1"),
                        rx.text(
                            item["count"].to_string(),
                            font_size="13px",
                            color=COLORS["warning"],
                            font_weight="600",
                        ),
                        align="center",
                        spacing="3",
                        padding="6px 0",
                        width="100%",
                    ),
                ),
                spacing="1",
                width="100%",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        flex="1",
        min_width="260px",
    )


def domain_time_card() -> rx.Component:
    """Domain time distribution."""
    return rx.box(
        rx.text(
            "Time by Domain",
            font_size="14px",
            font_weight="700",
            color=COLORS["text"],
            font_family="'Cabinet Grotesk', sans-serif",
            margin_bottom="16px",
        ),
        rx.cond(
            StatsState.domain_time.length() == 0,
            rx.text("No time tracked yet", font_size="13px", color=COLORS["muted"]),
            rx.vstack(
                rx.foreach(
                    StatsState.domain_time,
                    lambda item: rx.hstack(
                        rx.text(item["domain"], font_size="13px", color=COLORS["text"], flex="1"),
                        rx.text(
                            item["hours"].to_string() + "h",
                            font_size="13px",
                            color=COLORS["success"],
                            font_weight="600",
                        ),
                        align="center",
                        spacing="3",
                        padding="6px 0",
                        border_bottom=f"1px solid {COLORS['border']}",
                        width="100%",
                    ),
                ),
                spacing="0",
                width="100%",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        flex="1",
        min_width="260px",
    )


def epic_time_card() -> rx.Component:
    """Estimated vs actual time by Epic."""
    return rx.box(
        rx.text(
            "Estimated vs Actual by Epic",
            font_size="14px",
            font_weight="700",
            color=COLORS["text"],
            font_family="'Cabinet Grotesk', sans-serif",
            margin_bottom="16px",
        ),
        rx.cond(
            StatsState.epic_time.length() == 0,
            rx.text("No epics found", font_size="13px", color=COLORS["muted"]),
            rx.vstack(
                rx.foreach(
                    StatsState.epic_time,
                    lambda item: rx.box(
                        rx.text(
                            item["epic"],
                            font_size="13px",
                            color=COLORS["text"],
                            font_weight="500",
                            margin_bottom="6px",
                        ),
                        rx.hstack(
                            rx.vstack(
                                rx.text("Est.", font_size="11px", color=COLORS["muted"]),
                                rx.text(
                                    item["estimated_h"].to_string() + "h",
                                    font_size="13px",
                                    color=COLORS["border"],
                                    font_weight="600",
                                ),
                                spacing="0",
                                align="center",
                            ),
                            rx.vstack(
                                rx.text("Act.", font_size="11px", color=COLORS["muted"]),
                                rx.text(
                                    item["actual_h"].to_string() + "h",
                                    font_size="13px",
                                    color=COLORS["primary"],
                                    font_weight="600",
                                ),
                                spacing="0",
                                align="center",
                            ),
                            spacing="6",
                        ),
                        padding="10px 0",
                        border_bottom=f"1px solid {COLORS['border']}",
                        width="100%",
                    ),
                ),
                spacing="0",
                width="100%",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        width="100%",
    )


def overdue_item_row(item: dict) -> rx.Component:
    """Single overdue item row."""
    return rx.hstack(
        rx.icon("triangle-alert", size=14, color=COLORS["accent"]),
        rx.text(item["title"], font_size="13px", color=COLORS["text"], flex="1"),
        rx.text(
            item["due_date"],
            font_size="11px",
            color=COLORS["accent"],
            font_weight="600",
        ),
        status_badge(item["status"]),
        priority_badge(item["priority"]),
        align="center",
        spacing="2",
        padding="8px 12px",
        border_radius="6px",
        border=f"1px solid {COLORS['border']}",
        width="100%",
        _hover={"background_color": COLORS["surface2"]},
    )


def overdue_table() -> rx.Component:
    """Table of overdue items."""
    return rx.box(
        rx.text(
            "Overdue Items",
            font_size="14px",
            font_weight="700",
            color=COLORS["accent"],
            font_family="'Cabinet Grotesk', sans-serif",
            margin_bottom="12px",
        ),
        rx.cond(
            StatsState.overdue_items.length() == 0,
            rx.box(
                rx.vstack(
                    rx.icon("check-circle-2", size=28, color=COLORS["success"]),
                    rx.text("No overdue items!", font_size="14px", color=COLORS["muted"]),
                    align="center",
                    spacing="2",
                    padding="24px",
                ),
            ),
            rx.vstack(
                rx.foreach(StatsState.overdue_items, overdue_item_row),
                spacing="2",
                width="100%",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_left=f"3px solid {COLORS['accent']}",
        border_radius="10px",
        padding="20px",
        flex="1",
        min_width="300px",
    )


def cert_card(cert: dict) -> rx.Component:
    """Single certification progress card."""
    return rx.box(
        rx.hstack(
            rx.text(cert["title"], font_size="14px", font_weight="600", color=COLORS["text"]),
            rx.text(cert["issuer"], font_size="12px", color=COLORS["muted"]),
            rx.spacer(),
            rx.badge(
                cert["status"],
                color_scheme=rx.match(
                    cert["status"],
                    ("Active", "teal"),
                    ("Expired", "red"),
                    ("In Progress", "blue"),
                    "gray",
                ),
                variant="soft",
                size="1",
            ),
            align="center",
            spacing="2",
            margin_bottom="10px",
        ),
        # PDU bar
        rx.cond(
            cert["pdus_required"].to(int) > 0,
            rx.vstack(
                rx.hstack(
                    rx.text("PDUs", font_size="11px", color=COLORS["muted"]),
                    rx.spacer(),
                    rx.text(
                        cert["pdus_completed"].to_string() + "/" + cert["pdus_required"].to_string(),
                        font_size="11px",
                        color=COLORS["text"],
                        font_weight="600",
                    ),
                    width="100%",
                ),
                rx.box(
                    rx.box(
                        width=cert["pdu_pct"].to(int).to_string() + "%",
                        height="6px",
                        background_color=COLORS["primary"],
                        border_radius="3px",
                        max_width="100%",
                    ),
                    width="100%",
                    height="6px",
                    background_color=COLORS["border"],
                    border_radius="3px",
                    overflow="hidden",
                ),
                spacing="1",
                width="100%",
                margin_bottom="6px",
            ),
            rx.fragment(),
        ),
        # SEU bar
        rx.cond(
            cert["seus_required"].to(int) > 0,
            rx.vstack(
                rx.hstack(
                    rx.text("SEUs", font_size="11px", color=COLORS["muted"]),
                    rx.spacer(),
                    rx.text(
                        cert["seus_completed"].to_string() + "/" + cert["seus_required"].to_string(),
                        font_size="11px",
                        color=COLORS["text"],
                        font_weight="600",
                    ),
                    width="100%",
                ),
                rx.box(
                    rx.box(
                        width=cert["seu_pct"].to(int).to_string() + "%",
                        height="6px",
                        background_color=COLORS["success"],
                        border_radius="3px",
                        max_width="100%",
                    ),
                    width="100%",
                    height="6px",
                    background_color=COLORS["border"],
                    border_radius="3px",
                    overflow="hidden",
                ),
                spacing="1",
                width="100%",
            ),
            rx.fragment(),
        ),
        padding="16px",
        background_color=COLORS["surface2"],
        border=f"1px solid {COLORS['border']}",
        border_radius="8px",
        width="100%",
        margin_bottom="10px",
    )


def cert_progress_section() -> rx.Component:
    """Certification progress section."""
    return rx.box(
        rx.text(
            "Certification Progress",
            font_size="14px",
            font_weight="700",
            color=COLORS["text"],
            font_family="'Cabinet Grotesk', sans-serif",
            margin_bottom="12px",
        ),
        rx.cond(
            StatsState.cert_progress.length() == 0,
            rx.text("No certifications tracked", font_size="13px", color=COLORS["muted"]),
            rx.vstack(
                rx.foreach(StatsState.cert_progress, cert_card),
                spacing="0",
                width="100%",
            ),
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="20px",
        flex="1",
        min_width="280px",
    )


@rx.page(
    route="/stats",
    title="Stats — LifeOS",
    on_load=[AppState.load_settings, StatsState.load_stats],
)
def stats_page() -> rx.Component:
    """Stats/Analytics page component."""
    return page_template(
        rx.vstack(
            # Date range picker
            date_range_picker(),

            # KPI rows
            kpi_row(),
            time_kpi_row(),

            # Distribution charts row
            rx.hstack(
                status_distribution_card(),
                priority_distribution_card(),
                domain_time_card(),
                spacing="4",
                width="100%",
                flex_wrap="wrap",
                margin_bottom="24px",
            ),

            # Epic time comparison
            epic_time_card(),

            rx.box(height="24px"),

            # Overdue + certifications
            rx.hstack(
                overdue_table(),
                cert_progress_section(),
                spacing="4",
                width="100%",
                flex_wrap="wrap",
            ),

            spacing="4",
            width="100%",
            align="start",
        ),
        title="Stats",
    )
