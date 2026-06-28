# ==============================================================================
# File: f:/Code Repo/LifeOS_Django/lifeos_app/management/commands/seed_db.py
# Description: Django management command to seed the database with rich test data
# Component: Core / Database Seeding
# Version: 1.0 (Gold Master)
# Created: 2026-06-27
# Last Update: 2026-06-27
# ==============================================================================
import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from lifeos_app.models import (
    WorkspaceContainer, ExecutionItem, Tag, DomainCategory, 
    TimeAvailabilityBlock, RecurringConfig
)

class Command(BaseCommand):
    help = 'Seeds the database with rich mock data for testing hierarchy, focus, scheduling, and tagging.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Clearing existing LifeOS app data..."))
        
        # Wipe data to ensure a clean run (keeping users intact)
        RecurringConfig.objects.all().delete()
        TimeAvailabilityBlock.objects.all().delete()
        ExecutionItem.objects.all().delete()
        WorkspaceContainer.objects.all().delete()
        DomainCategory.objects.all().delete()
        Tag.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS("Wipe complete. Creating new seed data..."))
        
        # 1. Create Tags
        tag_work = Tag.objects.create(name="Work", color="#9966CC")
        tag_academy = Tag.objects.create(name="Academy", color="#50C878")
        tag_personal = Tag.objects.create(name="Personal", color="#0F52BA")
        tag_energy = Tag.objects.create(name="High Energy", color="#FF4500")
        tag_quick = Tag.objects.create(name="Quick Win", color="#FFD700")
        
        # 2. Create Domains
        dom_tech = DomainCategory.objects.create(name="Tech/Career", color="#9966CC", icon="terminal")
        dom_academy = DomainCategory.objects.create(name="Academy", color="#50C878", icon="academic-cap", is_academy=True)
        dom_home = DomainCategory.objects.create(name="Home", color="#0F52BA", icon="home")
        
        # 3. Create Hierarchical Containers
        # Epic -> Project -> Module
        epic_sys = WorkspaceContainer.objects.create(
            title="Mastering Distributed Systems",
            container_type="Epic",
            domain=dom_tech,
            domain_category="Tech/Career",
            para_category="Areas",
            priority="Critical",
            urgency="Normal"
        )
        
        proj_kv = WorkspaceContainer.objects.create(
            title="Build Sharded Key-Value Store",
            container_type="Project",
            parent=epic_sys,
            domain=dom_tech,
            domain_category="Tech/Career",
            para_category="Projects",
            priority="High",
            urgency="High"
        )
        
        mod_consensus = WorkspaceContainer.objects.create(
            title="Raft Consensus Engine Protocol",
            container_type="Module",
            parent=proj_kv,
            domain=dom_tech,
            domain_category="Tech/Career",
            para_category="Projects",
            priority="High",
            urgency="Immediate"
        )
        
        # Course -> Module (Academy)
        course_ml = WorkspaceContainer.objects.create(
            title="Advanced Machine Learning",
            container_type="Course",
            parent=None,
            domain=dom_academy,
            domain_category="Academy",
            para_category="Areas",
            priority="Medium",
            urgency="Normal"
        )
        
        mod_backprop = WorkspaceContainer.objects.create(
            title="Backpropagation & Neural Architectures",
            container_type="Module",
            parent=course_ml,
            domain=dom_academy,
            domain_category="Academy",
            para_category="Areas",
            priority="High",
            urgency="High"
        )
        
        # Standalone Project
        proj_renov = WorkspaceContainer.objects.create(
            title="House Kitchen Renovation",
            container_type="Project",
            domain=dom_home,
            domain_category="Home",
            para_category="Projects",
            priority="Low",
            urgency="Low"
        )
        
        # Orphaned container for Triage testing
        WorkspaceContainer.objects.create(
            title="Inbox Brain Dumped Container Idea",
            container_type="Project",
            priority="Medium",
            urgency="Normal"
        )
        
        # 4. Create Execution Items
        # Task 1 (High priority, scheduled today)
        today = timezone.now()
        task_api = ExecutionItem.objects.create(
            title="Design Consensus REST Protocol Specs",
            item_type="Task",
            status="Planned",
            priority="High",
            urgency="High",
            duration_estimate=120,
            start_date=today.replace(hour=9, minute=0, second=0),
            due_date=today.replace(hour=17, minute=0, second=0),
            content_type=ContentType.objects.get_for_model(WorkspaceContainer),
            object_id=mod_consensus.id
        )
        task_api.tags.add(tag_work, tag_energy)
        
        # Subtask 1.1 under Task 1
        subtask_draft = ExecutionItem.objects.create(
            title="Draft endpoint JSON request schemas",
            item_type="Task",
            status="In Progress",
            priority="Medium",
            urgency="Normal",
            duration_estimate=45,
            content_type=ContentType.objects.get_for_model(ExecutionItem),
            object_id=task_api.id
        )
        subtask_draft.tags.add(tag_work, tag_quick)
        
        # LearningTask (Academy, due tomorrow)
        tomorrow = today + datetime.timedelta(days=1)
        lt_read = ExecutionItem.objects.create(
            title="Read Chapter 4: Multi-Layer Perceptrons",
            item_type="LearningTask",
            status="Planned",
            priority="Medium",
            urgency="High",
            duration_estimate=60,
            start_date=tomorrow.replace(hour=10, minute=0, second=0),
            due_date=tomorrow.replace(hour=12, minute=0, second=0),
            content_type=ContentType.objects.get_for_model(WorkspaceContainer),
            object_id=mod_backprop.id
        )
        lt_read.tags.add(tag_academy)
        
        # Task (Home, in Backlog)
        ExecutionItem.objects.create(
            title="Install LED cabinet light strip strips",
            item_type="Task",
            status="Backlog",
            priority="Low",
            urgency="Low",
            duration_estimate=180,
            content_type=ContentType.objects.get_for_model(WorkspaceContainer),
            object_id=proj_renov.id
        ).tags.add(tag_personal)
        
        # Standalone LifeActivity
        la_run = ExecutionItem.objects.create(
            title="Evening Cardio Runs",
            item_type="LifeActivity",
            status="Planned",
            priority="Medium",
            urgency="Normal",
            duration_estimate=40,
            start_date=today.replace(hour=18, minute=0, second=0),
            due_date=today.replace(hour=19, minute=0, second=0)
        )
        la_run.tags.add(tag_personal, tag_quick)
        
        # Orphaned task in Inbox (Triage test target)
        ExecutionItem.objects.create(
            title="Clean code refactoring checklist task",
            item_type="Task",
            status="Inbox",
            priority="Medium",
            urgency="Normal",
            duration_estimate=30
        )
        
        # 5. Create Recurring Tasks
        # Weekly
        task_weekly = ExecutionItem.objects.create(
            title="Submit Weekly Progress Report",
            item_type="Task",
            status="Planned",
            priority="Low",
            urgency="Normal",
            duration_estimate=30
        )
        task_weekly.tags.add(tag_work)
        RecurringConfig.objects.create(
            execution_item=task_weekly,
            frequency="Weekly"
        )
        
        # Daily
        task_daily = ExecutionItem.objects.create(
            title="15-Minute Mindful Meditation",
            item_type="LifeActivity",
            status="Planned",
            priority="Medium",
            urgency="Normal",
            duration_estimate=15
        )
        task_daily.tags.add(tag_personal, tag_quick)
        RecurringConfig.objects.create(
            execution_item=task_daily,
            frequency="Daily"
        )
        
        # 6. Create Time Availability Blocks
        TimeAvailabilityBlock.objects.create(
            name="Core Work Hours",
            domain=dom_tech,
            day_monday=True, day_tuesday=True, day_wednesday=True, day_thursday=True, day_friday=True,
            day_saturday=False, day_sunday=False,
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 0)
        )
        
        TimeAvailabilityBlock.objects.create(
            name="Academy Study Time",
            domain=dom_academy,
            day_monday=True, day_tuesday=True, day_wednesday=True, day_thursday=True, day_friday=True,
            day_saturday=False, day_sunday=False,
            start_time=datetime.time(18, 0),
            end_time=datetime.time(21, 0)
        )
        
        self.stdout.write(self.style.SUCCESS("LifeOS Database successfully seeded! Ready for testing."))
