# ==============================================================================
# File: lifeos/state.py
# Description: The True Root State.
# Component: State Management Layer
# Version: 3.1 (Gold Master)
# ==============================================================================

import reflex as rx
from sqlmodel import text

class State(rx.State):
    """The Root State Engine. All domains inherit FROM this, not the other way around."""

    
            
        # Note: We rely on the UI to call TaskState.load_tasks() after this runs