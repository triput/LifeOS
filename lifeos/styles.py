"""Global styles, color tokens, and CSS variables for LifeOS."""

COLORS = {
    "bg": "#0f1117",            # near-black background
    "surface": "#161b27",       # card surface
    "surface2": "#1e2535",      # elevated surface
    "border": "#2a2f3d",        # subtle border
    "primary": "#2dd4bf",       # teal (In Progress)
    "primary_dim": "#1a7a70",   # dimmed teal
    "success": "#86efac",       # sage green (Completed)
    "success_dim": "#166534",   # dimmed sage
    "warning": "#fbbf24",       # amber (High priority)
    "warning_dim": "#92400e",   # dimmed amber
    "accent": "#fb7185",        # ruby (Critical/Blocked)
    "accent_dim": "#9f1239",    # dimmed ruby
    "muted": "#6b7280",         # muted text
    "text": "#e2e8f0",          # primary text
    "secondary_text": "#94a3b8", # secondary text
    "sidebar_bg": "#0d1120",    # sidebar background
    "sidebar_active": "#1e2a3a", # active sidebar item
}

SIDEBAR_WIDTH = "220px"
HEADER_HEIGHT = "60px"

# Status → color scheme mapping (for rx.badge color_scheme)
STATUS_COLOR = {
    "In Progress": "teal",
    "Completed": "green",
    "Blocked": "red",
    "On Hold": "orange",
    "Cancelled": "gray",
    "Planned": "blue",
    "Active": "teal",
    "Expired": "red",
}

# Priority → label mapping
PRIORITY_LABELS = {
    1: "Low",
    2: "Normal",
    3: "High",
    4: "Critical",
}

# Priority → color scheme mapping
PRIORITY_COLOR = {
    1: "gray",
    2: "blue",
    3: "amber",
    4: "red",
}

# Global font import (Fontshare CDN)
FONT_CSS = """
@import url('https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@800,700,500,400&f[]=satoshi@700,500,400&display=swap');

:root {
    --color-bg: #0f1117;
    --color-surface: #161b27;
    --color-surface2: #1e2535;
    --color-border: #2a2f3d;
    --color-primary: #2dd4bf;
    --color-success: #86efac;
    --color-warning: #fbbf24;
    --color-accent: #fb7185;
    --color-muted: #6b7280;
    --color-text: #e2e8f0;
    --color-secondary: #94a3b8;
    --sidebar-width: 220px;
}

* {
    box-sizing: border-box;
}

body {
    background-color: var(--color-bg) !important;
    color: var(--color-text) !important;
    font-family: 'Satoshi', 'Inter', system-ui, sans-serif !important;
    margin: 0;
    padding: 0;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Cabinet Grotesk', 'Inter', system-ui, sans-serif !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: var(--color-bg);
}
::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--color-muted);
}

/* Input/Select dark theme overrides */
input, textarea, select {
    background-color: var(--color-surface2) !important;
    color: var(--color-text) !important;
    border-color: var(--color-border) !important;
}

/* Radix UI dark overrides */
.rt-Card {
    background-color: var(--color-surface) !important;
    border-color: var(--color-border) !important;
}

/* Drawer dark override */
[data-vaul-drawer] {
    background-color: var(--color-surface) !important;
}
"""

# Base style dict for common elements
BASE_STYLE = {
    "background_color": COLORS["bg"],
    "color": COLORS["text"],
    "font_family": "'Satoshi', 'Inter', system-ui, sans-serif",
}

CARD_STYLE = {
    "background_color": COLORS["surface"],
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "8px",
    "padding": "16px",
}

SIDEBAR_STYLE = {
    "background_color": COLORS["sidebar_bg"],
    "border_right": f"1px solid {COLORS['border']}",
    "width": SIDEBAR_WIDTH,
    "min_height": "100vh",
    "padding": "16px 8px",
}
