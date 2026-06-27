# ==============================================================================
# File: f:/Code Repo/LifeOS_Django/lifeos_app/urls.py
# Description: Application level URL routing configurations for Django endpoints
# Component: Core / URL Configuration
# Version: 1.0 (Gold Master)
# Created: 2026-06-26
# Last Update: 2026-06-26
# ==============================================================================
from django.urls import path
from . import views

urlpatterns = [
    # 2. Pass the function itself (views.dashboard_view), NOT the string name
    path('', views.dashboard_view, name='dashboard'),
    path('api/task-action/', views.task_action_view, name='task-action'),
    path('toggle-task/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('container/<int:container_id>/', views.container_detail_view, name='container_detail'),
]

