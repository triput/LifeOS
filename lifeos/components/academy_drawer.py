"""Slide-out edit drawer for Academy items."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.academy_state import AcademyState


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


def academy_drawer() -> rx.Component:
    """Full slide-out drawer for editing academy items."""
    item = AcademyState.selected_item
    itype = AcademyState.selected_type

    is_cert = itype == "certification"
    is_lt = itype == "learning_task"
    is_spec_or_course = (itype == "specialization") | (itype == "course")
    is_module = itype == "module"

    return rx.drawer.root(
        rx.drawer.overlay(background_color="rgba(0,0,0,0.6)"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.text(
                            rx.match(
                                itype,
                                ("specialization", "Edit Specialization"),
                                ("course", "Edit Course"),
                                ("module", "Edit Module"),
                                ("learning_task", "Edit Learning Task"),
                                ("certification", "Edit Certification"),
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
                                on_click=AcademyState.close_drawer,
                            ),
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        padding_bottom="16px",
                        border_bottom=f"1px solid {COLORS['border']}",
                    ),

                    # Form
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
                                ),
                            ),

                            # Provider (spec/course)
                            rx.cond(
                                is_spec_or_course,
                                drawer_field(
                                    "PROVIDER",
                                    rx.input(
                                        name="provider",
                                        default_value=item.get("provider", ""),
                                        placeholder="e.g. Coursera, DeepLearning.AI...",
                                        width="100%",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),
                            ),

                            # Status
                            rx.cond(
                                ~is_lt,
                                drawer_field(
                                    "STATUS",
                                    rx.select.root(
                                        rx.select.trigger(width="100%"),
                                        rx.select.content(
                                            rx.select.item("In Progress", value="In Progress"),
                                            rx.select.item("Planned", value="Planned"),
                                            rx.select.item("Completed", value="Completed"),
                                            rx.select.item("Active", value="Active"),
                                            rx.select.item("Expired", value="Expired"),
                                            background_color=COLORS["surface"],
                                        ),
                                        name="status",
                                        default_value=item.get("status", "Planned"),
                                        width="100%",
                                    ),
                                ),
                            ),

                            # Learning task specific
                            rx.cond(
                                is_lt,
                                rx.vstack(
                                    rx.hstack(
                                        rx.checkbox(
                                            name="is_completed",
                                            default_checked=item.get("is_completed", False),
                                        ),
                                        rx.text("Completed", color=COLORS["text"], font_size="14px"),
                                        align="center",
                                        spacing="2",
                                    ),
                                    drawer_field(
                                        "ACTIVITY TYPE",
                                        rx.select.root(
                                            rx.select.trigger(width="100%"),
                                            rx.select.content(
                                                rx.select.item("Video", value="Video"),
                                                rx.select.item("Quiz", value="Quiz"),
                                                rx.select.item("Reading", value="Reading"),
                                                rx.select.item("Exercise", value="Exercise"),
                                                rx.select.item("Project", value="Project"),
                                                background_color=COLORS["surface"],
                                            ),
                                            name="activity_type",
                                            default_value=item.get("activity_type", "Video"),
                                            width="100%",
                                        ),
                                    ),
                                    rx.hstack(
                                        drawer_field(
                                            "EST. MINUTES",
                                            rx.input(
                                                name="estimated_minutes",
                                                default_value=str(item.get("estimated_minutes", 15)),
                                                type="number",
                                                width="100%",
                                                background_color=COLORS["surface"],
                                                border_color=COLORS["border"],
                                                color=COLORS["text"],
                                            ),
                                        ),
                                        drawer_field(
                                            "ACTUAL MINUTES",
                                            rx.input(
                                                name="actual_minutes",
                                                default_value=str(item.get("actual_minutes", 0)),
                                                type="number",
                                                width="100%",
                                                background_color=COLORS["surface"],
                                                border_color=COLORS["border"],
                                                color=COLORS["text"],
                                            ),
                                        ),
                                        spacing="4",
                                        width="100%",
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                            ),

                            # Certification-specific fields
                            rx.cond(
                                is_cert,
                                rx.vstack(
                                    drawer_field(
                                        "ISSUER",
                                        rx.input(
                                            name="issuer",
                                            default_value=item.get("issuer", ""),
                                            placeholder="e.g. PMI, Scrum Alliance...",
                                            width="100%",
                                            background_color=COLORS["surface"],
                                            border_color=COLORS["border"],
                                            color=COLORS["text"],
                                        ),
                                    ),
                                    rx.hstack(
                                        drawer_field(
                                            "ISSUE DATE",
                                            rx.input(
                                                name="issue_date",
                                                type="date",
                                                default_value=item.get("issue_date", ""),
                                                width="100%",
                                                background_color=COLORS["surface"],
                                                border_color=COLORS["border"],
                                                color=COLORS["text"],
                                            ),
                                        ),
                                        drawer_field(
                                            "RENEWAL DATE",
                                            rx.input(
                                                name="next_renewal_date",
                                                type="date",
                                                default_value=item.get("next_renewal_date", ""),
                                                width="100%",
                                                background_color=COLORS["surface"],
                                                border_color=COLORS["border"],
                                                color=COLORS["text"],
                                            ),
                                        ),
                                        spacing="4",
                                        width="100%",
                                    ),
                                    rx.hstack(
                                        drawer_field(
                                            "PDUs REQUIRED",
                                            rx.input(
                                                name="pdus_required",
                                                type="number",
                                                default_value=str(item.get("pdus_required", 0)),
                                                width="100%",
                                                background_color=COLORS["surface"],
                                                border_color=COLORS["border"],
                                                color=COLORS["text"],
                                            ),
                                        ),
                                        drawer_field(
                                            "PDUs COMPLETED",
                                            rx.input(
                                                name="pdus_completed",
                                                type="number",
                                                default_value=str(item.get("pdus_completed", 0)),
                                                width="100%",
                                                background_color=COLORS["surface"],
                                                border_color=COLORS["border"],
                                                color=COLORS["text"],
                                            ),
                                        ),
                                        spacing="4",
                                        width="100%",
                                    ),
                                    rx.hstack(
                                        drawer_field(
                                            "SEUs REQUIRED",
                                            rx.input(
                                                name="seus_required",
                                                type="number",
                                                default_value=str(item.get("seus_required", 0)),
                                                width="100%",
                                                background_color=COLORS["surface"],
                                                border_color=COLORS["border"],
                                                color=COLORS["text"],
                                            ),
                                        ),
                                        drawer_field(
                                            "SEUs COMPLETED",
                                            rx.input(
                                                name="seus_completed",
                                                type="number",
                                                default_value=str(item.get("seus_completed", 0)),
                                                width="100%",
                                                background_color=COLORS["surface"],
                                                border_color=COLORS["border"],
                                                color=COLORS["text"],
                                            ),
                                        ),
                                        spacing="4",
                                        width="100%",
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                            ),

                            # Notion URL
                            drawer_field(
                                "NOTION URL",
                                rx.input(
                                    name="notion_url",
                                    default_value=item.get("notion_url", ""),
                                    placeholder="https://notion.so/...",
                                    width="100%",
                                    background_color=COLORS["surface"],
                                    border_color=COLORS["border"],
                                    color=COLORS["text"],
                                ),
                            ),

                            # Notes
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

                            spacing="4",
                            width="100%",
                        ),

                        # Action buttons
                        rx.hstack(
                            rx.button(
                                rx.icon("trash-2", size=14),
                                "Delete",
                                color_scheme="red",
                                variant="soft",
                                size="2",
                                type="button",
                                on_click=AcademyState.delete_item,
                            ),
                            rx.spacer(),
                            rx.button(
                                "Cancel",
                                variant="ghost",
                                color_scheme="gray",
                                size="2",
                                type="button",
                                on_click=AcademyState.close_drawer,
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

                        on_submit=AcademyState.save_item,
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
        open=AcademyState.drawer_open,
        on_open_change=AcademyState.close_drawer,
    )
