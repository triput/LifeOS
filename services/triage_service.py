# ==============================================================================
# File: lifeos/services/triage_service.py
# Description: Logic for ingesting, routing, and processing LifeOS signals.
# Component: Service Layer (The Brain)
# Version: 1.0 (Gold Master)
# Created: 2026-04-21
# Last Update: 2026-04-21
# ==============================================================================

from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
from lifeos.models.habitat import LifeTask
from lifeos.models.audit import LifeAuditLog, LogLevel

class TriageService:
    def __init__(self, session: Session):
        """
        Initialize the Triage Service with a database session.
        """
        self.session = session

    def ingest_new_task(
        self, 
        title: str, 
        description: Optional[str] = None, 
        para_category: str = "Inbox"
    ) -> LifeTask:
        """
        Takes a raw signal and commits it to the Habitat as a LifeTask.
        Automatically generates a Standard audit log entry.
        """
        # 1. Create the Task object
        new_task = LifeTask(
            title=title,
            description=description,
            para_category=para_category,
            status="Inbox",
            last_modified_local=datetime.utcnow()
        )
        
        # 2. Add to session and commit to get the ID
        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)
        
        # 3. Log the event (The Forensic Trail)
        self._log_event(
            task_id=new_task.id,
            event_type="Task_Ingested",
            summary=f"New task created: {title} -> [{para_category}]"
        )
        
        return new_task

    def get_all_tasks(self) -> List[LifeTask]:
        """
        Retrieves all tasks currently in the Habitat.
        """
        statement = select(LifeTask)
        return self.session.exec(statement).all()

    def _log_event(
        self, 
        task_id: Optional[int], 
        event_type: str, 
        summary: str, 
        level: LogLevel = LogLevel.STANDARD,
        payload: Optional[dict] = None
    ):
        """
        Internal helper to create audit logs without cluttering business logic.
        """
        log = LifeAuditLog(
            task_id=task_id,
            source="Triage_Service",
            event_type=event_type,
            level=level,
            summary=summary,
            raw_payload=payload
        )
        self.session.add(log)
        self.session.commit()