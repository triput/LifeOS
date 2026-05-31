import reflex as rx
from lifeos.states.management import ManagementState
from lifeos.views.triage_inbox import rapid_capture_bar
from lifeos.views.backlog_board import backlog_grooming_board
from lifeos.views.management_modals import task_assignment_modal
from lifeos.views.management_modals import task_inspector_panel
#from lifeos.views.management_modals import quick_capture_modal




@rx.page(route="/management", title="Management Hub", on_load=ManagementState.load_backlog)
def management_hub_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            # Header
            rx.hstack(
                rx.link(rx.icon(tag="arrow-left"), href="/", color_scheme="gray"),
                rx.heading("Management Hub // Triage", size="7", weight="bold"),
                rx.spacer(),
                rx.badge("BACKLOG GROOMING", color_scheme="indigo", variant="soft"),
                width="100%", align="center", padding_bottom="4", border_bottom="1px solid var(--gray-5)"
            ),
            
            # The Capture Bar
            rapid_capture_bar(),
            
            # The Grooming Board  
            backlog_grooming_board(),
            
            # The Assignment Modal
            task_assignment_modal(),
            
            # The Inspector Panel
            task_inspector_panel(),
            
            # Quick Capture Modal
            #quick_capture_modal(),
            
            width="100%", max_width="1000px", margin_x="auto", padding_top="8"
        )
    )