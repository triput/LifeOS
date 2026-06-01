"""HabitatState — Environment, Weather, and Celestial tracking for Monroe."""

import reflex as rx
import httpx
import os
import asyncio
from dotenv import load_dotenv
from sqlmodel import select
from lifeos.models import Settings
from lifeos.state.base_state import AppState # Assuming you want to inherit from your base state

class HabitatState(AppState):
    """State for environmental tracking in the user's habitat."""

    # --- The UI Variables (API Agnostic) ---
    habitat_name: str = "INITIALIZING OBSERVATORY..."
    current_temp: str = "--°F"
    weather_condition: str = "Scanning Atmosphere..."
    is_day: bool = True
    
    # Celestial
    sunrise: str = "--:--"
    sunset: str = "--:--"
    moon_phase: str = "Unknown"

    @rx.event(background=True)
    async def sync_environment(self):
        """Background task to fetch data without blocking the UI."""
        # 1. Grab the key from your .env file
        load_dotenv()
        api_key = os.environ.get("WEATHER_API_KEY", "")
        if not api_key:
            print("Habitat Error: WEATHER_API_KEY not found in .env")
            return

        # 2. Grab the location and name from the database
        with rx.session() as session:
            settings = session.exec(select(Settings)).first()
        location = settings.habitat_location if settings and settings.habitat_location else "Monroe, WA"
        db_name = settings.habitat_name if settings and settings.habitat_name else "Monroe Observatory"

        current_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
        astro_url = f"http://api.weatherapi.com/v1/astronomy.json?key={api_key}&q={location}"

        try:
            async with httpx.AsyncClient() as client:
                current_resp, astro_resp = await asyncio.gather(
                    client.get(current_url),
                    client.get(astro_url),
                )

                if current_resp.status_code == 200 and astro_resp.status_code == 200:
                    current_data = current_resp.json()
                    astro_data = astro_resp.json()

                    # 3. Safely update the state variables
                    async with self:
                        self.habitat_name = db_name.upper()
                        self.current_temp = f"{int(current_data['current']['temp_f'])}°F"
                        self.weather_condition = current_data['current']['condition']['text']
                        self.is_day = bool(current_data['current']['is_day'])

                        astro = astro_data['astronomy']['astro']
                        self.sunrise = astro['sunrise']
                        self.sunset = astro['sunset']
                        self.moon_phase = astro['moon_phase']
                else:
                    print(
                        f"API Error. Current: {current_resp.status_code}, "
                        f"Astro: {astro_resp.status_code}"
                    )
        except Exception as e:
            print(f"Habitat Sync Failed: {e}")