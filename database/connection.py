# ==============================================================================
# File: lifeos/database/connection.py
# Description: Engine creation and session management for the Habitat.
# Component: Infrastructure Layer
# Version: 1.0 (Gold Master)
# Created: 2026-04-20
# Last Update: 2026-04-20
# ==============================================================================

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator


ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / ".env"

# Load the .env file explicitly
load_dotenv(dotenv_path=env_path)

# Logic Audit: Let's see what's actually happening
DB_USER = os.getenv("DB_USER")
if DB_USER is None:
    print(f"⚠️  WARNING: Could not find .env variables at {env_path}")
DB_PASS = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = "localhost"  # Use localhost since Python is running outside Docker for now
DB_PORT = "5432"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLModel engine
# echo=True is helpful for your logic audit (prints SQL to terminal)
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    """
    Initializes the database by creating all defined tables.
    To be called during the Mission Control boot sequence.
    """
    # This will be populated once we import our models
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency generator that provides a database session.
    Ensures the session is closed automatically after use.
    """
    with Session(engine) as session:
        yield session