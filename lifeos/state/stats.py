"""StatsState — analytics and time tracking computations."""

import reflex as rx
from sqlmodel import select

from lifeos.models import Epic, Project, Task, LearningTask, Module, Certification
from lifeos.state.base import AppState
from lifeos.utils import quarter_start, quarter_end, fmt_mins, today_str


class StatsState(AppState):
    """State for the Stats/Analytics page."""

    start_date: str = ""
    end_date: str = ""

    # Summary KPIs
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    completion_rate: float = 0.0
    total_estimated_minutes: int = 0
    total_actual_minutes: int = 0

    # Distribution data (list of dicts for charts)
    status_distribution: list[dict] = []
    priority_distribution: list[dict] = []
    domain_time: list[dict] = []
    epic_time: list[dict] = []
    overdue_items: list[dict] = []

    # Learning stats
    modules_completed: int = 0
    total_modules: int = 0
    learning_hours: float = 0.0
    cert_progress: list[dict] = []

    @rx.event
    async def load_stats(self):
        """Compute all stats from the database."""
        if not self.start_date:
            self.start_date = quarter_start()
        if not self.end_date:
            self.end_date = quarter_end()

        today = today_str()
        start = self.start_date
        end = self.end_date

        with rx.session() as session:
            all_tasks = session.exec(select(Task)).all()
            all_epics = session.exec(select(Epic)).all()
            all_modules = session.exec(select(Module)).all()
            all_ltasks = session.exec(select(LearningTask)).all()
            all_certs = session.exec(select(Certification)).all()

        # Filter tasks within date range by due_date or all if no due date set
        def in_range(t):
            if not t.due_date:
                return True  # include undated tasks in stats
            return start <= t.due_date <= end

        filtered = [t for t in all_tasks if in_range(t)]
        completed = [t for t in filtered if t.status == "Completed"]
        in_progress = [t for t in filtered if t.status == "In Progress"]
        overdue = [
            t for t in all_tasks
            if t.due_date and t.due_date < today and t.status not in ("Completed", "Cancelled")
        ]

        self.total_tasks = len(filtered)
        self.completed_tasks = len(completed)
        self.in_progress_tasks = len(in_progress)
        self.overdue_tasks = len(overdue)
        self.completion_rate = (
            round(len(completed) / len(filtered) * 100, 1) if filtered else 0.0
        )
        self.total_estimated_minutes = sum(t.estimated_minutes for t in filtered)
        self.total_actual_minutes = sum(t.actual_minutes for t in filtered)

        # Status distribution
        status_counts: dict[str, int] = {}
        for t in filtered:
            status_counts[t.status] = status_counts.get(t.status, 0) + 1
        self.status_distribution = [
            {"status": k, "count": v} for k, v in status_counts.items()
        ]

        # Priority distribution
        priority_counts: dict[int, int] = {}
        for t in filtered:
            priority_counts[t.priority] = priority_counts.get(t.priority, 0) + 1
        priority_labels = {1: "Low", 2: "Normal", 3: "High", 4: "Critical"}
        self.priority_distribution = [
            {"priority": priority_labels.get(k, str(k)), "count": v}
            for k, v in sorted(priority_counts.items())
        ]

        # Domain time (actual minutes by domain)
        domain_time: dict[str, int] = {}
        for t in filtered:
            domain = t.domain or "Uncategorized"
            domain_time[domain] = domain_time.get(domain, 0) + t.actual_minutes
        self.domain_time = [
            {"domain": k, "minutes": v, "hours": round(v / 60, 1)}
            for k, v in sorted(domain_time.items(), key=lambda x: -x[1])
        ]

        # Epic time comparison
        epic_time = []
        for epic in all_epics:
            epic_tasks = [t for t in all_tasks if t.project_id is not None]
            # Get project IDs under this epic
            epic_project_ids = {
                p.id for p in session.exec(
                    select(Project).where(Project.epic_id == epic.id)
                ).all()
            } if False else set()  # We'll compute differently below
            est = epic.estimated_minutes
            act = epic.actual_minutes
            epic_time.append({
                "epic": epic.title,
                "estimated": est,
                "actual": act,
                "estimated_h": round(est / 60, 1),
                "actual_h": round(act / 60, 1),
            })
        self.epic_time = epic_time

        # Overdue items
        self.overdue_items = [
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date,
                "status": t.status,
                "priority": t.priority,
                "domain": t.domain,
            }
            for t in sorted(overdue, key=lambda x: x.due_date or "")
        ]

        # Learning stats
        completed_modules = [m for m in all_modules if m.status == "Completed"]
        self.modules_completed = len(completed_modules)
        self.total_modules = len(all_modules)
        total_learning_mins = sum(lt.actual_minutes for lt in all_ltasks)
        self.learning_hours = round(total_learning_mins / 60, 1)

        # Cert progress
        self.cert_progress = [
            {
                "id": c.id,
                "title": c.title,
                "issuer": c.issuer,
                "status": c.status,
                "pdus_required": c.pdus_required,
                "pdus_completed": c.pdus_completed,
                "seus_required": c.seus_required,
                "seus_completed": c.seus_completed,
                "next_renewal_date": c.next_renewal_date,
                "pdu_pct": (
                    round(c.pdus_completed / c.pdus_required * 100)
                    if c.pdus_required > 0 else 0
                ),
                "seu_pct": (
                    round(c.seus_completed / c.seus_required * 100)
                    if c.seus_required > 0 else 0
                ),
            }
            for c in all_certs
        ]

    @rx.event
    async def set_date_range(self, start: str, end: str):
        """Update the date range and reload stats."""
        self.start_date = start
        self.end_date = end
        yield StatsState.load_stats

    @rx.event
    async def set_start_date(self, value: str):
        self.start_date = value

    @rx.event
    async def set_end_date(self, value: str):
        self.end_date = value
        yield StatsState.load_stats
