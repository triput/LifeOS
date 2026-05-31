# ==============================================================================
# File: lifeos/states/observatory.py
# Description: State management for background polling, temporal triggers, and weather.
# Component: State Management Layer
# Version: 1.0 (Gold Master)
# Created: 2026-05-02
# ==============================================================================

import reflex as rx
import asyncio
import calendar
from datetime import datetime, timezone
from sqlmodel import select

from lifeos.state import State
from lifeos.models.habitat import LifeBlueprint, LifeTask

class ObservatoryState(State):
    """Handles the continuous heartbeat of the application, temporal math, and telemetry."""
    
    # --- ENVIRONMENT VARIABLES ---
    active_profile: str = "Monroe"
    unit_system: str = "Imperial"
    
    weather_temp: str = "--°F"
    weather_condition: str = "Scanning..."
    celestial_time: str = "--:--"
    celestial_label: str = "Orbit"

    # --- EXPLICIT SETTERS ---
    def set_active_profile(self, val: str | list[str]):
        """Sets the active profile, handling both single and multi-select payloads."""
        if isinstance(val, list):
            self.active_profile = val[0] if val else "Monroe"
        else:
            self.active_profile = val

    def set_unit_system(self, val: str | list[str]):
        """Sets the unit system, handling both single and multi-select payloads."""
        if isinstance(val, list):
            self.unit_system = val[0] if val else "Imperial"
        else:
            self.unit_system = val
            
    # ==========================================
    # 1. THE CONVEYOR BELT (Temporal Math & Minter)
    # ==========================================
    
    def _calculate_next_spawn(self, base_date: datetime, interval: int, unit: str) -> datetime:
        """Bulletproof date-math engine for factory cadences."""
        from datetime import timedelta
        
        if unit == "Days":
            return base_date + timedelta(days=interval)
        if unit == "Weeks":
            return base_date + timedelta(weeks=interval)
            
        # Advanced math for non-linear time (Months, Quarters, Years)
        month = base_date.month - 1
        year = base_date.year
        
        if unit == "Months":
            month += interval
        elif unit == "Quarters":
            month += (interval * 3)
        elif unit == "Years":
            year += interval
            
        year += month // 12
        month = (month % 12) + 1
        
        # Safely clamp the day so we don't accidentally invent Feb 30th
        day = min(base_date.day, calendar.monthrange(year, month)[1])
        
        return base_date.replace(year=year, month=month, day=day)

    def run_factory_floor(self):
        """Evaluates blueprints and mints tasks if their temporal strike has passed."""
        now = datetime.now(timezone.utc)
        
        with rx.session() as session:
            blueprints = session.exec(
                select(LifeBlueprint).where(LifeBlueprint.is_active == True)
            ).all()
            
            for bp in blueprints:
                # Target routing - we only mint Tasks here for now
                if bp.target_type.value == "Task" or str(bp.target_type) == "Task": 
                    
                    needs_spawn = False
                    if bp.next_spawn_local is None:
                        needs_spawn = True
                    elif bp.next_spawn_local.replace(tzinfo=timezone.utc) <= now:
                        needs_spawn = True
                        
                    if needs_spawn:
                        new_task = LifeTask(
                            title=bp.title,
                            domain=bp.domain,
                            status="Triage",
                            para_category="Inbox",
                            last_modified_local=now
                        )
                        session.add(new_task)
                        
                        bp.last_spawned_local = now.replace(tzinfo=None)
                        bp.next_spawn_local = self._calculate_next_spawn(
                            now.replace(tzinfo=None), 
                            bp.frequency_interval, 
                            bp.frequency_unit.value if hasattr(bp.frequency_unit, 'value') else str(bp.frequency_unit)
                        )
                        session.add(bp)
                        
            session.commit()

    # ==========================================
    # 2. THE HEARTBEAT (Background Polling)
    # ==========================================

    @rx.event(background=True)
    async def refresh_observatory(self):
        """Continuously polls environmental data and turns the factory gears."""
        while True:
            async with self:
                # 1. Turn the automated gears
                self.run_factory_floor()
                
                # 2. Safely call the task loader if we are stitched into the Root State
                if hasattr(self, 'load_tasks'):
                    self.load_tasks()
                
                # 3. Environmental Telemetry
                if self.active_profile == "Monroe":
                    self.celestial_time, self.celestial_label = "19:52", "Sunset"
                    raw_t = 52 if self.unit_system == "Imperial" else 11
                else:
                    self.celestial_time, self.celestial_label = "20:08", "Sunset"
                    raw_t = 82 if self.unit_system == "Imperial" else 28
                
                suffix = "°F" if self.unit_system == "Imperial" else "°C"
                self.weather_temp = f"{raw_t}{suffix}"
                self.weather_condition = "Clouds" if self.active_profile == "Monroe" else "Clear"
                
            await asyncio.sleep(60)