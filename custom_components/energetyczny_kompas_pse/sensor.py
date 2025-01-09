import aiohttp
import async_timeout
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util.dt import now as ha_now, utcnow as ha_utcnow
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
    update_interval = entry.data.get("update_interval", 6)  # Domyślny interwał co 6 godzin
    async_add_entities([EnergetycznyKompasSensor(update_interval, entry)])


class EnergetycznyKompasSensor(Entity):
    """Representation of the Energetyczny Kompas sensor."""

    def __init__(self, update_interval, entry):
        self._state = None
        self._attributes = {}
        self._update_interval = timedelta(hours=update_interval)
        self._entry_id = entry.entry_id
        self._currently = None
        self._daily_max = None
        self._all_data = []  # Przechowywane dane z API
        self._next_update_time = None  # Czas następnego pobrania danych z API

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
            "color": COLOR_MAPPING.get(self._currently, "#000000"),
            "all_data": self._all_data,
            "last_update": self._attributes.get("last_update", None),
        }

    async def async_update(self):
        """Fetch the latest data."""
        now = ha_utcnow()

        # Aktualizacja stanu encji o pełnej godzinie
        self._update_current_state(now)

        # Pobranie nowych danych z API, jeśli minął interwał
        if not self._next_update_time or now >= self._next_update_time:
            self._next_update_time = now + self._update_interval
            await self._fetch_data_for_day(now.strftime("%Y-%m-%d"))

    async def _fetch_data_for_day(self, date):
        """Fetch data for a specific day from the API."""
        url = API_URL.format(date=date)

        async with aiohttp.ClientSession() as session:
            try:
                with async_timeout.timeout(10):
                    response = await session.get(url)
                    if response.status == 200:
                        data = await response.json()
                        self._process_api_data(data)
                    else:
                        self._attributes["error"] = f"API error: {response.status}"
            except Exception as e:
                self._attributes["error"] = str(e)

    def _process_api_data(self, data):
        """Process data fetched from the API."""
        all_data = data.get("value", [])
        self._all_data = all_data

        # Oblicz maksymalny znacznik dla dnia
        if all_data:
            self._daily_max = max(entry["znacznik"] for entry in all_data)
        else:
            self._daily_max = None

        # Ustawienie czasu ostatniej aktualizacji
        self._attributes["last_update"] = ha_utcnow().isoformat()

    def _update_current_state(self, now):
        """Update the current state based on previously fetched data."""
        current_hour = now.strftime("%Y-%m-%d %H:00:00")
        matched_entry = next(
            (entry for entry in self._all_data if entry["udtczas"] == current_hour),
            None
        )

        # Ustawienie wartości currently i stanu
        if matched_entry:
            self._currently = matched_entry["znacznik"]
            self._state = STATE_MAPPING.get(self._currently, "UNKNOWN")
        else:
            self._currently = None
            self._state = "NO DATA"
