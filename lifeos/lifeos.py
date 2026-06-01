"""LifeOS app entry point — registers all pages and global styles."""

import reflex as rx

# Import all pages (they register themselves via @rx.page decorator)
from lifeos.pages.dashboard_page import dashboard_page
from lifeos.pages.work_page import work_page
from lifeos.pages.academy_page import academy_page
from lifeos.pages.agenda_page import agenda_page
from lifeos.pages.stats_page import stats_page
from lifeos.pages.settings_page import settings_page

# Create the app with dark theme and custom stylesheet
app = rx.App(
    stylesheets=["lifeos.css"],
    style={
        "background_color": "#0f1117",
        "color": "#e2e8f0",
        "font_family": "'Satoshi', 'Inter', system-ui, sans-serif",
    },
)

