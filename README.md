<!--
# ==============================================================================
# File: README.md
# Description: Primary documentation and bootstrap instructions for the LifeOS Django repository
# Component: Documentation
# Version: 1.0 (Gold Master)
# Created: 2026-06-26
# Last Update: 2026-06-26
# ==============================================================================
-->
# LifeOS Django

LifeOS Django is a stability-first, single-owner personal operating system designed to run locally. Built around a unified DRY data model, it consolidates work management (Epics, Projects, Tasks) and academic learning trackers (Specializations, Courses, Modules, LearningTasks) into a cohesive relational structure. 

The application utilizes server-rendered Django templates, HTMX for partial-page reactivity, and is backed by PostgreSQL (development/production) and SQLite (testing).

---

## Key Features

*   **Unified DRY Data Model**: Avoids separate databases/model trees for work and study by implementing type-discriminated `WorkspaceContainer` and actionable `ExecutionItem` records.
*   **Consolidated Focus Engine**: Universal timing controls allowing active focus tracking over tasks. Enforces a single-active-timer constraint to prevent tracking overlap.
*   **Unified Domain Context HUD**: Real-time dashboard panel displaying:
    *   *Atmospheric Telemetry*: Temperature, sunrise, and sunset times via Open-Meteo.
    *   *Space Weather Telemetry*: Geomagnetic Kp Index levels via NOAA SWPC.
    *   *Progress Aggregates*: Allocation statistics and completion velocities grouped by Domain and PARA classifications.
*   **Layered Security**: Enforces strong `Argon2` password hashing and a strict single-owner access policy via middleware that blocks and redirects unauthenticated or non-owner requests.
*   **Isolated Testing Engine**: Built-in test suite automatically executes database checks inside local memory using SQLite, avoiding locking issues on cloud instances during test runs.

---

## Directory Index

*   [USER_GUIDE.md](USER_GUIDE.md) - Operations guide detailing server startup, data structures, and focus sessions.
*   [LifeOS-SRS.md](docs/LifeOS-SRS.md) - Version 1.0 Software Requirements Specification.
*   [LifeOS-SRS-v2.md](docs/LifeOS-SRS-v2.md) - Version 2.0 Specifications (Inbox, Quick Entry, Workspace Explorer, Analytics Charts).
*   [validate_sandbox.py](validate_sandbox.py) - Environment verification script check.

---

## Quick Start

### 1. Prerequisite Verification
Run the verification utility to verify that your system runtimes (`python3`, `git`, `pip3`) are configured correctly:
```powershell
python validate_sandbox.py
```

### 2. Dependency Installation
Create and activate your Python virtual environment, then install requirements:
```powershell
# Activate venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Migrations
Generate and apply database migrations to setup the schema:
```powershell
python manage.py makemigrations lifeos_app
python manage.py migrate
```

### 4. Create Owner Superuser
Configure your secure owner credentials:
```powershell
python manage.py createsuperuser
```

### 5. Running the Application
Boot up the local development server:
```powershell
python manage.py runserver
```
Navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Running the Automated Test Suite

Validate system components, authentication middleware, and timing models:
```powershell
python manage.py test lifeos_app
```
