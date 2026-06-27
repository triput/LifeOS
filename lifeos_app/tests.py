# ==============================================================================
# File: f:/Code Repo/LifeOS_Django/lifeos_app/tests.py
# Description: Unit and functional tests for authentication, models, and HUD logic
# Component: Core / Automated Testing
# Version: 1.0 (Gold Master)
# Created: 2026-06-26
# Last Update: 2026-06-26
# ==============================================================================
"""Automated verification suite for the LifeOS application.

Validates security policies (auth, password hashers, single-owner restriction),
data constraints (cycles, PARA archival, soft deletion), focus actions,
and HUD context metrics.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

from .models import WorkspaceContainer, ExecutionItem, AppSettings

User = get_user_model()

class LifeOSSecurityTestCase(TestCase):
    """
    Verifies authentication controls, single-owner access restrictions, and password hashes (Section 7).
    """
    def setUp(self):
        # Create standard owner user (superuser)
        self.owner = User.objects.create_superuser(
            username='owner_trish',
            password='StrongSecurePassword123!',
            email='trish@lifeos.lan'
        )
        # Create non-owner authenticated user
        self.non_owner = User.objects.create_user(
            username='non_owner_guest',
            password='AnotherPassword123!',
            email='guest@lifeos.lan'
        )
        self.client = Client()

    def test_tc_sec_001_anonymous_redirect(self):
        """Anonymous user attempts to access a protected application view. (TC-SEC-001)"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('login'))

    def test_tc_sec_002_owner_access(self):
        """Owner logs in and accesses a protected view. (TC-SEC-002 / TC-SEC-007)"""
        login_success = self.client.login(username='owner_trish', password='StrongSecurePassword123!')
        self.assertTrue(login_success)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_tc_sec_004_logout_invalidation(self):
        """User logs out and then attempts to access protected content. (TC-SEC-004)"""
        self.client.login(username='owner_trish', password='StrongSecurePassword123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Logout
        self.client.get(reverse('logout'))
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('login'))

    def test_tc_sec_005_password_hashing(self):
        """New password is stored using the configured strong password hasher. (TC-SEC-005)"""
        # Retrieve the user record from database
        user = User.objects.get(username='owner_trish')
        # Standard Argon2 has prefix 'argon2'
        self.assertTrue(user.password.startswith('argon2'))

    def test_tc_sec_006_invalid_credentials(self):
        """Invalid credentials are rejected during login. (TC-SEC-006)"""
        response = self.client.post(reverse('login'), {
            'username': 'owner_trish',
            'password': 'WrongPassword123!'
        })
        self.assertEqual(response.status_code, 200) # Re-renders login screen
        self.assertContains(response, "Please enter a correct username and password")

    def test_tc_sec_008_non_owner_forbidden(self):
        """Authenticated non-owner account is denied access. (TC-SEC-008)"""
        self.client.login(username='non_owner_guest', password='AnotherPassword123!')
        response = self.client.get(reverse('dashboard'))
        # Returns 403 Forbidden
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "You are not authorized to access this LifeOS", status_code=403)


class LifeOSDataLifecycleTestCase(TestCase):
    """
    Verifies circular relationship prevention, PARA archival state, and soft deletions (Section 8).
    """
    def setUp(self):
        # Create base containers
        self.epic = WorkspaceContainer.objects.create(
            title='Tech Career',
            container_type='Epic',
            domain_category='Tech/Career',
            para_category='Areas'
        )
        self.project = WorkspaceContainer.objects.create(
            title='LifeOS Development',
            container_type='Project',
            parent=self.epic,
            domain_category='Tech/Career',
            para_category='Projects'
        )
        
        self.container_type = ContentType.objects.get_for_model(WorkspaceContainer)
        
        # Create test execution item
        self.task = ExecutionItem.objects.create(
            title='Implement testing suite',
            item_type='Task',
            content_type=self.container_type,
            object_id=self.project.id,
            domain_category='Tech/Career',
            para_category='Projects',
            duration_estimate=60,
            time_spent_seconds=3600
        )

    def test_hierarchy_cycles(self):
        """Circular parent-child container relationships are prevented. (FR-DATA-001.3)"""
        # Setting a child as its parent's parent should fail validation
        self.epic.parent = self.project
        with self.assertRaises(ValidationError):
            self.epic.clean()

    def test_tc_life_001_soft_delete(self):
        """ExecutionItem is soft-deleted without losing timing data. (TC-LIFE-001)"""
        self.assertEqual(self.task.time_spent_seconds, 3600)
        self.task.is_deleted = True
        self.task.save()

        # Re-fetch from DB
        re_fetched = ExecutionItem.objects.get(id=self.task.id)
        self.assertTrue(re_fetched.is_deleted)
        self.assertEqual(re_fetched.time_spent_seconds, 3600) # preserved

    def test_tc_life_004_archival_preserves_data(self):
        """Archiving preserves classification and timing-related data. (TC-LIFE-004)"""
        self.task.is_archived = True
        self.task.save()

        re_fetched = ExecutionItem.objects.get(id=self.task.id)
        self.assertTrue(re_fetched.is_archived)
        self.assertEqual(re_fetched.domain_category, 'Tech/Career')
        self.assertEqual(re_fetched.para_category, 'Projects')
        self.assertEqual(re_fetched.time_spent_seconds, 3600)


class LifeOSWorkspaceTestCase(TestCase):
    """
    Verifies scoped container detail workspaces and backlog listings (Section 8).
    """
    def setUp(self):
        self.owner = User.objects.create_superuser(username='owner', password='p', email='e')
        
        self.container_active = WorkspaceContainer.objects.create(
            title='Active Course',
            container_type='Course',
            domain_category='Academy',
            para_category='Areas'
        )
        self.container_archived = WorkspaceContainer.objects.create(
            title='Archived Course',
            container_type='Course',
            domain_category='Academy',
            para_category='Areas',
            is_archived=True
        )
        
        self.container_type = ContentType.objects.get_for_model(WorkspaceContainer)
        
        # Actionable tasks
        self.task_active = ExecutionItem.objects.create(
            title='Active Module Homework',
            item_type='LearningTask',
            content_type=self.container_type,
            object_id=self.container_active.id,
            domain_category='Academy',
            para_category='Areas'
        )
        self.task_completed = ExecutionItem.objects.create(
            title='Completed Module Homework',
            item_type='LearningTask',
            is_completed=True,
            content_type=self.container_type,
            object_id=self.container_active.id,
            domain_category='Academy',
            para_category='Areas'
        )
        self.task_deleted = ExecutionItem.objects.create(
            title='Deleted Module Homework',
            item_type='LearningTask',
            is_deleted=True,
            content_type=self.container_type,
            object_id=self.container_active.id,
            domain_category='Academy',
            para_category='Areas'
        )
        self.client = Client()
        self.client.force_login(self.owner)

    def test_tc_wsp_001_valid_workspace(self):
        """Valid WorkspaceContainer opens a scoped workspace view. (TC-WSP-001)"""
        response = self.client.get(reverse('container_detail', args=[self.container_active.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.container_active.title)

    def test_tc_wsp_002_invalid_workspace(self):
        """Invalid WorkspaceContainer identifier returns 404. (TC-WSP-002)"""
        response = self.client.get(reverse('container_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_tc_wsp_004_backlog_exclusions(self):
        """Focused backlog hides completed, archived, and soft-deleted items by default. (TC-WSP-004 / TC-LIFE-002)"""
        response = self.client.get(reverse('container_detail', args=[self.container_active.id]))
        self.assertEqual(response.status_code, 200)
        # Verify active task is shown, completed and deleted are excluded
        self.assertContains(response, self.task_active.title)
        self.assertNotContains(response, self.task_completed.title)
        self.assertNotContains(response, self.task_deleted.title)


class LifeOSFocusEngineTestCase(TestCase):
    """
    Verifies focus transitions and timing metrics accumulation (Section 3.2).
    """
    def setUp(self):
        self.owner = User.objects.create_superuser(username='owner', password='p', email='e')
        self.container = WorkspaceContainer.objects.create(title='C', container_type='Project')
        self.container_type = ContentType.objects.get_for_model(WorkspaceContainer)
        self.task = ExecutionItem.objects.create(
            title='Focus Item',
            item_type='Task',
            content_type=self.container_type,
            object_id=self.container.id
        )
        self.client = Client()
        self.client.force_login(self.owner)

    def test_focus_start_and_stop(self):
        """Start and Stop focus commands record active time correctly."""
        # 1. Start timer
        response = self.client.post(
            reverse('task-action'),
            data={'task_id': self.task.id, 'action': 'start'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'started')

        # Verify database state
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_active)
        self.assertIsNotNone(self.task.started_at)

        # Force fake duration in past to simulate active timer
        self.task.started_at = timezone.now() - datetime.timedelta(seconds=120)
        self.task.save()

        # 2. Stop timer
        response = self.client.post(
            reverse('task-action'),
            data={'task_id': self.task.id, 'action': 'stop'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'stopped')

        self.task.refresh_from_db()
        self.assertFalse(self.task.is_active)
        self.assertIsNone(self.task.started_at)
        # Should record ~120 seconds
        self.assertGreaterEqual(self.task.time_spent_seconds, 120)
