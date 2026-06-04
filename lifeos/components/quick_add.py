import reflex as rx
from lifeos.state.work_state import WorkState
from lifeos.styles import COLORS
from lifeos.state.capture_state import CaptureState

def universal_quick_add_widget(domain: str = "work") -> rx.Component:
    
    if domain == "academy":
        type_options = ["Specialization", "Course", "Module", "Task"]
        placeholder_text = "Capture new learning item..."
    else:
        type_options = ["Epic", "Project", "Task", "Subtask"]
        placeholder_text = "Capture new work item..."

    return rx.hstack(
        # 1. The Item Type Dropdown
        rx.select.root(
            rx.select.trigger(placeholder="Select Type", width="150px"),
            rx.select.content(
                rx.foreach(type_options, lambda type_name: rx.select.item(type_name, value=type_name)),
            ),
            value=CaptureState.capture_type, 
            on_change=CaptureState.set_capture_type, # This now triggers the DB lookup!
        ),
        
        # 2. THE FIX: The Dynamic Parent Dropdown
        rx.cond(
            CaptureState.available_parents.length() > 0,
            rx.select.root(
                rx.select.trigger(placeholder="Select Parent...", width="180px"),
                rx.select.content(
                    rx.foreach(
                        CaptureState.available_parents,
                        lambda p: rx.select.item(p["label"].to(str), value=p["value"].to(str)))
                    ),
                
                value=CaptureState.capture_parent_id,
                on_change=CaptureState.set_capture_parent_id,
            ),
            rx.fragment() # Render nothing if it's an Epic or Specialization
        ),
        
        # 3. The Title Input
        rx.input(
            placeholder=placeholder_text,
            value=CaptureState.capture_title,
            on_change=CaptureState.set_capture_title,
            on_key_down=rx.call_script(f"if(event.key === 'Enter') {{ {CaptureState.execute_capture()} }}"),
            flex="1",
        ),
        rx.button(
            "Capture",
            on_click=CaptureState.execute_capture,
            color_scheme="teal",
        ),
        width="100%",
        padding="16px",
        
        # VERY IMPORTANT: When this component loads on the page, tell the engine its domain!
        on_mount=lambda: CaptureState.set_capture_domain(domain)
    )