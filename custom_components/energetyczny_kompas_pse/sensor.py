import aiohttp
import async_timeout
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util.dt import now as ha_now
from .const import DOMAIN, STATE_MAPPING

API_URL = "https://api.raporty.pse.pl/api/pdgsz?$select=znacznik,udtczas&$filter=business_date eq '{date}'"

COLOR_MAPPING = {
    0: "#006600",  # Ciemno zielony
    1: "#ccff99",  # Jasno zielony
    2: "#ffcc00",  # Pomarańczowy
    3: "#FF0000"   # Czerwony
}

SENSOR_VERSION = "0.1.0"  # Wersja z poprawką czasu lokalnego

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor."""
    sensor = EnergetycznyKompasSensor(entry)
    async_add_entities([sensor])

    # Natychmiastowe odświeżenie danych po dodaniu encji
    await sensor.async_force_update()


class EnergetycznyKompasSensor(Entity):
    """Representation of the Energetyczny Kompas sensor."""

    def __init__(self, entry):
        self._state = None
        self._attributes = {}
        self._entry_id = entry.entry_id
        self._currently = None
        self._next_hour = None  # Stan dla następnej godziny
        self._daily_max = None
        self._next_day_data = None  # Dane na następny dzień
        self._next_day_max = None
        self._next_day_min = None
        self._all_data = []  # Przechowywane dane z API

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
            "friendly_name": "Energetyczny Kompas PSE",
            "currently": self._currently,
            "next_hour": self._next_hour,
            "daily_max": self._daily_max,
            "next_day_data": self._next_day_data,
            "next_day_max": self._next_day_max,
            "next_day_min": self._next_day_min,
            "color": COLOR_MAPPING.get(self._currently, "#000000"),
            "all_data": self._all_data,
            "last_update": self._attributes.get("last_update", None),
            "version": SENSOR_VERSION
        }

    async def async_update(self):
        """Fetch the latest data."""
        now = ha_now()

        # Pobranie danych na bieżący dzień
        await self._fetch_data_for_day(now.strftime("%Y-%m-%d"))

        # Pobranie danych na następny dzień, jeśli dostępne
        next_day = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        await self._fetch_data_for_day(next_day, is_next_day=True)

        # Aktualizacja stanu encji na podstawie pobranych danych
        self._update_current_state(now)

    async def async_force_update(self):
        """Force update data immediately."""
        now = ha_now()

        # Pobranie danych na bieżący dzień
        await self._fetch_data_for_day(now.strftime("%Y-%m-%d"))

        # Pobranie danych na następny dzień, jeśli dostępne
        next_day = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        await self._fetch_data_for_day(next_day, is_next_day=True)

        # Aktualizacja stanu encji na podstawie pobranych danych
        self._update_current_state(now)

    async def _fetch_data_for_day(self, date, is_next_day=False):
        """Fetch data for a specific day from the API."""
        url = API_URL.format(date=date)

        async with aiohttp.ClientSession() as session:
            try:
                with async_timeout.timeout(10):
                    response = await session.get(url)
                    if response.status == 200:
                        data = await response.json()
                        self._process_api_data(data, is_next_day)
            except Exception as e:
                self._attributes["error"] = str(e)

    def _process_api_data(self, data, is_next_day):
        """Process data fetched from the API."""
        all_data = data.get("value", [])

        if is_next_day:
            # Przetwarzanie danych na następny dzień
            self._next_day_data = all_data
            if all_data:
                self._next_day_max = max((entry["znacznik"] for entry in all_data), default=None)
                self._next_day_min = min((entry["znacznik"] for entry in all_data), default=None)
            else:
                self._next_day_max = None
                self._next_day_min = None
        else:
            # Przetwarzanie danych na bieżący dzień
            self._all_data = all_data
            if all_data:
                self._daily_max = max(entry["znacznik"] for entry in all_data)
            else:
                self._daily_max = None

        # Ustawienie czasu ostatniej aktualizacji
        self._attributes["last_update"] = data.get("value", [{}])[0].get("udtczas", "UNKNOWN")

    def _update_current_state(self, now):
        """Update the current state and attributes based on previously fetched data."""
        current_hour = now.strftime("%Y-%m-%d %H:00:00")
        next_hour = (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:00:00")

        matched_entry = next(
            (entry for entry in self._all_data if entry["udtczas"] == current_hour),
            None
        )
        next_hour_entry = next(
            (entry for entry in self._all_data if entry["udtczas"] == next_hour),
            None
        )

        # Ustawienie wartości currently i next_hour
        self._currently = matched_entry["znacznik"] if matched_entry else None
        self._next_hour = next_hour_entry["znacznik"] if next_hour_entry else None

        # Ustawienie stanu encji
        if matched_entry:
            self._state = STATE_MAPPING.get(self._currently, "UNKNOWN")
        else:
            self._state = "NO DATA"

        # Aktualizacja atrybutów
        self._attributes["currently"] = self._currently
        self._attributes["next_hour"] = self._next_hour
        self._attributes["last_update"] = ha_now().isoformat()
