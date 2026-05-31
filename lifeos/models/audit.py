# ==============================================================================
# File: lifeos/models/audit.py
# Description: Audit and logging models for tracking system events.
# Component: Data Layer (The Habitat)
# Version: 1.0 (Gold Master)
# Created: 2026-04-20
# Last Update: 2026-04-20
# ==============================================================================

from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, JSON, Column
from enum import Enum

class LogLevel(str, Enum):
    STANDARD = "STANDARD"
    VERBOSE = "VERBOSE"

class LifeAuditLog(SQLModel, table=True):
    """
    Forensic log of internal changes and external API handshakes.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="lifetask.id")
    
    source: str      # e.g., "Skedpal_Adapter", "Triage_Service"
    event_type: str  # e.g., "Sync_Push", "Conflict_Resolved"
    level: LogLevel = Field(default=LogLevel.STANDARD)
    summary: str     # Human-readable "Standard" message
    
    # Raw JSON payload for "Verbose" debugging
    # We use sa_column to ensure Postgres handles the JSONB type correctly
    raw_payload: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)