<!--
# ==============================================================================
# File: USER_GUIDE.md
# Description: User guide explaining application startup, authentication, structure, and focus features
# Component: Documentation
# Version: 1.0 (Gold Master)
# Created: 2026-06-26
# Last Update: 2026-06-26
# ==============================================================================
-->
# LifeOS Django: User Guide

Welcome to **LifeOS Django**—a stability-first personal operating system built around a unified DRY data model. This guide outlines how to manage, navigate, and utilize the core modules of the system.

---

## 1. Starting the Application
Since LifeOS Django is designed as a single-user local system, you run the service from your local workstation using the standard Django development server.

### Steps to Run
1. Open a terminal (PowerShell or Command Prompt) and navigate to the project directory:
   ```powershell
   cd "path/to/LifeOS_Django"
   ```
2. Activate the python virtual environment:
   ```powershell
   .venv\Scripts\activate
   ```
3. Boot up the server:
   ```powershell
   python manage.py runserver
   ```
   *By default, the server will bind to port `8000` on localhost.*
4. Open your web browser and navigate to:
   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 2. Authentication & Security
Access to the LifeOS Django interface is strictly limited to the system owner.

### Logging In
1. Navigate to the application URL (by default, `http://localhost:8000/login/` or `http://127.0.0.1:8000/login/`).
2. Input the owner credentials you created during system setup (superuser account).
3. If an unauthorized user attempts to access any page on the system, they will be blocked and redirected back to the login page.

---

## 3. Managing Scopes (WorkspaceContainers)
**WorkspaceContainers** represent the structural nesting of your life domains and study materials. They can be created and managed via the Django Admin interface.

### Types of Containers
*   **Epic**: Broad life domains or career milestones (e.g., "Career Development").
*   **Project**: Structured end-goals nested under Epics (e.g., "Implement LifeOS V1").
*   **Specialization**: Major academic areas (e.g., "Computer Science").
*   **Course**: Specific courses nested under Specializations (e.g., "Advanced Algorithms").
*   **Module**: Discrete learning modules nested under Courses (e.g., "Graph Theory").

### Creating a Hierarchy in Django Admin
1. Navigate to `http://localhost:8000/admin/` and click on **Workspace Containers**.
2. Click **Add Workspace Container**.
3. Fill in the fields:
    *   **Title**: The name of the container.
    *   **Container Type**: Select the role (Epic, Project, Course, etc.).
    *   **Parent**: Select a parent container to establish nesting (e.g., set `Tech Career` as the parent of `LifeOS Development` to establish an Epic-to-Project link).
    *   **Domain Category**: Group the container (Tech/Career, Theater, Academy, Home, Governance/Compliance).
    *   **PARA Category**: Group the container (Projects, Areas, Resources, Archives).
4. Click **Save**.

*Note: The system automatically prevents circular nesting (e.g., setting a container as a child of itself or creating circular parent loops).*

---

## 4. Managing Actionable Backlogs (ExecutionItems)
**ExecutionItems** represent the actual tasks, subtasks, assignments, and activities you execute.

### Types of ExecutionItems
*   **Task**: Standalone work item (e.g., "Write views tests").
*   **Subtask**: Component of a larger Task.
*   **LearningTask**: Homework, coding challenge, or reading assignment (e.g., "Read Chapter 4").
*   **LifeActivity**: Fitness, domestic work, or general habits.

### Linking ExecutionItems to Containers
Because the backend uses a unified `GenericForeignKey` design, any ExecutionItem can be linked to any WorkspaceContainer or parent ExecutionItem:
1. In the Django Admin panel, go to **Execution Items** -> **Add Execution Item**.
2. Set the **Item Type** (Task, LearningTask, etc.).
3. Choose the **Content Type** (e.g., `WorkspaceContainer` to link it to a container, or `ExecutionItem` to link it to a parent task).
4. Set the **Object ID** to the ID of the target container/item.
5. Set `domain_category` and `para_category` markers.

---

## 5. Scoped Workspace Views
To help you reduce cross-context noise, you can open focused backlog views for individual containers.

1. Navigate to `/container/<container_id>/` (e.g., `http://localhost:8000/container/1/`).
2. You will see:
    *   **Breadcrumbs**: A path showing the container parent hierarchy.
    *   **Sub-Workspaces**: Grid navigation boxes linking to child containers.
    *   **Scoped Active Backlog**: Task widgets for tasks explicitly assigned to this workspace scope. 
3. Completed, archived, and soft-deleted tasks are hidden from this backlog by default to keep the interface clean.

---

## 6. Consolidated Focus Engine
The Focus Engine handles real-time timer tracking for all of your execution tasks.

### Starting a Focus Session
1. Go to the **Mission Control Dashboard** (Root `/` or `/dashboard/`) or any **Scoped Workspace**.
2. Locate the Task widget you want to work on.
3. Click the green **Start** button. 
4. The digital clock display will begin ticking in real-time, displaying elapsed hours, minutes, and seconds.

### Enforcing Single-Active Timer
The system operates under a strict **Single-Active-Timer** rule to prevent timing leakage. If you click **Start** on Task B while Task A is actively running:
1. The backend automatically pauses the timer on Task A.
2. The elapsed time on Task A is calculated and added to its `time_spent_seconds` in the database.
3. Task B's timer is started.

### Stopping/Pausing a Session
1. Click the red **Stop** button on an active widget.
2. The page will refresh, the timer will stop ticking, and your total time spent on that task will accumulate and show updated numbers across the dashboard HUD statistics.

---

## 7. Interpreting the Unified Domain Context HUD
At the top of the Mission Control Dashboard, the Heads-Up Display (HUD) aggregates environment data and progress vectors:

### Environmental HUD
*   **Local Atmosphere**: Displays the current temperature, sunrise, and sunset times fetched from the Open-Meteo API.
*   **Geomagnetic Kp Index**: Displays the latest planetary space weather Kp index from the NOAA SWPC. 
    *   `Kp < 4.0`: Green **Quiet** badge.
    *   `Kp 4.0 - 4.9`: Yellow **Unsettled** badge.
    *   `Kp >= 5.0`: Red **Storm Active** badge.
*   *Note: If the system loses internet connectivity, these indicators will display a clean "N/A" offline fallback without breaking the page.*

### Progress & Allocation HUDs
*   **Domain Velocity**: Displays completion bars grouped by life domain category (e.g., Tech/Career, Academy, Home). It shows the completed task ratio and the sum of total focus time spent in seconds.
*   **PARA Allocation**: Displays allocation metrics showing active projects, areas, and resource lists grouped by PARA structure rules.

---

## 8. Archival & Deletion Workflows
To keep database tables healthy over months and years of use, the app supports clean data lifecycle states.

### Soft Deletion (`is_deleted`)
When you delete an `ExecutionItem`, set its `is_deleted` field to `true` in the Admin panel.
*   It is hidden from all backlogs and active dashboards.
*   Historical tracking stats and cumulative seconds spent are preserved in the DB.

### PARA Archiving (`is_archived`)
When a container (like a completed Project or Course) is archived:
*   Set `is_archived` to `true` on the `WorkspaceContainer` record.
*   The container and its child sub-workspaces are filtered out of active lists, but they remain safely retrievable in the Admin panel.
