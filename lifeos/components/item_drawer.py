"""Slide-out edit drawer component for Work items."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.work import WorkState
from lifeos.utils import fmt_mins


def field_label(text: str) -> rx.Component:
    return rx.text(
        text,
        font_size="12px",
        font_weight="600",
        color=COLORS["muted"],
        letter_spacing="0.05em",
        margin_bottom="4px",
    )


def drawer_field(label: str, *inputs) -> rx.Component:
    return rx.vstack(
        field_label(label),
        *inputs,
        spacing="1",
        width="100%",
        align="start",
    )


def item_drawer() -> rx.Component:
    """Full slide-out drawer for editing work items."""
    is_task = WorkState.selected_type == "task"
    is_subtask = WorkState.selected_type == "subtask"

    item = WorkState.selected_item

    return rx.drawer.root(
        rx.drawer.overlay(background_color="rgba(0,0,0,0.6)"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.text(
                            rx.match(
                                WorkState.selected_type,
                                ("epic", "Edit Epic"),
                                ("project", "Edit Project"),
                                ("task", "Edit Task"),
                                ("subtask", "Edit Subtask"),
                                "Edit Item",
                            ),
                            font_size="18px",
                            font_weight="700",
                            color=COLORS["text"],
                            font_family="'Cabinet Grotesk', sans-serif",
                        ),
                        rx.drawer.close(
                            rx.icon_button(
                                rx.icon("x", size=16),
                                variant="ghost",
                                color_scheme="gray",
                                on_click=WorkState.close_drawer,
                            ),
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        padding_bottom="16px",
                        border_bottom=f"1px solid {COLORS['border']}",
                    ),

                    # Form fields
                    rx.form(
                        rx.vstack(
                            # Title
                            drawer_field(
                                "TITLE",
                                rx.input(
                                    name="title",
                                    default_value=item.get("title", ""),
                                    placeholder="Enter title...",
                                    width="100%",
                                    background_color=COLORS["surface"],
                                    border_color=COLORS["border"],
                                    color=COLORS["text"],
                                    _focus={"border_color": COLORS["primary"]},
                                ),
                            ),

                            # Description
                            rx.cond(
                                ~is_subtask,
                                drawer_field(
                                    "DESCRIPTION",
                                    rx.text_area(
                                        name="description",
                                        default_value=item.get("description", ""),
                                        placeholder="Description...",
                                        width="100%",
                                        rows="3",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),
                            ),

                            # Status + Priority row
                            rx.cond(
                                ~is_subtask,
                                rx.hstack(
                                    drawer_field(
                                        "STATUS",
                                        rx.select.root(
                                            rx.select.trigger(width="100%"),
                                            rx.select.content(
                                                rx.select.item("In Progress", value="In Progress"),
                                                rx.select.item("Planned", value="Planned"),
                                                rx.select.item("Completed", value="Completed"),
                                                rx.select.item("On Hold", value="On Hold"),
                                                rx.select.item("Blocked", value="Blocked"),
                                                rx.select.item("Cancelled", value="Cancelled"),
                                                background_color=COLORS["surface"],
                                            ),
                                            name="status",
                                            default_value=item.get("status", "In Progress"),
                                        ),
                                    ),
                                    drawer_field(
                                        "PRIORITY",
                                        rx.select.root(
                                            rx.select.trigger(width="100%"),
                                            rx.select.content(
                                                rx.select.item("1 — Low", value="1"),
                                                rx.select.item("2 — Normal", value="2"),
                                                rx.select.item("3 — High", value="3"),
                                                rx.select.item("4 — Critical", value="4"),
                                                background_color=COLORS["surface"],
                                            ),
                                            name="priority",
                                            default_value=str(item.get("priority", "2")),
                                        ),
                                    ),
                                    spacing="4",
                                    width="100%",
                                ),
                            ),

                            # Subtask is_completed
                            rx.cond(
                                is_subtask,
                                rx.hstack(
                                    rx.checkbox(
                                        name="is_completed",
                                        default_checked=item.get("is_completed", False),
                                    ),
                                    rx.text("Completed", color=COLORS["text"], font_size="14px"),
                                    align="center",
                                    spacing="2",
                                ),
                            ),

                            # Domain (not for subtask)
                            rx.cond(
                                ~is_subtask,
                                drawer_field(
                                    "DOMAIN",
                                    rx.input(
                                        name="domain",
                                        default_value=item.get("domain", ""),
                                        placeholder="e.g. Engineering, Product...",
                                        width="100%",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),
                            ),

                            # Due date (projects/tasks only)
                            rx.cond(
                                (WorkState.selected_type == "project") | is_task,
                                drawer_field(
                                    "DUE DATE",
                                    rx.input(
                                        name="due_date",
                                        type="date",
                                        default_value=item.get("due_date", ""),
                                        width="100%",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),
                            ),

                            # Scheduled At + Duration (tasks only)
                            rx.cond(
                                is_task,
                                rx.hstack(
                                    drawer_field(
                                        "SCHEDULED AT",
                                        rx.input(
                                            name="scheduled_at",
                                            type="datetime-local",
                                            default_value=item.get("scheduled_at", ""),
                                            width="100%",
                                            background_color=COLORS["surface"],
                                            border_color=COLORS["border"],
                                            color=COLORS["text"],
                                        ),
                                    ),
                                    drawer_field(
                                        "DURATION (mins)",
                                        rx.input(
                                            name="scheduled_duration",
                                            type="number",
                                            default_value=str(item.get("scheduled_duration", "")),
                                            placeholder="e.g. 60",
                                            width="100%",
                                            background_color=COLORS["surface"],
                                            border_color=COLORS["border"],
                                            color=COLORS["text"],
                                        ),
                                    ),
                                    spacing="4",
                                    width="100%",
                                ),
                            ),

                            # Time tracking row
                            rx.hstack(
                                drawer_field(
                                    "ESTIMATED",
                                    rx.input(
                                        name="estimated_minutes",
                                        default_value=str(item.get("estimated_minutes", 0)),
                                        placeholder="e.g. 1h 30m",
                                        width="100%",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),
                                drawer_field(
                                    "ACTUAL",
                                    rx.input(
                                        name="actual_minutes",
                                        default_value=str(item.get("actual_minutes", 0)),
                                        placeholder="e.g. 45m",
                                        width="100%",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),
                                spacing="4",
                                width="100%",
                            ),

                            # Notion URL (not subtask)
                            rx.cond(
                                ~is_subtask,
                                drawer_field(
                                    "NOTION URL",
                                    rx.hstack(
                                        rx.input(
                                            name="notion_url",
                                            default_value=item.get("notion_url", ""),
                                            placeholder="https://notion.so/...",
                                            width="100%",
                                            background_color=COLORS["surface"],
                                            border_color=COLORS["border"],
                                            color=COLORS["text"],
                                        ),
                                        rx.cond(
                                            item.get("notion_url", "") != "",
                                            rx.link(
                                                rx.icon("external-link", size=16),
                                                href=item.get("notion_url", "#"),
                                                is_external=True,
                                                color=COLORS["primary"],
                                            ),
                                        ),
                                        width="100%",
                                        align="center",
                                        spacing="2",
                                    ),
                                ),
                            ),

                            # Notes (not subtask)
                            rx.cond(
                                ~is_subtask,
                                drawer_field(
                                    "NOTES",
                                    rx.text_area(
                                        name="notes",
                                        default_value=item.get("notes", ""),
                                        placeholder="Notes...",
                                        width="100%",
                                        rows="4",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),
                            ),

                            # Skedpal push button (tasks only)
                            rx.cond(
                                is_task,
                                rx.button(
                                    rx.icon("send", size=14),
                                    "Push to Skedpal",
                                    variant="soft",
                                    color_scheme="teal",
                                    size="2",
                                    width="100%",
                                    type="button",
                                ),
                            ),

                            spacing="4",
                            width="100%",
                        ),

                        # Action buttons
                        rx.hstack(
                            # Delete button
                            rx.button(
                                rx.icon("trash-2", size=14),
                                "Delete",
                                color_scheme="red",
                                variant="soft",
                                size="2",
                                type="button",
                                on_click=WorkState.delete_item,
                                flex="0",
                            ),
                            rx.spacer(),
                            rx.button(
                                "Cancel",
                                variant="ghost",
                                color_scheme="gray",
                                size="2",
                                type="button",
                                on_click=WorkState.close_drawer,
                            ),
                            rx.button(
                                rx.icon("save", size=14),
                                "Save",
                                color_scheme="teal",
                                size="2",
                                type="submit",
                            ),
                            width="100%",
                            align="center",
                            padding_top="16px",
                            border_top=f"1px solid {COLORS['border']}",
                            margin_top="8px",
                        ),

                        on_submit=WorkState.save_item,
                        width="100%",
                    ),

                    spacing="4",
                    width="100%",
                    padding="24px",
                    height="100%",
                    overflow_y="auto",
                ),

                side="right",
                background_color=COLORS["surface"],
                border_left=f"1px solid {COLORS['border']}",
                width="480px",
                height="100vh",
                overflow_y="auto",
            ),
        ),
        open=WorkState.drawer_open,
        on_open_change=WorkState.close_drawer,
    )
