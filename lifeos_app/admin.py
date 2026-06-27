# ==============================================================================
# File: f:/Code Repo/LifeOS_Django/lifeos_app/admin.py
# Description: Django Admin panel configuration and registration for app models
# Component: Core / Admin Interfaces
# Version: 1.0 (Gold Master)
# Created: 2026-06-26
# Last Update: 2026-06-26
# ==============================================================================
"""Django Admin registration configuration for the LifeOS Django application.

Configures listing, filtration, and inline management for WorkspaceContainer,
ExecutionItem, and AppSettings records (FR-ADM-001).
"""

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    AppSettings,
    WorkspaceContainer,
    ExecutionItem,
)

class ExecutionItemInline(GenericTabularInline):
    """
    Allows editing actionable ExecutionItems directly inside WorkspaceContainer screens.
    """
    model = ExecutionItem
    extra = 1
    fields = ('title', 'item_type', 'domain_category', 'para_category', 'is_completed', 'is_archived', 'is_deleted')


@admin.register(WorkspaceContainer)
class WorkspaceContainerAdmin(admin.ModelAdmin):
    """
    Admin configuration for type-discriminated structural containers.
    """
    list_display = ('title', 'container_type', 'parent', 'domain_category', 'para_category', 'is_archived', 'created_at')
    list_filter = ('container_type', 'domain_category', 'para_category', 'is_archived')
    search_fields = ('title',)
    ordering = ('container_type', 'order', 'title')
    inlines = [ExecutionItemInline]


@admin.register(ExecutionItem)
class ExecutionItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for actionable tasks and activities.
    """
    list_display = ('title', 'item_type', 'content_object', 'domain_category', 'para_category', 'is_completed', 'is_active', 'is_archived', 'is_deleted')
    list_filter = ('item_type', 'domain_category', 'para_category', 'is_completed', 'is_active', 'is_archived', 'is_deleted')
    search_fields = ('title',)
    ordering = ('-created_at',)


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for the system settings singleton.
    """
    list_display = ('__str__', 'pomodoro_duration', 'start_of_work_day', 'enable_ai_scheduling')
    
    def has_add_permission(self, request):
        # Prevent creating multiple configurations
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent removing system preferences
        return False
