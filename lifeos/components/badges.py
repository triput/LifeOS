"""Status and priority badge components."""

import reflex as rx


def status_badge(status: str) -> rx.Component:
    """Color-coded badge for task/item status."""
    return rx.badge(
        status,
        color_scheme=rx.match(
            status,
            ("In Progress", "teal"),
            ("Completed", "green"),
            ("Blocked", "red"),
            ("On Hold", "orange"),
            ("Cancelled", "gray"),
            ("Planned", "blue"),
            ("Active", "teal"),
            ("Expired", "red"),
            "gray",
        ),
        variant="soft",
        size="1",
    )


def priority_badge(priority) -> rx.Component:
    """Color-coded badge for task priority (1-4)."""
    priority_str = priority.to_string() if hasattr(priority, "to_string") else str(priority)
    label = rx.match(
        priority,
        (1, "Low"),
        (2, "Normal"),
        (3, "High"),
        (4, "Critical"),
        "Unknown",
    )
    color = rx.match(
        priority,
        (1, "gray"),
        (2, "blue"),
        (3, "amber"),
        (4, "red"),
        "gray",
    )
    return rx.badge(
        label,
        color_scheme=color,
        variant="soft",
        size="1",
    )


def activity_type_badge(activity_type: str) -> rx.Component:
    """Badge for learning task activity type."""
    return rx.badge(
        activity_type,
        color_scheme=rx.match(
            activity_type,
            ("Video", "blue"),
            ("Quiz", "purple"),
            ("Reading", "cyan"),
            ("Exercise", "green"),
            ("Project", "orange"),
            "gray",
        ),
        variant="soft",
        size="1",
    )
