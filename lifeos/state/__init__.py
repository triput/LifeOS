"""State package for LifeOS."""
from .base_state import AppState
from .work_state import WorkState
from .academy_state import AcademyState
from .agenda_state import AgendaState
from .stats_state import StatsState

__all__ = ["AppState", "WorkState", "AcademyState", "AgendaState", "StatsState"]
