import os
import reflex as rx

config = rx.Config(
    app_name="lifeos",
    db_url=os.environ.get("DATABASE_URL", "sqlite:///lifeos.db"),
)
