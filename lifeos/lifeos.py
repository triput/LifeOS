# ==============================================================================
# File: lifeos/lifeos.py
# Description: Main entry point and structural layout for LifeOS.
# Component: Frontend / Router Layer
# Version: 4.1 (Gold Master)
# Created: 2026-04-22
# Last Update: 2026-05-03
# ==============================================================================

import reflex as rx

from lifeos.state import State
from lifeos.states.management import ManagementState
from lifeos.states.tasks import TaskState
from lifeos.states.habits import HabitState
from lifeos.states.blueprints import BlueprintState
from lifeos.states.observatory import ObservatoryState
from lifeos.states.academy import AcademyState

from lifeos.views.hud import observatory_hud
from lifeos.views.cards import habitat_health_card, task_card
from lifeos.views.telemetry import telemetry_widget
from lifeos.views.modals import quick_add_modal
from lifeos.views.tuning_board import tuning_board_modal
from lifeos.views.deep_work_view import deep_work_page
from lifeos.states.deep_work import DeepWorkState


from .settings import settings_page
from .backlog import backlog_page
from .learning_hub import learning_hub_page
from .management_hub import management_hub_page


def index() -> rx.Component:
    """The Master Mission Control Layout."""
    return rx.box(
        quick_add_modal(),
        rx.container(
            rx.vstack(
                # Header Row
                rx.hstack(
                    rx.heading("LIFE OS // Command Center", size="7", weight="bold", color_scheme="gray"),
                    rx.spacer(),
                    observatory_hud(),
                    tuning_board_modal(),
            
                    # NEW: Navigation Links
                    rx.link(rx.icon(tag="kanban", size=20), href="/backlog", color_scheme="gray"),
                    rx.link(rx.icon(tag="settings", size=20), href="/settings", color_scheme="gray"),
                    
                    width="100%", align="center", padding_bottom="4", border_bottom="1px solid var(--gray-5)"
                ),
                
                # Main Grid
                rx.grid(
                    # Left Column: Telemetry & Capture
                    rx.vstack(
                        habitat_health_card(),
                        telemetry_widget(),
                        spacing="6", width="100%",
                    ),
                    # Right Column: The Backlog
                    rx.vstack(
                        # NEW: Inbox Header
                        rx.hstack(
                            rx.icon(tag="inbox", color="var(--blue-9)"),
                            rx.heading("Triage Inbox", size="4", weight="bold"),
                            align="center", width="100%", padding_bottom="2"
                            ),

                        
                        # NEW: The Sort & Filter Control Bar
                        rx.hstack(
                            # 1. Domain Filter
                            rx.vstack(
                                rx.text("DOMAIN", size="1", weight="bold", color_scheme="gray"),
                                rx.select(
                                    ["All", "HOME", "TECH", "ACADEMY", "THEATER", "GOVERNANCE"], 
                                    value=TaskState.filter_domain, 
                                    on_change=TaskState.set_filter_domain, 
                                    variant="surface", size="1"
                                ),
                                spacing="1"
                            ),
                            
                            # 2. Status Filter
                            rx.vstack(
                                rx.text("STATUS", size="1", weight="bold", color_scheme="gray"),
                                rx.select(
                                    ["All", "Triage", "Active", "Blocked", "Done"], 
                                    value=TaskState.filter_status, 
                                    on_change=TaskState.set_filter_status, 
                                    variant="surface", size="1"
                                ),
                                spacing="1"
                            ),
                            
                            rx.spacer(),
                            
                            # 3. Sort Engine
                            rx.vstack(
                                rx.text("SORT BY", size="1", weight="bold", color_scheme="gray"),
                                rx.select(
                                    ["Priority", "Due Date", "Age"], 
                                    value=TaskState.sort_mode, 
                                    on_change=TaskState.set_sort_mode, 
                                    variant="soft", color_scheme="gray", size="1"
                                ),
                                spacing="1", align="end"
                            ),
                            width="100%", padding_bottom="2", align="end" 
                        ),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(TaskState.triage_list, task_card),
                                width="100%", spacing="3",
                            ),
                            style={"height": "650px"},
                        ),
                        width="100%", spacing="4",
                    ),
                    columns="2", spacing="8", width="100%",
                ),
                width="100%", spacing="6",
            ),
            size="4", padding="6",
        )
   ) 

app = rx.App()

app.add_page(
    index, 
    on_load=[
        TaskState.load_tasks, 
        ObservatoryState.refresh_observatory, 
        HabitState.load_telemetry, 
        BlueprintState.load_blueprints
    ]
)
app.add_page(settings_page, route="/settings")
app.add_page(backlog_page, route="/backlog", on_load=TaskState.load_tasks)
app.add_page(learning_hub_page, route="/academy", on_load=AcademyState.load_academy_data)

app.add_page(deep_work_page, route="/project/[project_id]", on_load=DeepWorkState.load_project_data)


