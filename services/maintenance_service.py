# ==============================================================================
# File: services/maintenance_service.py
# Description: Automated cleanup and health checks for the Habitat.
# Component: Service Layer (The Brain)
# Version: 1.0 (Gold Master)
# Created: 2026-04-21
# Last Update: 2026-04-21
# ==============================================================================

from datetime import datetime, timedelta
from sqlmodel import Session, select, delete, func
from lifeos.models.audit import LifeAuditLog, LogLevel
from lifeos.models.settings import SystemSettings
from lifeos.models.habitat import LifeTask
import logging

logger = logging.getLogger("Maintenance_Service")

class MaintenanceService:
    def __init__(self, session: Session):
        self.session = session

    def get_habitat_stats(self) -> dict:
        """
        Returns a snapshot of the Habitat's current data volume.
        """
        task_count = self.session.exec(select(func.count(LifeTask.id))).one()
        log_count = self.session.exec(select(func.count(LifeAuditLog.id))).one()
        
        return {
            "task_count": task_count,
            "log_count": log_count,
        }
    
    def run_log_cleanup(self):
        """
        Prunes logs based on the retention rules in SystemSettings.
        """
        # 1. Fetch current settings
        settings = self.session.exec(select(SystemSettings)).first()
        
        # If no settings exist yet, we create default ones
        if not settings:
            settings = SystemSettings()
            self.session.add(settings)
            self.session.commit()
            self.session.refresh(settings)

        if not settings.auto_prune_enabled:
            logger.info("⏸️ Auto-pruning is disabled in settings.")
            return

        # 2. Prune Verbose Logs (Default: 28 days / 4 weeks)
        self._prune_logs(LogLevel.VERBOSE, settings.verbose_log_retention)

        # 3. Prune Standard Logs (Default: 180 days / 6 months)
        self._prune_logs(LogLevel.STANDARD, settings.standard_log_retention)

    def _prune_logs(self, level: LogLevel, days_retention: int):
        """
        Internal logic to delete logs older than X days for a specific level.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_retention)
        
        statement = delete(LifeAuditLog).where(
            LifeAuditLog.level == level,
            LifeAuditLog.timestamp < cutoff_date
        )
        
        results = self.session.exec(statement)
        self.session.commit()
        
        logger.info(f"🧹 Pruned {level} logs older than {days_retention} days.") 