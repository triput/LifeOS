"""Academy page — learning hierarchy and certifications."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.academy_state import AcademyState
from lifeos.state.base_state import AppState
from lifeos.components.template import page_template
from lifeos.components.academy_views import academy_tree
from lifeos.components.academy_drawer import academy_drawer
from lifeos.components.badges import status_badge
from lifeos.components.quick_add import universal_quick_add_widget


def cert_progress_bar(completed, required, color: str) -> rx.Component:
    """Horizontal progress bar. completed and required are Reflex vars."""
    return rx.box(
        rx.box(
            # Width expressed as a string percentage via rx.cond
            rx.cond(
                required > 0,
                rx.box(
                    width=(completed * 100 // required).to_string() + "%",
                    height="8px",
                    background_color=color,
                    border_radius="4px",
                    max_width="100%",
                ),
                rx.box(width="0%", height="8px"),
            ),
        ),
        width="100%",
        height="8px",
        background_color=COLORS["border"],
        border_radius="4px",
        overflow="hidden",
    )


def cert_card(cert: dict) -> rx.Component:
    """Certification card with PDU/SEU progress."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        cert["title"],
                        font_size="15px",
                        font_weight="700",
                        color=COLORS["text"],
                        font_family="'Cabinet Grotesk', sans-serif",
                    ),
                    rx.text(
                        cert["issuer"],
                        font_size="12px",
                        color=COLORS["muted"],
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                status_badge(cert["status"]),
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    size="2",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=AcademyState.open_drawer("certification", cert["id"]),
                ),
                align="center",
                width="100%",
            ),

            # PDU Progress
            rx.cond(
                cert["pdus_required"].to(int) > 0,
                rx.vstack(
                    rx.hstack(
                        rx.text("PDUs", font_size="12px", color=COLORS["muted"], font_weight="600"),
                        rx.spacer(),
                        rx.text(
                            cert["pdus_completed"].to_string() + " / " + cert["pdus_required"].to_string(),
                            font_size="12px",
                            color=COLORS["text"],
                            font_weight="600",
                        ),
                        width="100%",
                    ),
                    rx.box(
                        rx.box(
                            width=(cert["pdus_completed"].to(int) * 100 // cert["pdus_required"].to(int)).to_string() + "%",
                            height="8px",
                            background_color=COLORS["primary"],
                            border_radius="4px",
                            max_width="100%",
                        ),
                        width="100%",
                        height="8px",
                        background_color=COLORS["border"],
                        border_radius="4px",
                        overflow="hidden",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.fragment(),
            ),

            # SEU Progress
            rx.cond(
                cert["seus_required"].to(int) > 0,
                rx.vstack(
                    rx.hstack(
                        rx.text("SEUs", font_size="12px", color=COLORS["muted"], font_weight="600"),
                        rx.spacer(),
                        rx.text(
                            cert["seus_completed"].to_string() + " / " + cert["seus_required"].to_string(),
                            font_size="12px",
                            color=COLORS["text"],
                            font_weight="600",
                        ),
                        width="100%",
                    ),
                    rx.box(
                        rx.box(
                            width=(cert["seus_completed"].to(int) * 100 // cert["seus_required"].to(int)).to_string() + "%",
                            height="8px",
                            background_color=COLORS["success"],
                            border_radius="4px",
                            max_width="100%",
                        ),
                        width="100%",
                        height="8px",
                        background_color=COLORS["border"],
                        border_radius="4px",
                        overflow="hidden",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.fragment(),
            ),

            # Renewal date
            rx.cond(
                cert["next_renewal_date"] != None,
                rx.hstack(
                    rx.icon("calendar", size=12, color=COLORS["muted"]),
                    rx.text(
                        "Renewal: " + cert["next_renewal_date"].to_string(),
                        font_size="12px",
                        color=COLORS["muted"],
                    ),
                    align="center",
                    spacing="1",
                ),
                rx.fragment(),
            ),

            spacing="3",
            width="100%",
        ),
        background_color=COLORS["surface"],
        border=f"1px solid {COLORS['border']}",
        border_radius="10px",
        padding="16px",
        width="100%",
        margin_bottom="12px",
    )


def certifications_panel() -> rx.Component:
    """Right panel showing certifications."""
    return rx.box(
        rx.hstack(
            rx.text(
                "Certifications",
                font_size="16px",
                font_weight="700",
                color=COLORS["text"],
                font_family="'Cabinet Grotesk', sans-serif",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=14),
                "Add Cert",
                size="2",
                color_scheme="teal",
                variant="soft",
                on_click=AcademyState.open_new_drawer("certification", 0),
            ),
            align="center",
            width="100%",
            margin_bottom="16px",
        ),
        rx.cond(
            AcademyState.certifications.length() == 0,
            rx.box(
                rx.vstack(
                    rx.icon("award", size=36, color=COLORS["muted"]),
                    rx.text(
                        "No certifications yet",
                        font_size="14px",
                        color=COLORS["muted"],
                    ),
                    align="center",
                    spacing="2",
                    padding="32px",
                ),
            ),
            rx.foreach(
                AcademyState.certifications,
                cert_card,
            ),
        ),
        min_width="300px",
        width="320px",
        flex_shrink="0",
    )


@rx.page(
    route="/academy",
    title="Academy — LifeOS",
    on_load=[AppState.load_settings, AcademyState.load_academy],
)
def academy_page() -> rx.Component:
    """Academy page component."""
    return page_template(
        rx.vstack(
            universal_quick_add_widget(domain="academy"),  # The new universal quick-add widget at the top of the academy page
            
            rx.hstack(
                # Left: Academy tree
                rx.box(
                    rx.cond(
                        AcademyState.specializations.length() == 0,
                        rx.box(
                            rx.vstack(
                                rx.icon("graduation-cap", size=48, color=COLORS["muted"]),
                                rx.text(
                                    "No learning paths yet",
                                    font_size="18px",
                                    font_weight="600",
                                    color=COLORS["muted"],
                                ),
                                rx.text(
                                    "Create your first Specialization to get started",
                                    font_size="14px",
                                    color=COLORS["muted"],
                                ),
                                rx.button(
                                    rx.icon("plus", size=16),
                                    "Create Specialization",
                                    color_scheme="teal",
                                    size="3",
                                    on_click=AcademyState.open_new_drawer("specialization", 0),
                                ),
                                align="center",
                                spacing="4",
                                padding="60px",
                            ),
                        ),
                        academy_tree(),
                    ),
                    flex="1",
                    overflow_y="auto",
                ),

                # Right: Certifications panel
                certifications_panel(),

                spacing="6",
                width="100%",
                align="start",
            ),

            # Academy drawer
            academy_drawer(),

            spacing="0",
            width="100%",
            align="start",
        ),
        title="Academy",
    )
