import re

def parse_human_time(time_str: str) -> int:
    """Converts strings like '2w 3d 4h 15m' into total integer minutes."""
    if not time_str:
        return 0
    minutes = 0
    matches = re.findall(r'(\d+)\s*([wdhm])', time_str.lower())
    for amount, unit in matches:
        val = int(amount)
        if unit == 'w': minutes += val * 10080  # 7 days * 24 hrs * 60 mins
        elif unit == 'd': minutes += val * 1440 # 24 hrs * 60 mins
        elif unit == 'h': minutes += val * 60
        elif unit == 'm': minutes += val
    return minutes

def format_human_time(total_minutes: int) -> str:
    """Converts total integer minutes back into readable '1h 30m' format."""
    if not total_minutes or total_minutes == 0:
        return ""
    w = total_minutes // 10080
    rem = total_minutes % 10080
    d = rem // 1440
    rem %= 1440
    h = rem // 60
    m = rem % 60
    
    parts = []
    if w > 0: parts.append(f"{w}w")
    if d > 0: parts.append(f"{d}d")
    if h > 0: parts.append(f"{h}h")
    if m > 0: parts.append(f"{m}m")
    return " ".join(parts)
