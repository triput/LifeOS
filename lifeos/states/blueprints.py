# ==============================================================================
# File: lifeos/states/blueprints.py
# Description: State management for the automated Blueprint Factory and Parsing.
# Component: State Management Layer
# Version: 1.1 (Gold Master)
# Created: 2026-05-02
# Last Update: 2026-05-04
# ==============================================================================

import reflex as rx
import re
from sqlmodel import select
from pydantic import BaseModel

from lifeos.state import State
from lifeos.models.habitat import LifeBlueprint


# Strict Schema for the UI, using Pydantic Strict Models for better type safety and validation  
class BlueprintItem(BaseModel):
    id: str
    title: str
    target_type: str
    frequency_interval: str
    frequency_unit: str
    is_active: bool


class BlueprintState(State):
    """Handles all logic for automated Cadences and the Tuning Board UI."""
    
    # --- UI DICTIONARIES ---
    # Upgraded to use the strict schema
    tuning_board_list: list[BlueprintItem] = []

    # ==========================================
    # 1. TUNING BOARD UI
    # ==========================================
    
    def load_blueprints(self):
        """Explicitly builds the dictionary for the Tuning Board."""
        with rx.session() as session:
            blueprints = session.exec(select(LifeBlueprint)).all()
            
            ui_ready = []
            for bp in blueprints:
                ui_ready.append(
                    # Instantiating the strictly typed object instead of a dict
                    BlueprintItem(
                        id=str(bp.id),
                        title=bp.title,
                        target_type=bp.target_type.value if hasattr(bp.target_type, 'value') else str(bp.target_type),
                        frequency_interval=str(bp.frequency_interval),
                        frequency_unit=bp.frequency_unit.value if hasattr(bp.frequency_unit, 'value') else str(bp.frequency_unit),
                        is_active=bool(bp.is_active)
                    )
                )
                
            self.tuning_board_list = ui_ready

    def toggle_active(self, bp_id_str: str, new_status: bool):
        """Universal mutator for enabling/disabling cadences."""
        with rx.session() as session:
            bp = session.get(LifeBlueprint, int(bp_id_str))
            if bp:
                bp.is_active = new_status
                session.add(bp)
                session.commit()
        return self.load_blueprints()

    def update_blueprint_interval(self, bp_id_str: str, new_val: str):
        """Safely casts and updates the integer cadence interval."""
        if not new_val.strip():
            return # Don't crash on empty input
        try:
            val = int(new_val)
        except ValueError:
            return 
            
        with rx.session() as session:
            bp = session.get(LifeBlueprint, int(bp_id_str))
            if bp:
                bp.frequency_interval = val
                session.add(bp)
                session.commit()
                
        return self.load_blueprints()

    def update_blueprint_unit(self, bp_id_str: str, new_val: str):
        """Updates the dropdown time unit."""
        with rx.session() as session:
            bp = session.get(LifeBlueprint, int(bp_id_str))
            if bp:
                bp.frequency_unit = new_val
                session.add(bp)
                session.commit()
                
        return self.load_blueprints()

    # ==========================================
    # 2. NLP PARSING ENGINE
    # ==========================================

    def _parse_blueprint_syntax(self, command: str) -> dict | None:
        """
        Interprets natural language to configure the factory.
        Expected format: "Blueprint: [Title] every [Interval] [Unit]"
        """
        clean_cmd = command.strip()
        if not clean_cmd.lower().startswith("blueprint:"):
            return None

        payload = clean_cmd[10:].strip()
        pattern = r"(.+?)\severy\s(?:(\d+)\s)?(days?|weeks?|months?|quarters?|years?)$"
        match = re.search(pattern, payload, re.IGNORECASE)

        if not match:
            return {"error": "Could not parse cadence. Use format: 'Title every 2 weeks'"}

        title = match.group(1).strip()
        interval_str = match.group(2)
        unit_str = match.group(3).lower()
        interval = int(interval_str) if interval_str else 1
        
        unit_map = {
            "day": "Days", "days": "Days",
            "week": "Weeks", "weeks": "Weeks",
            "month": "Months", "months": "Months",
            "quarter": "Quarters", "quarters": "Quarters",
            "year": "Years", "years": "Years"
        }
        
        return {
            "title": title,
            "interval": interval,
            "unit": unit_map.get(unit_str, "Days")
        }