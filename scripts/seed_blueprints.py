# ==============================================================================
# File: seed_blueprints.py
# Description: Injects initial automated cadences into the Blueprint Factory.
# Component: Database / Utility Layer
# Version: 1.0 (Gold Master)
# Created: 2026-05-04
# Last Update: 2026-05-04
# ==============================================================================

from sqlmodel import Session, select
import reflex as rx

# Adjust these imports if your exact paths differ

from lifeos.models.habitat import LifeBlueprint, CadenceType, FrequencyUnit

def seed_factory():
    """Populates the database with core automated cadences."""
    
    seed_data = [
        # --- HOME & HABITAT ---
        {
            "title": "Walk the dogs at Sky River Park",
            "domain": "HOME",
            "target_type": "Habit",
            "cadence_type": CadenceType.FIXED_CALENDAR, # <-- THE FIX
            "frequency_interval": 1,
            "frequency_unit": "Days",
            "is_active": True
        },
        {
            "title": "Inventory hot sauce balancing ingredients (Agave, Pears)",
            "domain": "HOME",
            "target_type": "Task",
            "cadence_type": CadenceType.FIXED_CALENDAR,
            "frequency_interval": 2,
            "frequency_unit": "Weeks",
            "is_active": True
        },
        
        # --- THEATER ---
        {
            "title": "Review 'Angry Housewives' piano and reed scores",
            "domain": "THEATER",
            "target_type": "Habit",
            "cadence_type": CadenceType.FIXED_CALENDAR,
            "frequency_interval": 3,
            "frequency_unit": "Days",
            "is_active": True
        },
        
        # --- TECH & ACADEMY ---
        {
            "title": "Read one chapter of ReAct multi-agent orchestration docs",
            "domain": "ACADEMY",
            "target_type": "Habit",
            "cadence_type": CadenceType.FIXED_CALENDAR,
            "frequency_interval": 1,
            "frequency_unit": "Days",
            "is_active": True
        },
        {
            "title": "Clear RTX 3090 VRAM cache and update local model weights",
            "domain": "TECH",
            "target_type": "Task",
            "cadence_type": CadenceType.FIXED_CALENDAR,
            "frequency_interval": 1,
            "frequency_unit": "Weeks",
            "is_active": True
        },
        {
            "title": "PMP Mindset and Earned Value formulas review session",
            "domain": "ACADEMY",
            "target_type": "Task",
            "cadence_type": CadenceType.FIXED_CALENDAR,
            "frequency_interval": 2,
            "frequency_unit": "Weeks",
            "is_active": True
        },

        # --- GOVERNANCE (LifeOS) ---
        {
            "title": "Tactical Backlog Grooming & Triage",
            "domain": "GOVERNANCE",
            "target_type": "Task",
            "cadence_type": CadenceType.FIXED_CALENDAR,
            "frequency_interval": 1,
            "frequency_unit": "Weeks",
            "is_active": True
        },
        {
            "title": "LifeOS PostgreSQL Database Backup",
            "domain": "GOVERNANCE",
            "target_type": "Task",
            "cadence_type": CadenceType.FIXED_CALENDAR,
            "frequency_interval": 1,
            "frequency_unit": "Months",
            "is_active": True
        }
    ]

    # Reflex uses a context manager for the DB engine
    with rx.session() as session:
        # Check if blueprints already exist to avoid duplicates
        # existing = session.exec(select(LifeBlueprint)).all()
        # if existing:
        #     print(f"Factory already holds {len(existing)} blueprints. Seeding aborted.")
        #     return

        print("Spinning up the Blueprint Factory...")
        for data in seed_data:
            bp = LifeBlueprint(**data)
            session.add(bp)
            
        session.commit()
        print("Successfully injected 8 automation cadences. You may now load the Tuning Board.")

if __name__ == "__main__":
    seed_factory()