import aiohttp
import async_timeout
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN, STATE_MAPPING

API_URL = "https://api.raporty.pse.pl/api/pdgsz?$select=znacznik,udtczas&$filter=business_date eq '{date}'"

COLOR_MAPPING = {
    0: "#006600",  # Ciemno zielony
    1: "#ccff99",  # Jasno zielony
    2: "#ffcc00",  # Pomarańczowy
    3: "#FF0000"   # Czerwony
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor."""
    update_interval = entry.data.get("update_interval", 6)
    async_add_entities([EnergetycznyKompasSensor(update_interval, entry)])


class EnergetycznyKompasSensor(Entity):
    """Representation of the Energetyczny Kompas sensor."""

    def __init__(self, update_interval, entry):
        self._state = None
        self._attributes = {}
        self._update_interval = timedelta(hours=update_interval)
        self._last_update = None
        self._next_day_data = None  # Dane na następny dzień
        self._entry_id = entry.entry_id
        self._currently = None
        self._daily_max = None
        self._next_day_max = None
        self._next_day_min = None
        self._force_midnight_update = False  # Flaga wymuszenia aktualizacji o 00:01

    @property
    def name(self):
        return "Energetyczny Kompas PSE"

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"{DOMAIN}_{self._entry_id}"

    @property
    def device_info(self):
        """Return device info for the sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Energetyczny Kompas PSE",
            manufacturer="PSE",
            model="Energetyczny Kompas",
            entry_type="service",
        )

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        """Return attributes of the sensor."""
        return {
            "icon": "mdi:lightning-bolt",
            "friendly_name": "Compass PSE",
            "currently": self._currently,
            "daily_max": self._daily_max,
            "next_day_data": self._next_day_data,
            "next_day_max": self._next_day_max,
            "next_day_min": self._next_day_min,
            "color": COLOR_MAPPING.get(self._currently, "#000000"),  # Kolor ikony
            "all_data": self._attributes.get("all_data", []),
            "last_update": self._attributes.get("last_update", None),
        }

    async def async_update(self):
        """Fetch the latest data."""
        now = datetime.now()

        # Wymuszenie pobrania danych o 00:01
        if now.hour == 0 and now.minute == 1 and not self._force_midnight_update:
            self._force_midnight_update = True  # Zapobiega wielokrotnym pobraniom w ciągu tej samej minuty
            await self._fetch_data_for_day(now.strftime("%Y-%m-%d"))
            return

        # Zresetowanie flagi po północy
        if now.hour > 0:
            self._force_midnight_update = False

        # Regularne pobieranie danych w ramach interwału
        if self._last_update and now - self._last_update < self._update_interval:
            return

        self._last_update = now
        await self._fetch_data_for_day(now.strftime("%Y-%m-%d"))

        # Pobranie danych na następny dzień po godzinie 18
        if now.hour >= 18:
            next_day = (now + timedelta(days=1)).strftime("%Y-%m-%d")
            await self._fetch_data_for_day(next_day, is_next_day=True)

    async def _fetch_data_for_day(self, date, is_next_day=False):
        """Fetch data for a specific day."""
        url = API_URL.format(date=date)

        async with aiohttp.ClientSession() as session:
            try:
                with async_timeout.timeout(10):
                    response = await session.get(url)
                    if response.status == 200:
                        data = await response.json()
                        self._process_data(data, is_next_day=is_next_day)
                    elif is_next_day:
                        self._clear_next_day_data()
            except Exception as e:
                self._attributes["error"] = str(e)

    def _process_data(self, data, is_next_day):
        """Process data from API response."""
        now = datetime.now()
        all_data = data.get("value", [])

        if is_next_day:
            # Procesowanie danych na następny dzień
            self._next_day_data = all_data
            if all_data:
                self._next_day_max = max((entry["znacznik"] for entry in all_data), default=None)
                self._next_day_min = min((entry["znacznik"] for entry in all_data), default=None)
            else:
                self._next_day_max = None
                self._next_day_min = None
        else:
            # Procesowanie danych na bieżący dzień
            current_hour = now.strftime("%Y-%m-%d %H:00:00")
            matched_entry = next(
                (entry for entry in all_data if entry["udtczas"] == current_hour),
                None
            )

            # Set the currently value
            self._currently = matched_entry["znacznik"] if matched_entry else None

            # Calculate the daily max
            self._daily_max = max((entry["znacznik"] for entry in all_data), default=None)

            # Update the state
            if matched_entry:
                znacznik = matched_entry["znacznik"]
                self._state = STATE_MAPPING.get(znacznik, "UNKNOWN")
            else:
                self._state = "NO DATA"

            # Update attributes
            self._attributes["all_data"] = all_data
            self._attributes["last_update"] = now.isoformat()

    def _clear_next_day_data(self):
        """Clear next day data if unavailable."""
        self._next_day_data = None
        self._next_day_max = None
        self._next_day_min = None
