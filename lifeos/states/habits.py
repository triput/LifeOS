# ==============================================================================
# File: lifeos/states/habits.py
# Description: State management for Daily Telemetry and automated LifeBlueprints.
# Component: State Management Layer
# Version: 1.0 (Gold Master)
# Created: 2026-05-02
# ==============================================================================

import reflex as rx
from typing import List
from datetime import datetime, timezone
from sqlmodel import select

from lifeos.state import State
from lifeos.models.habitat import LifeHabit, HabitLog, LifeBlueprint

class HabitState(State):
    """Handles all logic for Daily Habits and the Blueprint Factory Floor."""
    
    # --- UI DICTIONARIES ---
    telemetry_data: list[dict] = []
    tuning_board_list: list[dict[str, str]] = []

    # ==========================================
    # 1. DAILY TELEMETRY (Habits)
    # ==========================================
    
    def load_telemetry(self):
        """Builds the explicit dictionary for the daily habit tracking UI."""
        today_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        with rx.session() as session:
            # Get all active habits
            habits = session.exec(select(LifeHabit)).all()
            
            ui_ready = []
            for h in habits:
                # Check if a log exists for today
                log = session.exec(
                    select(HabitLog)
                    .where(HabitLog.habit_id == h.id)
                    .where(HabitLog.log_date == today_date_str)
                ).first()
                
                ui_ready.append({
                    "id": str(h.id),
                    "title": h.title,
                    "target_type": "Habit", 
                    "is_completed": bool(log and log.is_completed)
                })
                
            self.telemetry_data = ui_ready

    def toggle_habit(self, habit_id_str: str):
        """Explicitly toggles a daily habit and updates the UI."""
        today_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        habit_id = int(habit_id_str)
        
        with rx.session() as session:
            # Check for existing log today
            existing_log = session.exec(
                select(HabitLog)
                .where(HabitLog.habit_id == habit_id)
                .where(HabitLog.log_date == today_date_str)
            ).first()
            
            if existing_log:
                # Toggle it
                existing_log.is_completed = not existing_log.is_completed
                session.add(existing_log)
            else:
                # Create it
                new_log = HabitLog(
                    habit_id=habit_id,
                    log_date=today_date_str,
                    is_completed=True
                )
                session.add(new_log)
                
            session.commit()
            
        return self.load_telemetry()

 