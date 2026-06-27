# ==============================================================================
# File: f:/Code Repo/LifeOS_Django/lifeos_app/views.py
# Description: Views implementing auth, focus engine controls, and context HUD logic
# Component: Core / Views
# Version: 1.0 (Gold Master)
# Created: 2026-06-26
# Last Update: 2026-06-26
# ==============================================================================
"""View controllers for the LifeOS application.

Contains dashboard views, HUD calculations, focus engine endpoints,
scoped workspace handlers, and authentication routes.
"""

import json
from django.db import models
from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

from .models import WorkspaceContainer, ExecutionItem
from .telemetry import OpenMeteoAdapter, NoaaKpAdapter

def login_view(request):
    """
    Renders the login view and handles authenticated session setups.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Hard single-owner enforcement check on login (FR-SEC-003)
            if user.is_superuser:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, "Forbidden: Only the owner account is allowed access.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """
    Terminates the authenticated session and redirects.
    """
    auth_logout(request)
    return redirect('login')


def dashboard_view(request):
    """
    Renders the consolidated workspace dashboard and the Unified Domain Context HUD.
    """
    # 1. Active (incomplete, non-deleted, non-archived) actionable ExecutionItems
    active_items = ExecutionItem.objects.filter(
        is_completed=False,
        is_deleted=False,
        is_archived=False
    ).order_by('created_at')

    # 2. Dynamic progress vectors by Domain Category (FR-HUD-001)
    domain_stats = ExecutionItem.objects.filter(
        is_deleted=False,
        is_archived=False
    ).values('domain_category').annotate(
        total_tasks=Count('id'),
        completed_tasks=Count('id', filter=models.Q(is_completed=True)),
        total_time_spent=Sum('time_spent_seconds'),
    )

    # 3. Dynamic progress vectors by PARA Category (FR-HUD-001)
    para_stats = ExecutionItem.objects.filter(
        is_deleted=False,
        is_archived=False
    ).values('para_category').annotate(
        total_tasks=Count('id'),
        completed_tasks=Count('id', filter=models.Q(is_completed=True)),
        total_time_spent=Sum('time_spent_seconds'),
    )

    # Process stats to ensure clean list output with percentages
    processed_domains = []
    for stat in domain_stats:
        cat = stat['domain_category'] or 'Uncategorized'
        total = stat['total_tasks']
        completed = stat['completed_tasks']
        time_spent = stat['total_time_spent'] or 0
        rate = int((completed / total) * 100) if total > 0 else 0
        processed_domains.append({
            'category': cat,
            'total': total,
            'completed': completed,
            'rate': rate,
            'time_spent': time_spent
        })

    processed_para = []
    for stat in para_stats:
        cat = stat['para_category'] or 'Uncategorized'
        total = stat['total_tasks']
        completed = stat['completed_tasks']
        time_spent = stat['total_time_spent'] or 0
        rate = int((completed / total) * 100) if total > 0 else 0
        processed_para.append({
            'category': cat,
            'total': total,
            'completed': completed,
            'rate': rate,
            'time_spent': time_spent
        })

    # 4. Environment Telemetry from Open-Meteo & NOAA SWPC (FR-HUD-004)
    weather_adapter = OpenMeteoAdapter()
    weather_data = weather_adapter.get_telemetry()
    
    kp_adapter = NoaaKpAdapter()
    kp_data = kp_adapter.get_kp_index()

    context = {
        'tasks': active_items,
        'domain_stats': processed_domains,
        'para_stats': processed_para,
        'weather': weather_data,
        'kp': kp_data,
    }
    return render(request, 'dashboard.html', context)


def container_detail_view(request, container_id):
    """
    Renders workspace view scoped to a selected WorkspaceContainer.
    Excludes completed, archived, and soft-deleted items by default.
    """
    container = get_object_or_404(WorkspaceContainer, id=container_id, is_archived=False)
    
    # Get immediate child containers
    child_containers = WorkspaceContainer.objects.filter(
        parent=container,
        is_archived=False
    ).order_by('order', 'title')

    # Fetch ExecutionItems linked to this WorkspaceContainer (generic relation)
    container_type = ContentType.objects.get_for_model(WorkspaceContainer)
    container_items = ExecutionItem.objects.filter(
        content_type=container_type,
        object_id=container.id,
        is_completed=False,
        is_deleted=False,
        is_archived=False
    ).order_by('created_at')

    context = {
        'container': container,
        'child_containers': child_containers,
        'tasks': container_items,
    }
    return render(request, 'container_detail.html', context)


def task_action_view(request):
    """
    Consolidated focus engine endpoint for ExecutionItem focus actions.
    Supports start, pause, resume, and stop actions.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    task_id = data.get('task_id')
    action = data.get('action') # 'start', 'stop', 'pause', 'resume'
    
    if not task_id or not action:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    task = get_object_or_404(ExecutionItem, id=task_id, is_deleted=False)

    if action in ['start', 'resume']:
        # Ensure only one task can be active at a time to prevent leakage
        active_timers = ExecutionItem.objects.filter(is_active=True).exclude(id=task.id)
        for active_task in active_timers:
            if active_task.started_at:
                delta = timezone.now() - active_task.started_at
                active_task.time_spent_seconds += int(delta.total_seconds())
            active_task.is_active = False
            active_task.started_at = None
            active_task.save()

        task.is_active = True
        task.started_at = timezone.now()
        task.save()
        return JsonResponse({
            'status': 'started', 
            'started_at': task.started_at.isoformat(),
            'time_spent_seconds': task.time_spent_seconds
        })

    elif action in ['stop', 'pause']:
        if task.is_active and task.started_at:
            delta = timezone.now() - task.started_at
            task.time_spent_seconds += int(delta.total_seconds())
        
        task.is_active = False
        task.started_at = None
        task.save()
        return JsonResponse({
            'status': 'stopped', 
            'total_seconds': task.time_spent_seconds
        })
            
    return JsonResponse({'error': 'Invalid action'}, status=400)


def toggle_task(request, task_id):
    """
    Toggles completion state on an ExecutionItem.
    """
    task = get_object_or_404(ExecutionItem, id=task_id, is_deleted=False)
    task.is_completed = not task.is_completed
    
    # If completed, stop any running timers
    if task.is_completed and task.is_active:
        if task.started_at:
            delta = timezone.now() - task.started_at
            task.time_spent_seconds += int(delta.total_seconds())
        task.is_active = False
        task.started_at = None
        
    task.save()
    
    # Try to redirect to referrer, fallback to dashboard
    next_url = request.META.get('HTTP_REFERER', 'dashboard')
    if 'container/' in next_url:
        return redirect(next_url)
    return redirect('dashboard')