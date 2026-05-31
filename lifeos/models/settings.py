# ==============================================================================
# File: lifeos/models/settings.py
# Description: System-wide configuration and retention policies.
# Component: Data Layer (The Habitat)
# Version: 1.0 (Gold Master)
# Created: 2026-04-20
# Last Update: 2026-04-20
# ==============================================================================

from typing import Optional
from sqlmodel import Field, SQLModel

class SystemSettings(SQLModel, table=True):
    """
    Operational settings for LifeOS, including Janitor policies.
    """
    id: Optional[int] = Field(default=1, primary_key=True)
    
    # Maintenance Settings (Days to keep logs)
    standard_log_retention: int = Field(default=180) 
    verbose_log_retention: int = Field(default=28)   # Trish's 4-week example
    
    auto_prune_enabled: bool = Field(default=True)
    
    # System Pulse
    is_sync_active: bool = Field(default=True)