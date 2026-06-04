# ==============================================================================
# File: lifeos/components/item_drawer.py
# Description: Interactive UI component for editing work items and relational data.
# Component: Frontend Component
# Version: 1.0 (Gold Master)
# Created: 2026-03-24
# Last Update: 2026-06-01
# =============================================================================

import reflex as rx
from lifeos.styles import COLORS
from lifeos.state.work_state import WorkState
from lifeos.utils import fmt_mins

def relational_children_widget() -> rx.Component:
    """Reusable widget to display, stage, and commit children items."""
    
    def render_child_row(child):
        is_done = (child["status"] == "Completed")
        child_type_with_s = child["type"].to(str) + "s"
        return rx.hstack(
            rx.checkbox(
                checked=is_done,
                on_change=lambda is_checked: WorkState.toggle_drawer_child(is_checked, child["id"].to(int), child["type"].to(str)),
                color_scheme="teal",
          
            ),
            rx.text(
                child["title"], 
                font_size="14px", 
                color=rx.cond(is_done, COLORS["muted"], COLORS["text"]),
                text_decoration=rx.cond(is_done, "line-through", "none")
            ),
            rx.spacer(),
            rx.icon_button(
                rx.icon("pencil", size=14), size="1", variant="ghost",
                on_click=lambda: WorkState.open_drawer(child["type"].to(str), child["id"].to(int))
            ),
            width="100%", align="center", padding="8px 0", border_bottom=f"1px solid {COLORS['border']}"
        )

    def render_staged_row(title_tuple):
        # Enumerate gives us a tuple: (index, value)
        index = title_tuple[0]
        title = title_tuple[1]
        return rx.hstack(
            rx.icon("circle-dashed", size=16, color=COLORS["warning"]),
            rx.text(title, font_size="14px", color=COLORS["warning"], font_style="italic"),
            rx.spacer(),
            rx.icon_button(
                rx.icon("x", size=14), size="1", variant="ghost", color_scheme="red",
                on_click=lambda: WorkState.remove_staged_child(index)
            ),
            width="100%", align="center", padding="4px 0"
        )

    return rx.cond(
        WorkState.drawer_type != "subtask",
        rx.box(
            rx.text("CHILDREN CONTEXT", font_size="11px", font_weight="700", color=COLORS["muted"], margin_bottom="8px"),
            
            # Active DB Children
            rx.cond(
                WorkState.drawer_children.length() > 0,
                rx.vstack(rx.foreach(WorkState.drawer_children, render_child_row), width="100%", margin_bottom="8px"),
                rx.text("No Children Linked.", font_size="13px", color=COLORS["muted"], font_style="italic", margin_bottom="8px")
            ),
            
            # Staged (Unsaved) Children
            rx.cond(
                WorkState.drawer_staged_children.length() > 0,
                rx.box(
                    rx.vstack(rx.foreach(WorkState.drawer_staged_children, render_staged_row), width="100%"),
                    rx.button("Commit Pending Children", size="2", width="100%", color_scheme="teal", margin_top="8px", on_click=WorkState.commit_staged_children),
                    background_color=COLORS["bg"], padding="12px", border_radius="8px", margin_bottom="12px", border=f"1px dashed {COLORS['warning']}"
                ),
                rx.fragment()
            ),
            
            # Staging Input Area
            rx.hstack(
                rx.input(
                    placeholder="Queue a child item...",
                    value=WorkState.drawer_new_child_title,
                    on_change=WorkState.set_drawer_new_child_title,
                    on_key_down=rx.call_script(f"if(event.key === 'Enter') {{ {WorkState.stage_new_child()} }}"), # JS is safe here!
                    size="2", flex="1", background_color=COLORS["surface"]
                ),
                rx.button(rx.icon("plus", size=16), on_click=WorkState.stage_new_child, size="2", color_scheme="gray", variant="soft"),
                width="100%"
            ),
            margin_bottom="24px", width="100%",
        ),
        rx.fragment()
    )

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

def relational_parent_widget() -> rx.Component:
    """Reusable widget to display an item's parent with click-to-navigate."""
    return rx.box(
        rx.text("PARENT CONTEXT", font_size="11px", font_weight="700", color=COLORS["muted"], margin_bottom="8px"),
        rx.cond(
            # Check if the dictionary actually has keys (meaning a parent exists)
            WorkState.drawer_parent.contains("id"),
            rx.hstack(
                rx.icon("corner-left-up", size=16, color=COLORS["primary"]),
                rx.text(WorkState.drawer_parent["title"], font_size="14px", color=COLORS["text"], font_weight="500"),
                rx.badge(WorkState.drawer_parent["type"], variant="soft", color_scheme="gray"),
                rx.spacer(),
                rx.button(
                    "Open", 
                    size="1", 
                    variant="ghost", 
                    # Click to instantly jump to the parent's drawer!
                    on_click=lambda: WorkState.open_drawer(WorkState.drawer_parent["type"], WorkState.drawer_parent["id"].to(int))
                ),
                align="center",
                padding="12px",
                border=f"1px solid {COLORS['border']}",
                border_radius="8px",
                background_color=COLORS["bg"],
                width="100%",
            ),
            # Empty State
            rx.text("No Parent Linked.", font_size="13px", color=COLORS["muted"], font_style="italic")
        ),
        margin_bottom="24px",
        width="100%",
    )

def relational_children_widget() -> rx.Component:
    """Reusable widget to display and add children items."""
    
    def render_child_row(child):
        is_done = (child["status"] == "Completed")
        
        # THE FIX 1: Explicitly cast to string so Reflex can safely concatenate in JS
        child_type_with_s = child["type"].to(str) + "s"
        
        return rx.hstack(
            rx.checkbox(
                checked=is_done,
                # THE FIX 2: Safely tucked INSIDE the checkbox parameters
                on_change=lambda _: WorkState.fast_complete_item(child["id"].to(int), child_type_with_s),
                color_scheme="teal",
            ),
            rx.text(
                child["title"], 
                font_size="14px", 
                color=rx.cond(is_done, COLORS["muted"], COLORS["text"]),
                text_decoration=rx.cond(is_done, "line-through", "none")
            ),
            rx.spacer(),
            rx.icon_button(
                rx.icon("pencil", size=14), 
                size="1", 
                variant="ghost",
                on_click=lambda: WorkState.open_drawer(child["type"].to(str), child["id"].to(int))
            ),
            width="100%", 
            align="center", 
            padding="8px 0", 
            border_bottom=f"1px solid {COLORS['border']}"
        )

    return rx.cond(
        # Hide the entire children block if we are looking at a Subtask
        WorkState.drawer_type != "subtask",
        rx.box(
            rx.text("CHILDREN CONTEXT", font_size="11px", font_weight="700", color=COLORS["muted"], margin_bottom="8px"),
            
            # The List of Children
            rx.cond(
                WorkState.drawer_children.length() > 0,
                rx.vstack(
                    rx.foreach(WorkState.drawer_children, render_child_row),
                    width="100%", margin_bottom="12px"
                ),
                rx.text("No Children Linked.", font_size="13px", color=COLORS["muted"], font_style="italic", margin_bottom="12px")
            ),
            
            # BONUS: The Quick Add Input
            rx.hstack(
                rx.input(
                    placeholder="Quick add child...",
                    value=WorkState.drawer_new_child_title,
                    on_change=WorkState.set_drawer_new_child_title,
                    size="2", flex="1", background_color=COLORS["surface"]
                ),
                rx.button(
                    rx.icon("plus", size=16), 
                    on_click=WorkState.quick_add_drawer_child,
                    size="2", color_scheme="teal"
                ),
                width="100%"
            ),
            margin_bottom="24px",
            width="100%",
        ),
        rx.fragment() # Render nothing if it's a subtask
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
                                    value=WorkState.drawer_title_str,
                                    on_change=WorkState.set_drawer_title_str,
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
                                        value=WorkState.drawer_description_str,
                                        on_change=WorkState.set_drawer_description_str,
                                        placeholder="Description...",
                                        width="100%",
                                        rows="3",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),

                            ),
                            
                            # --- THE NEW CONTEXT WIDGETS ---
                            relational_parent_widget(),
                            relational_children_widget(),

                            # Status + Priority row
                            rx.cond(
                                ~is_subtask,
                                rx.hstack(
                                    drawer_field(
                                        "STATUS",
                                        rx.select.root(
                                            rx.select.trigger(width="100%"),
                                            rx.select.content(
                                                rx.select.item("Backlog", value="Backlog"),
                                                rx.select.item("Planned", value="Planned"),
                                                rx.select.item("In Progress", value="In Progress"),
                                                rx.select.item("Completed", value="Completed"),
                                                rx.select.item("On Hold", value="On Hold"),
                                                rx.select.item("Blocked", value="Blocked"),
                                                rx.select.item("Cancelled", value="Cancelled"),
                                                background_color=COLORS["surface"],
                                                z_index="9999",
                                                
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
                                                z_index="9999",  # Ensure it appears above other elements
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
                                        "DURATION",
                                        rx.input(
                                            value=WorkState.drawer_duration_str,
                                            on_change=WorkState.set_drawer_duration_str,
                                            placeholder="e.g. 1w 2d 4h 30m",
                                            name="scheduled_duration",
                                                                                                                                   
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
                                        value=WorkState.drawer_estimated_str,
                                        on_change=WorkState.set_drawer_estimated_str,
                                        placeholder="e.g. 1w 2d 4h 30m",
                                        name="estimated_minutes",
                                       
                                        width="100%",
                                        background_color=COLORS["surface"],
                                        border_color=COLORS["border"],
                                        color=COLORS["text"],
                                    ),
                                ),
                                drawer_field(
                                    "ACTUAL",
                                    rx.input(
                                        value=WorkState.drawer_actual_str,
                                        on_change=WorkState.set_drawer_actual_str,
                                        placeholder="e.g. 1w 2d 4h 30m",
                                        name="actual_minutes",
                                        
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
                                on_click=WorkState.delete_drawer_item,
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
