"""State package for LifeOS."""
from .base import AppState
from .work import WorkState
from .academy import AcademyState
from .agenda import AgendaState
from .stats import StatsState

__all__ = ["AppState", "WorkState", "AcademyState", "AgendaState", "StatsState"]
