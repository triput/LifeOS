"""Sidebar navigation component."""

import reflex as rx
from lifeos.styles import COLORS, SIDEBAR_WIDTH


def nav_item(label: str, icon: str, href: str) -> rx.Component:
    """Single sidebar navigation item."""
    is_active = rx.State.router.page.path == href

    return rx.link(
        rx.hstack(
            rx.icon(icon, size=18, color=rx.cond(is_active, COLORS["primary"], COLORS["muted"])),
            rx.text(
                label,
                font_size="14px",
                font_weight=rx.cond(is_active, "600", "400"),
                color=rx.cond(is_active, COLORS["text"], COLORS["muted"]),
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        href=href,
        text_decoration="none",
        display="block",
        padding="10px 12px",
        border_radius="6px",
        background_color=rx.cond(is_active, COLORS["sidebar_active"], "transparent"),
        _hover={"background_color": COLORS["sidebar_active"], "text_decoration": "none"},
        margin_bottom="2px",
        width="100%",
    )


def sidebar() -> rx.Component:
    """Full sidebar navigation."""
    return rx.box(
        # Logo / App name
        rx.hstack(
            rx.box(
                rx.text(
                    "L",
                    font_size="18px",
                    font_weight="800",
                    color=COLORS["primary"],
                    font_family="'Cabinet Grotesk', sans-serif",
                ),
                background_color=COLORS["surface"],
                border_radius="8px",
                padding="6px 10px",
                border=f"1px solid {COLORS['border']}",
            ),
            rx.vstack(
                rx.text(
                    "LifeOS",
                    font_size="16px",
                    font_weight="700",
                    color=COLORS["text"],
                    font_family="'Cabinet Grotesk', sans-serif",
                ),
                rx.text(
                    "Productivity OS",
                    font_size="11px",
                    color=COLORS["muted"],
                ),
                spacing="0",
                align="start",
            ),
            align="center",
            spacing="3",
            margin_bottom="24px",
            padding="0 4px",
        ),

        # Navigation items
        rx.vstack(
            rx.text(
                "MAIN",
                font_size="10px",
                font_weight="600",
                color=COLORS["muted"],
                letter_spacing="0.08em",
                padding="0 12px",
                margin_bottom="4px",
            ),
            nav_item("Dashboard", "layout-dashboard", "/"),
            nav_item("Work", "briefcase", "/work"),
            nav_item("Academy", "graduation-cap", "/academy"),
            nav_item("Agenda", "calendar-days", "/agenda"),
            nav_item("Stats", "bar-chart-2", "/stats"),
            rx.divider(
                border_color=COLORS["border"],
                margin_y="12px",
            ),
            rx.text(
                "SYSTEM",
                font_size="10px",
                font_weight="600",
                color=COLORS["muted"],
                letter_spacing="0.08em",
                padding="0 12px",
                margin_bottom="4px",
            ),
            nav_item("Settings", "settings", "/settings"),
            width="100%",
            spacing="0",
            align="start",
        ),

        # Version tag at bottom
        rx.box(flex="1"),
        rx.text(
            "LifeOS v1.0",
            font_size="11px",
            color=COLORS["muted"],
            padding="8px 12px",
            margin_top="auto",
        ),

        # Sidebar container
        position="fixed",
        top="0",
        left="0",
        height="100vh",
        width=SIDEBAR_WIDTH,
        background_color=COLORS["sidebar_bg"],
        border_right=f"1px solid {COLORS['border']}",
        padding="16px 8px",
        display="flex",
        flex_direction="column",
        z_index="100",
        overflow_y="auto",
    )
