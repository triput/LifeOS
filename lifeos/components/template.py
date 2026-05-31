"""Base page template that wraps content with sidebar."""

import reflex as rx
from lifeos.styles import COLORS, SIDEBAR_WIDTH
from lifeos.components.sidebar import sidebar


def page_template(*content: rx.Component, title: str = "") -> rx.Component:
    """Wrap page content with the sidebar and main layout."""
    return rx.box(
        sidebar(),
        rx.box(
            # Top header bar
            rx.hstack(
                rx.text(
                    title,
                    font_size="22px",
                    font_weight="700",
                    color=COLORS["text"],
                    font_family="'Cabinet Grotesk', sans-serif",
                ),
                justify="between",
                align="center",
                width="100%",
                padding="16px 24px",
                border_bottom=f"1px solid {COLORS['border']}",
                background_color=COLORS["surface"],
                position="sticky",
                top="0",
                z_index="50",
            ) if title else rx.fragment(),

            # Main content area
            rx.box(
                *content,
                padding="24px",
                min_height="calc(100vh - 60px)",
            ),

            margin_left=SIDEBAR_WIDTH,
            min_height="100vh",
            background_color=COLORS["bg"],
            flex="1",
        ),
        display="flex",
        width="100%",
        min_height="100vh",
        background_color=COLORS["bg"],
    )
