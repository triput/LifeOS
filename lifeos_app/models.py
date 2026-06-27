# ==============================================================================
# File: f:/Code Repo/LifeOS_Django/lifeos_app/models.py
# Description: Models definitions for WorkspaceContainer, ExecutionItem, and AppSettings
# Component: Core / Database Models
# Version: 1.0 (Gold Master)
# Created: 2026-06-26
# Last Update: 2026-06-26
# ==============================================================================
"""Database model definitions for the LifeOS Django application.

Contains the unified DRY models: WorkspaceContainer (for hierarchical structure)
and ExecutionItem (for actionable items), along with system preferences (AppSettings).
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

class AppSettings(models.Model):
    """
    Singleton model for system-wide user preferences.
    Always access via AppSettings.get_solo()
    """
    pomodoro_duration = models.IntegerField(default=25)
    start_of_work_day = models.TimeField(default="09:00:00")
    enable_ai_scheduling = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "System AppSettings"


class WorkspaceContainer(models.Model):
    """
    Unified type-discriminated container supporting hierarchical structures:
    Epics, Projects, Specializations, Courses, and Modules.
    """
    CONTAINER_TYPES = [
        ('Epic', 'Epic'),
        ('Project', 'Project'),
        ('Specialization', 'Specialization'),
        ('Course', 'Course'),
        ('Module', 'Module'),
    ]

    DOMAIN_CATEGORIES = [
        ('Tech/Career', 'Tech/Career'),
        ('Theater', 'Theater'),
        ('Academy', 'Academy'),
        ('Home', 'Home'),
        ('Governance/Compliance', 'Governance/Compliance'),
    ]

    PARA_CATEGORIES = [
        ('Projects', 'Projects'),
        ('Areas', 'Areas'),
        ('Resources', 'Resources'),
        ('Archives', 'Archives'),
    ]

    title = models.CharField(max_length=255)
    container_type = models.CharField(max_length=50, choices=CONTAINER_TYPES)
    
    parent = models.ForeignKey(
        'self', null=True, blank=True, 
        on_delete=models.CASCADE, related_name='children'
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Category markers (FR-DATA-004)
    domain_category = models.CharField(
        max_length=100, choices=DOMAIN_CATEGORIES, null=True, blank=True, db_index=True
    )
    para_category = models.CharField(
        max_length=100, choices=PARA_CATEGORIES, null=True, blank=True, db_index=True
    )
    
    # Archival state (FR-LIFE-001)
    is_archived = models.BooleanField(default=False, db_index=True)

    def clean(self):
        # Prevent self-referencing hierarchy cycles (FR-DATA-001.3)
        if self.parent == self:
            raise ValidationError("A container cannot be its own parent.")
        
        # Prevent deeper cycles
        curr = self.parent
        while curr is not None:
            if curr == self:
                raise ValidationError("Circular relationship detected in container hierarchy.")
            curr = curr.parent

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.container_type}: {self.title}"


class ExecutionItem(models.Model):
    """
    Unified actionable leaf-node model representing Tasks, Subtasks,
    LearningTasks, and LifeActivities.
    """
    ITEM_TYPES = [
        ('Task', 'Task'),
        ('Subtask', 'Subtask'),
        ('LearningTask', 'LearningTask'),
        ('LifeActivity', 'LifeActivity'),
    ]

    DOMAIN_CATEGORIES = [
        ('Tech/Career', 'Tech/Career'),
        ('Theater', 'Theater'),
        ('Academy', 'Academy'),
        ('Home', 'Home'),
        ('Governance/Compliance', 'Governance/Compliance'),
    ]

    PARA_CATEGORIES = [
        ('Projects', 'Projects'),
        ('Areas', 'Areas'),
        ('Resources', 'Resources'),
        ('Archives', 'Archives'),
    ]

    title = models.CharField(max_length=255)
    item_type = models.CharField(max_length=50, choices=ITEM_TYPES)
    is_completed = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic relation to link to either WorkspaceContainer or another ExecutionItem
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Focus Engine metrics (FR-FOCUS-001)
    duration_estimate = models.PositiveIntegerField(help_text="Minutes", default=30)
    time_spent_seconds = models.PositiveIntegerField(default=0, help_text="Seconds elapsed")
    is_active = models.BooleanField(default=False, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)

    # Category markers (FR-DATA-004)
    domain_category = models.CharField(
        max_length=100, choices=DOMAIN_CATEGORIES, null=True, blank=True, db_index=True
    )
    para_category = models.CharField(
        max_length=100, choices=PARA_CATEGORIES, null=True, blank=True, db_index=True
    )

    # Archival & Soft delete states (FR-LIFE-001, FR-LIFE-002)
    is_archived = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.item_type}: {self.title}"