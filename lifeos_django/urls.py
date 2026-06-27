# ==============================================================================
# File: f:/Code Repo/LifeOS_Django/lifeos_django/urls.py
# Description: Root URL routing configurations mapping core views and admin modules
# Component: Core / URL Configuration
# Version: 1.0 (Gold Master)
# Created: 2026-06-26
# Last Update: 2026-06-26
# ==============================================================================
"""Root URL configuration for lifeos_django project."""

from django.contrib import admin
from django.urls import path, include
from lifeos_app import views as app_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", app_views.login_view, name="login"),
    path("logout/", app_views.logout_view, name="logout"),
    path("", include("lifeos_app.urls")),
]

