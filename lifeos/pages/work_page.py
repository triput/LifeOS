"""Work page — Epic → Project → Task → Subtask tree and kanban views."""

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.work_state import WorkState
from lifeos.state.base_state import AppState
from lifeos.components.template import page_template
from lifeos.components.item_drawer import item_drawer
from lifeos.components.work_tree import work_tree, kanban_board


def filter_bar() -> rx.Component:
    """Filter and view mode controls."""
    return rx.hstack(
        # Status filter
        rx.select.root(
            rx.select.trigger(placeholder="All Statuses"),
            rx.select.content(
                rx.select.item("All Statuses", value="all"),
                rx.select.item("In Progress", value="In Progress"),
                rx.select.item("Planned", value="Planned"),
                rx.select.item("Completed", value="Completed"),
                rx.select.item("On Hold", value="On Hold"),
                rx.select.item("Blocked", value="Blocked"),
                rx.select.item("Cancelled", value="Cancelled"),
                background_color=COLORS["surface"],
            ),
            on_change=WorkState.set_filter_status,
            value=WorkState.filter_status,
        ),

        # Priority filter
        rx.select.root(
            rx.select.trigger(placeholder="All Priorities"),
            rx.select.content(
                rx.select.item("All Priorities", value="0"),
                rx.select.item("1 — Low", value="1"),
                rx.select.item("2 — Normal", value="2"),
                rx.select.item("3 — High", value="3"),
                rx.select.item("4 — Critical", value="4"),
                background_color=COLORS["surface"],
            ),
            on_change=WorkState.set_filter_priority,
        ),

        rx.spacer(),

        # View mode toggle
        rx.hstack(
            rx.button(
                rx.icon("git-branch", size=14),
                "Tree",
                variant=rx.cond(WorkState.view_mode == "tree", "solid", "soft"),
                color_scheme="teal",
                size="2",
                on_click=WorkState.set_view_mode("tree"),
            ),
            rx.button(
                rx.icon("columns-3", size=14),
                "Kanban",
                variant=rx.cond(WorkState.view_mode == "kanban", "solid", "soft"),
                color_scheme="teal",
                size="2",
                on_click=WorkState.set_view_mode("kanban"),
            ),
            spacing="2",
        ),

        # Add Epic button
        rx.button(
            rx.icon("plus", size=16),
            "New Epic",
            color_scheme="teal",
            size="2",
            on_click=WorkState.open_new_drawer("epic", 0),
        ),

        align="center",
        spacing="3",
        width="100%",
        padding="12px 0",
        margin_bottom="16px",
        flex_wrap="wrap",
    )


def empty_state() -> rx.Component:
    """Show when no epics exist."""
    return rx.box(
        rx.vstack(
            rx.icon("inbox", size=48, color=COLORS["muted"]),
            rx.text(
                "No work items yet",
                font_size="18px",
                font_weight="600",
                color=COLORS["muted"],
            ),
            rx.text(
                "Create your first Epic to get started",
                font_size="14px",
                color=COLORS["muted"],
            ),
            rx.button(
                rx.icon("plus", size=16),
                "Create First Epic",
                color_scheme="teal",
                size="3",
                on_click=WorkState.open_new_drawer("epic", 0),
            ),
            align="center",
            spacing="4",
            padding="60px",
        ),
        width="100%",
        display="flex",
        justify_content="center",
    )


def quick_add_epic_bar() -> rx.Component:
    """Quick add Epic inline form."""
    return rx.hstack(
        rx.input(
            placeholder="New epic title (press button to add)...",
            value=WorkState.quick_add_title,
            on_change=WorkState.set_quick_add_title,
            background_color=COLORS["surface"],
            border_color=COLORS["border"],
            color=COLORS["text"],
            flex="1",
            _placeholder={"color": COLORS["muted"]},
        ),
        rx.button(
            rx.icon("plus", size=14),
            "Add Epic",
            color_scheme="teal",
            size="2",
            on_click=WorkState.quick_add_epic,
        ),
        spacing="2",
        width="100%",
        margin_bottom="12px",
    )


@rx.page(
    route="/work",
    title="Work — LifeOS",
    on_load=[AppState.load_settings, WorkState.load_work],
)
def work_page() -> rx.Component:
    """Work page component."""
    return page_template(
        rx.vstack(
            filter_bar(),

            # Quick add epic
            quick_add_epic_bar(),

            # Main content: tree or kanban
            rx.cond(
                WorkState.epics.length() == 0,
                empty_state(),
                rx.cond(
                    WorkState.view_mode == "tree",
                    work_tree(),
                    kanban_board(),
                ),
            ),

            # Item edit drawer
            item_drawer(),

            spacing="0",
            width="100%",
            align="start",
        ),
        title="Work",
    )
