# ==============================================================================
# File: lifeos/views/hud.py
# Description: Environmental and temporal telemetry.
# Component: Frontend / UI Layer
# Version: 1.0 (Gold Master)
# ==============================================================================

import reflex as rx
from lifeos.states.observatory import ObservatoryState

def observatory_hud() -> rx.Component:
    """Real-time environmental synchronization."""
    return rx.hstack(
        rx.badge(rx.icon(tag="map-pin", size=14), ObservatoryState.active_profile, color_scheme="gray", variant="surface"),
        rx.badge(rx.icon(tag="thermometer", size=14), ObservatoryState.weather_temp, color_scheme="amber", variant="surface"),
        rx.badge(rx.icon(tag="cloud", size=14), ObservatoryState.weather_condition, color_scheme="blue", variant="surface"),
        rx.badge(rx.icon(tag="moon", size=14), f"{ObservatoryState.celestial_label}: {ObservatoryState.celestial_time}", color_scheme="indigo", variant="surface"),
        spacing="3"
    )