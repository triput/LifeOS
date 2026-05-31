# ==============================================================================
# File: lifeos/learning_hub.py
# Description: The visual dashboard for Academy coursework and PDU tracking.
# Component: Frontend UI (Page)
# Version: 1.0 (Gold Master)
# Created: 2026-05-04
# ==============================================================================

import reflex as rx
from lifeos.states.academy import AcademyState, CertItem, SpecializationItem, CourseItem
from lifeos.views.academy_modals import track_constructor_modal, nested_course_constructor_modal, module_constructor_modal, activity_constructor_modal
from lifeos.models.learning import LifeActivity, LifeCourse, LifeModule, LifeCertification, LifeSpecialization


def render_cert(cert: CertItem) -> rx.Component:
    """Renders a single certification card with a PDU progress bar."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="award", color="var(--amber-9)"),
                rx.text(cert.title, weight="bold", size="3"),
                rx.spacer(),
                # --- FIX: Deferred rx.cond evaluation ---
                rx.badge(cert.status, color_scheme=rx.cond(cert.status == "Active", "green", "tomato")),
                width="100%", align="center"
            ),
            rx.text(f"Issuer: {cert.issuer}", size="1", color_scheme="gray"),
            rx.text(f"Expires: {cert.expiration_date}", size="1", color_scheme="gray"),
            
            # PDU Ledger & Progress Bar
            rx.cond(
                cert.pdus_required > 0,
                rx.vstack(
                    rx.hstack(
                        rx.text("PDU Progress", size="1", weight="bold"),
                        rx.spacer(),
                        rx.text(f"{cert.pdus_earned} / {cert.pdus_required}", size="1"),
                        width="100%", padding_top="2"
                    ),
                    rx.progress(value=cert.pdus_earned, max=cert.pdus_required, color_scheme="blue", height="8px"),
                    width="100%"
                )
            ),
            width="100%", align_items="start", spacing="2"
        ),
        width="100%", variant="surface", padding="3"
    )
    
def render_activity(activity: LifeActivity) -> rx.Component:
    """Renders the smallest unit: a single video, quiz, or lab."""
    return rx.hstack(
        rx.icon(
            tag=rx.cond(activity.activity_type == "Video", "play-circle", "file-text"), 
            size=14, color_scheme="gray"
        ),
        rx.text(activity.title, size="1"),
        rx.spacer(),
        rx.text(f"{activity.duration_minutes} min", size="1", color_scheme="gray"),
        rx.badge(activity.status, color_scheme=rx.cond(activity.status == "Completed", "green", "gray")),
        width="100%", align="center", padding_y="1", padding_left="2"
    )

def render_module(module: LifeModule) -> rx.Component:
    """Renders a module folder and loops through its activities."""
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="folder", size=14, color_scheme="blue"),
            rx.text(module.title, weight="bold", size="2"),
            rx.spacer(),
            rx.icon_button(rx.icon(tag="plus", size=14), size="1", variant="ghost", color_scheme="gray", on_click=lambda: AcademyState.open_activity_modal(module.id)),
            rx.badge(module.status, color_scheme=rx.cond(module.status == "Completed", "green", "blue")),
            width="100%", align="center", padding_y="1"
        ),
        # Loop through the activities inside this module
        rx.vstack(
            rx.foreach(module.activities, render_activity),
            width="100%", padding_left="3", border_left="2px solid var(--gray-3)"
        ),
        width="100%", align_items="start", padding_top="2"
    )   
    
def render_course(course: CourseItem) -> rx.Component:
    """Renders a single course as a row, expanding into its modules."""
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="book-open", size=16, color_scheme="gray"),
            rx.vstack(
                rx.text(course.title, weight="medium", size="2"),
                rx.text(f"Progress: {course.progress}%", size="1", color_scheme="gray"),
                spacing="0", align_items="start"
            ),
            rx.spacer(),
            rx.icon_button(rx.icon(tag="plus", size=14), size="1", variant="ghost", color_scheme="gray", on_click=lambda: AcademyState.open_module_modal(course.id)),
            rx.badge(course.status, color_scheme=rx.cond(course.status == "In Progress", "blue", "gray")),
            width="100%", align="center", padding_y="2"
        ),
        
        # --- NEW: Render the nested modules if they exist ---
        rx.cond(
            course.modules.length() > 0,
            rx.vstack(
                rx.foreach(course.modules, render_module),
                width="100%", padding_left="4", padding_bottom="3"
            )
        ),
        width="100%", align_items="start", border_bottom="1px solid var(--gray-4)"
    )
    
def render_specialization(spec: SpecializationItem) -> rx.Component:
    """Renders an expanding accordion for nested learning tracks."""
    return rx.accordion.item(
        header=rx.hstack(
            rx.icon(tag="layers"),
            rx.text(spec.title, weight="bold"),
            rx.spacer(),
            
            rx.badge(f"{spec.progress}%", color_scheme="blue"),
            width="100%", align="center", padding_right="4"
        ),
        content=rx.vstack(
            rx.foreach(spec.courses, render_course),
            rx.icon_button(rx.icon(tag="plus", size=14),"Add Course", size="1", variant="ghost", color_scheme="gray", on_click=lambda: AcademyState.open_course_modal(spec.id)),
            width="100%", padding_left="4"
        ),
        value=spec.id,
    )

def learning_hub_page() -> rx.Component:
    """The Master Academy Dashboard."""
    return rx.container(
        rx.vstack(
            # --- Header ---
            rx.hstack(
                rx.link(rx.icon(tag="arrow-left"), href="/", color_scheme="gray"),
                rx.heading("Academy // Learning Hub", size="7", weight="bold"),
                rx.spacer(),
                
                # --- NEW: The Trigger Button & Modal ---
                rx.button(
                    rx.icon(tag="plus"), "New Track", 
                    color_scheme="blue", 
                    on_click=AcademyState.toggle_track_modal
                ),
                track_constructor_modal(), # Injects the hidden modal into the DOM
                nested_course_constructor_modal(),
                module_constructor_modal(),
                activity_constructor_modal(),
                
                rx.badge("ACADEMY DOMAIN", color_scheme="blue", variant="soft"),
                width="100%", align="center", padding_bottom="4", border_bottom="1px solid var(--gray-5)"
            ),
            
            # --- Two-Column Layout ---
            rx.hstack(
                # Left Column: Active Learning Tracks
                rx.vstack(
                    rx.heading("Active Tracks & Courses", size="4", weight="bold", color_scheme="gray"),
                    
                    # 1. Render Specializations
                    rx.card(
                        rx.cond(
                            AcademyState.specialization_list.length() > 0,
                            rx.accordion.root(
                                rx.foreach(AcademyState.specialization_list, render_specialization),
                                width="100%", variant="ghost", type="multiple"
                            ),
                            rx.text("No active Specializations.", color_scheme="gray", size="2")
                        ),
                        width="100%", padding="2", variant="surface"
                    ),
                    
                    # 2. NEW: Render Standalone Courses!
                    rx.cond(
                        AcademyState.standalone_course_list.length() > 0,
                        rx.card(
                            rx.vstack(
                                rx.foreach(AcademyState.standalone_course_list, render_course),
                                width="100%", padding="2"
                            ),
                            width="100%", variant="surface", margin_top="4"
                        )
                    ),
                    width="60%", align_items="start", spacing="3"
                ),
                
                # Right Column: Certification & PDU Ledger
                rx.vstack(
                    rx.heading("Certifications & Renewals", size="4", weight="bold", color_scheme="gray"),
                    rx.foreach(AcademyState.cert_list, render_cert),
                    width="40%", align_items="start", spacing="3"
                ),
                width="100%", align_items="start", spacing="6", padding_top="4"
            ),
            width="100%"
        ),
        size="4", padding="6"
    )