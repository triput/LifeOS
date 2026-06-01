import os
import reflex as rx

# config = rx.Config(
#     app_name="lifeos",
#     #db_url=os.environ.get("DATABASE_URL", "sqlite:///lifeos.db"),
#)
config = rx.Config(
    app_name="lifeos",
    theme=rx.theme(
        appearance="dark",
        accent_color="teal",
        gray_color="slate",
        radius="medium",
        scaling="100%",
    ),
    # db_url="postgresql://triput_admin:w33bl3sLOWobble!@localhost:5432/lifeos_habitat",
    db_url="postgresql://neondb_owner:npg_ySMNJu1Hkp6e@ep-curly-forest-akl1t0gt-pooler.c-3.us-west-2.aws.neon.tech/lifeos?sslmode=require&channel_binding=require",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin()
    ]
)