"""Pages package for LifeOS."""
from .dashboard import dashboard_page
from .work import work_page
from .academy import academy_page
from .agenda import agenda_page
from .stats import stats_page
from .settings import settings_page

__all__ = [
    "dashboard_page",
    "work_page",
    "academy_page",
    "agenda_page",
    "stats_page",
    "settings_page",
]
