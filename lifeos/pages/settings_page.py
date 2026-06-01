"""Settings page — label customization and integrations."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.base_state import AppState
from lifeos.components.template import page_template


def section_header(title: str, subtitle: str = "") -> rx.Component:
    """Settings section header."""
    return rx.vstack(
        rx.text(
            title,
            font_size="16px",
            font_weight="700",
            color=COLORS["text"],
            font_family="'Cabinet Grotesk', sans-serif",
        ),
        rx.text(subtitle, font_size="13px", color=COLORS["muted"]) if subtitle else rx.fragment(),
        align="start",
        spacing="1",
        margin_bottom="16px",
    )


def label_field(label: str, name: str, settings_key: str, placeholder: str = "") -> rx.Component:
    """A single label customization field."""
    return rx.vstack(
        rx.text(label, font_size="12px", color=COLORS["muted"], font_weight="600"),
        rx.input(
            name=name,
            default_value=AppState.settings.get(settings_key, ""),
            placeholder=placeholder or label,
            background_color=COLORS["surface2"],
            border_color=COLORS["border"],
            color=COLORS["text"],
            width="100%",
            _focus={"border_color": COLORS["primary"]},
        ),
        spacing="1",
        width="100%",
        align="start",
    )


def labels_section() -> rx.Component:
    """Label customization section."""
    return rx.box(
        section_header(
            "Label Customization",
            "Rename the hierarchies to match your personal workflow.",
        ),
        rx.vstack(
            rx.hstack(
                label_field("Epic Label", "label_epic", "label_epic", "e.g. Initiative, Goal"),
                label_field("Project Label", "label_project", "label_project", "e.g. Project, Sprint"),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                label_field("Task Label", "label_task", "label_task", "e.g. Task, Story"),
                label_field("Subtask Label", "label_subtask", "label_subtask", "e.g. Subtask, Step"),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                label_field("Specialization Label", "label_specialization", "label_specialization", "e.g. Path, Track"),
                label_field("Course Label", "label_course", "label_course", "e.g. Course, Program"),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                label_field("Module Label", "label_module", "label_module", "e.g. Module, Week"),
                rx.box(flex="1"),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="24px",
        width="100%",
        margin_bottom="24px",
    )


def integration_field(label: str, name: str, settings_key: str, placeholder: str = "", help_text: str = "") -> rx.Component:
    """Integration token/URL field."""
    return rx.vstack(
        rx.text(label, font_size="13px", color=COLORS["text"], font_weight="600"),
        rx.input(
            name=name,
            default_value=AppState.settings.get(settings_key, ""),
            placeholder=placeholder,
            background_color=COLORS["surface2"],
            border_color=COLORS["border"],
            color=COLORS["text"],
            width="100%",
            _focus={"border_color": COLORS["primary"]},
        ),
        rx.text(help_text, font_size="11px", color=COLORS["muted"]) if help_text else rx.fragment(),
        spacing="2",
        width="100%",
        align="start",
    )


def skedpal_section() -> rx.Component:
    """Skedpal integration section."""
    return rx.box(
        section_header(
            "Skedpal Integration",
            "Push tasks to Skedpal for AI-powered scheduling.",
        ),
        rx.vstack(
            integration_field(
                "Webhook URL",
                "skedpal_webhook_url",
                "skedpal_webhook_url",
                "https://app.skedpal.com/api/webhook/...",
                "Get your webhook URL from Skedpal → Settings → Integrations → Zapier/Webhook.",
            ),
            rx.box(
                rx.vstack(
                    rx.text(
                        "Setup Guide",
                        font_size="12px",
                        font_weight="600",
                        color=COLORS["primary"],
                    ),
                    rx.ordered_list(
                        rx.list_item(rx.text("Log in to Skedpal at app.skedpal.com", font_size="12px", color=COLORS["muted"])),
                        rx.list_item(rx.text("Go to Settings → Integrations", font_size="12px", color=COLORS["muted"])),
                        rx.list_item(rx.text("Enable Webhook integration and copy the URL", font_size="12px", color=COLORS["muted"])),
                        rx.list_item(rx.text("Paste it in the field above and save", font_size="12px", color=COLORS["muted"])),
                    ),
                    spacing="2",
                    align="start",
                ),
                background_color=COLORS["surface2"],
                border=f"1px solid {COLORS['border']}",
                border_radius="6px",
                padding="12px 16px",
            ),
            spacing="4",
            width="100%",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="24px",
        width="100%",
        margin_bottom="24px",
    )


def notion_section() -> rx.Component:
    """Notion integration section."""
    return rx.box(
        section_header(
            "Notion Integration",
            "Link items to Notion pages and sync notes.",
        ),
        rx.vstack(
            integration_field(
                "Notion Access Token",
                "notion_access_token",
                "notion_access_token",
                "secret_...",
                "Create an integration at notion.so/my-integrations and copy the Internal Integration Token.",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Setup Guide", font_size="12px", font_weight="600", color=COLORS["primary"]),
                    rx.ordered_list(
                        rx.list_item(rx.text("Go to notion.so/my-integrations", font_size="12px", color=COLORS["muted"])),
                        rx.list_item(rx.text("Click 'New integration' and name it LifeOS", font_size="12px", color=COLORS["muted"])),
                        rx.list_item(rx.text("Copy the Internal Integration Token (starts with secret_)", font_size="12px", color=COLORS["muted"])),
                        rx.list_item(rx.text("Paste it in the field above and save", font_size="12px", color=COLORS["muted"])),
                        rx.list_item(rx.text("Share your Notion pages with the integration", font_size="12px", color=COLORS["muted"])),
                    ),
                    spacing="2",
                    align="start",
                ),
                background_color=COLORS["surface2"],
                border=f"1px solid {COLORS['border']}",
                border_radius="6px",
                padding="12px 16px",
            ),
            spacing="4",
            width="100%",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="24px",
        width="100%",
        margin_bottom="24px",
    )


def google_calendar_section() -> rx.Component:
    """Settings for Google Calendar integration."""
    return rx.box(
        rx.vstack(
            section_header("Google Calendar", "Sync your external schedule to the Agenda view."),
            rx.vstack(
                label_field("Calendar ID (e.g., your@gmail.com)", "google_calendar_id", "google_calendar_id", "Primary Calendar ID"),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="24px",
        width="100%",
        margin_bottom="24px",
    )
    
def habitat_section() -> rx.Component:
    """Settings for the environment and weather tracking."""
    return rx.box(
        rx.vstack(
            section_header("Habitat & Environment", "Configure your Observatory tracking coordinates."),
            rx.vstack(
                label_field("Observatory Title", "habitat_name", "habitat_name", "e.g., Monroe Observatory"),
                label_field("Weather API Location", "habitat_location", "habitat_location", "e.g., Monroe, WA"),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="24px",
        width="100%",
        margin_bottom="24px",
    )

def settings_form() -> rx.Component:
    """Complete settings form."""
    return rx.form(
        rx.vstack(
            habitat_section(),
            labels_section(),
            skedpal_section(),
            notion_section(),
            google_calendar_section(),

            # Save button
            rx.hstack(
                rx.button(
                    rx.icon("save", size=16),
                    "Save All Settings",
                    color_scheme="teal",
                    size="3",
                    type="submit",
                ),
                width="100%",
                justify="end",
            ),

            spacing="0",
            width="100%",
        ),
        on_submit=AppState.save_settings,
        width="100%",
    )


@rx.page(
    route="/settings",
    title="Settings — LifeOS",
    on_load=AppState.load_settings,
)
def settings_page() -> rx.Component:
    """Settings page component."""
    return page_template(
        settings_form(),
        title="Settings",
    )
