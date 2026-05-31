"""Utility functions for LifeOS."""

import re
from datetime import date, datetime


def fmt_mins(m: int) -> str:
    """Format minutes as human-readable string like '1h 30m' or '45m'."""
    if m is None or m == 0:
        return "0m"
    m = int(m)
    if m < 60:
        return f"{m}m"
    h, rem = divmod(m, 60)
    if rem:
        return f"{h}h {rem}m"
    return f"{h}h"


def parse_mins(s: str) -> int:
    """
    Parse a human-readable duration string into minutes.

    Supports:
    - "90"         → 90 minutes
    - "1h 30m"     → 90 minutes
    - "1h"         → 60 minutes
    - "30m"        → 30 minutes
    - "1.5h"       → 90 minutes
    - "1:30"       → 90 minutes
    """
    if not s or not str(s).strip():
        return 0

    s = str(s).strip().lower()

    # Pure integer
    if re.match(r"^\d+$", s):
        return int(s)

    # HH:MM format
    colon_match = re.match(r"^(\d+):(\d{2})$", s)
    if colon_match:
        return int(colon_match.group(1)) * 60 + int(colon_match.group(2))

    # Combined h/m format: "1h 30m", "1h30m", "1h", "30m"
    hours = 0
    minutes = 0

    h_match = re.search(r"([\d.]+)\s*h", s)
    m_match = re.search(r"(\d+)\s*m", s)

    if h_match:
        hours = float(h_match.group(1))
    if m_match:
        minutes = int(m_match.group(1))

    total = int(hours * 60) + minutes
    if total > 0:
        return total

    return 0


def today_str() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return date.today().isoformat()


def now_str() -> str:
    """Return current datetime as ISO string."""
    return datetime.now().isoformat()


def quarter_start() -> str:
    """Return the start of the current quarter as YYYY-MM-DD."""
    today = date.today()
    quarter = (today.month - 1) // 3
    start_month = quarter * 3 + 1
    return date(today.year, start_month, 1).isoformat()


def quarter_end() -> str:
    """Return the end of the current quarter as YYYY-MM-DD."""
    today = date.today()
    quarter = (today.month - 1) // 3
    end_month = quarter * 3 + 3
    # Last day of end_month
    if end_month == 12:
        end_date = date(today.year, 12, 31)
    else:
        end_date = date(today.year, end_month + 1, 1).replace(day=1)
        from datetime import timedelta
        end_date = end_date - timedelta(days=1)
    return end_date.isoformat()


def model_to_dict(model) -> dict:
    """Convert an rx.Model instance to a plain dict."""
    if model is None:
        return {}
    d = {}
    for col in model.__table__.columns:
        d[col.name] = getattr(model, col.name)
    return d


def models_to_dicts(models) -> list:
    """Convert a list of rx.Model instances to a list of dicts."""
    return [model_to_dict(m) for m in models]
