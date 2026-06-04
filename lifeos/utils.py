# ==============================================================================
# File: lifeos/utils.py
# Description: Shared utility functions for time parsing and data formatting.
# Component: Shared Utilities
# Version: 1.0 (Gold Master)
# Created: 2026-03-24
# Last Update: 2026-06-01
# ==============================================================================

import re
from datetime import date, datetime



import re

def parse_time_to_minutes(time_str: str) -> int:
    """Converts strings like '1w 2d 4h 30m' to total minutes."""
    if not time_str: return 0
    total = 0
    pattern = r'(\d+)\s*(mo|w|d|h|m)'
    matches = re.findall(pattern, str(time_str).lower())
    
    for val, unit in matches:
        v = int(val)
        if unit == 'mo': total += v * 43200
        elif unit == 'w': total += v * 10080
        elif unit == 'd': total += v * 1440
        elif unit == 'h': total += v * 60
        elif unit == 'm': total += v
        
    # Fallback if they just typed a raw number
    if not matches and str(time_str).strip().isdigit():
        return int(str(time_str).strip())
        
    return total

def format_minutes_to_time(minutes: int) -> str:
    """Converts total minutes to '1w 2d 4h 30m' format."""
    if not minutes or int(minutes) == 0: return ""
    m = int(minutes)
    
    mo, rem = divmod(m, 43200)
    w, rem = divmod(rem, 10080)
    d, rem = divmod(rem, 1440)
    h, rem = divmod(rem, 60)
    
    parts = []
    if mo: parts.append(f"{mo}mo")
    if w: parts.append(f"{w}w")
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if rem: parts.append(f"{rem}m")
    
    return " ".join(parts)

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
