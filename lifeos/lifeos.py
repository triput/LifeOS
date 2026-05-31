"""LifeOS app entry point — registers all pages and global styles."""

import reflex as rx

# Import all pages (they register themselves via @rx.page decorator)
from lifeos.pages.dashboard import dashboard_page
from lifeos.pages.work import work_page
from lifeos.pages.academy import academy_page
from lifeos.pages.agenda import agenda_page
from lifeos.pages.stats import stats_page
from lifeos.pages.settings import settings_page

# Create the app with dark theme and custom stylesheet
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="teal",
        gray_color="slate",
        radius="medium",
        scaling="100%",
    ),
    stylesheets=["lifeos.css"],
    style={
        "background_color": "#0f1117",
        "color": "#e2e8f0",
        "font_family": "'Satoshi', 'Inter', system-ui, sans-serif",
    },
)
