# ==============================================================================
# File: lifeos/components/template.py
# Description: Base page template that wraps content with sidebar and global UI
# Component: Frontend / Layout
# Version: 1.0 (Gold Master)
# Created: 2026-06-01
# Last Update: 2026-06-01
# ==============================================================================

import reflex as rx
from lifeos.styles import COLORS, SIDEBAR_WIDTH
from lifeos.components.sidebar import sidebar
from lifeos.components.item_drawer import item_drawer
from lifeos.components.academy_drawer import academy_drawer
from lifeos.state.base_state import AppState  # Ensure this is imported!

def page_template(*content: rx.Component, title: str = "") -> rx.Component:
    """Wrap page content with the sidebar, main layout, and global overlays."""
    return rx.box(
        # Conditionally render the sidebar based on state
        rx.cond(AppState.sidebar_open, sidebar(), rx.fragment()),
        rx.box(
            # Top header bar
            rx.hstack(
                rx.hstack(
                    rx.icon_button(
                        rx.icon("menu", size=20), 
                        on_click=AppState.toggle_sidebar, 
                        variant="ghost", 
                        color_scheme="gray"
                    ),
                    rx.text(
                        title,
                        font_size="22px",
                        font_weight="700",
                        color=COLORS["text"],
                        font_family="'Cabinet Grotesk', sans-serif",
                    ),
                    align="center",
                    spacing="3",
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

            # Dynamically adjust the margin so content shifts when closed
            margin_left=rx.cond(AppState.sidebar_open, SIDEBAR_WIDTH, "0px"),
            transition="margin-left 0.2s ease-in-out",
            min_height="100vh",
            background_color=COLORS["bg"],
            flex="1",
        ),
        
        # --- GLOBAL OVERLAYS ---
        item_drawer(),
        academy_drawer(),

        display="flex",
        width="100%",
        min_height="100vh",
        background_color=COLORS["bg"],
    )