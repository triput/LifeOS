# ==============================================================================
# File: scripts/seed_db.py
# Description: Utility to hydrate the PostgreSQL database with PARA seed data.
# Component: Data Layer (Utilities)
# Version: 1.1 (Gold Master)
# Created: 2026-04-23
# Last Update: 2026-04-23
# ==============================================================================

import sys
import os
from datetime import datetime, timezone
from sqlalchemy import text

# Ensure the script can see the main app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, SQLModel, select
from lifeos.models.habitat import LifeTask
from rxconfig import config

# 1. Setup the Engine using your rxconfig string
engine = create_engine(config.db_url)

def seed_database():
    """Wipes the LifeTask table and pours in fresh PARA-method data."""
    print(f"🚀 Connecting to: {config.db_url}")
    
    # Define a set of diverse tasks to test your PARA filters
    seed_data = [
        # Inbox / Triage
        {"title": "Buy Carolina Reaper seeds", "description": "Need to start the 2027 batch early.", "para_category": "Inbox", "status": "Inbox"},
        {"title": "Review Newsies piano score", "description": "Check the transition in Act 1.", "para_category": "Inbox", "status": "Inbox"},
        
        # Projects (Garnet)
        {"title": "Finish LifeOS Database Wiring", "description": "Switch from mock to Postgres.", "para_category": "Projects", "status": "Active", "priority": 1},
        {"title": "Plan Bangkok 2026 Trip", "description": "Check visa requirements and flight paths.", "para_category": "Projects", "status": "Active", "priority": 2},
        
        # Areas (Emerald)
        {"title": "Daily Dog Walk (Monroe Trails)", "description": "Keep the Corgis moving.", "para_category": "Areas", "status": "Active"},
        {"title": "Theater Board Monthly Audit", "description": "Review the Cascade Community Theatre budget.", "para_category": "Areas", "status": "Active"},
        
        # Resources
        {"title": "Reflex Framework Documentation", "description": "Keep as a reference for state management.", "para_category": "Resources", "status": "Active"},
        {"title": "Hot Sauce Recipe Log", "description": "Agave vs Honey ratios for Reapers.", "para_category": "Resources", "status": "Active"},
    ]

    with Session(engine) as session:
        print("🗑️  Cleaning tables with extreme prejudice (CASCADE)...")
        
        # 1. Use TRUNCATE CASCADE to wipe lifetask and anything that depends on it
        # This handles LifeAuditLog automatically and resets the ID counters to 1.
        session.exec(text("TRUNCATE TABLE lifetask RESTART IDENTITY CASCADE;"))
        session.commit()

        # Add the new seeds
        print(f"🌱 Planting {len(seed_data)} seed tasks...")
        for item in seed_data:
            task = LifeTask(
                **item,
                last_modified_local=datetime.now(timezone.utc),
                notion_id=f"notion_{os.urandom(4).hex()}" # Mocking the IDs
            )
            session.add(task)
        
        session.commit()
        print("✅ Database Hydration Complete!")

if __name__ == "__main__":
    seed_database()