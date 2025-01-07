import aiohttp
import async_timeout
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from .const import DOMAIN, SENSOR_NAME

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=6)

STATE_MAPPING = {
    0: "ZALECANE UŻYTKOWANIE",
    1: "NORMALNE UŻYTKOWANIE",
    3: "ZALECANE OSZCZĘDZANIE",
    4: "WYMAGANE OGRANICZANIE"
}

API_URL = "https://api.raporty.pse.pl/api/pdgsz?$select=znacznik,udtczas&$filter=business_date eq '{date}'"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Energetyczny Kompas PSE sensor."""
    async_add_entities([EnergetycznyKompasSensor()])


class EnergetycznyKompasSensor(Entity):
    """Representation of the Energetyczny Kompas sensor."""

    def __init__(self):
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return SENSOR_NAME

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return attributes of the sensor."""
        return self._attributes

    @property
    def icon(self):
        """Return an icon based on the state."""
        if self._state == "ZALECANE UŻYTKOWANIE":
            return "mdi:check-circle"
        elif self._state == "NORMALNE UŻYTKOWANIE":
            return "mdi:information"
        elif self._state == "ZALECANE OSZCZĘDZANIE":
            return "mdi:alert"
        elif self._state == "WYMAGANE OGRANICZANIE":
            return "mdi:alert-circle"
        return "mdi:power"

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Fetch new state data for the sensor."""
        today = datetime.now().strftime("%Y-%m-%d")
        url = API_URL.format(date=today)

        async with aiohttp.ClientSession() as session:
            try:
                with async_timeout.timeout(10):
                    response = await session.get(url)
                    if response.status == 200:
                        data = await response.json()
                        self._process_data(data)
                    else:
                        self._state = None
                        self._attributes = {"error": f"HTTP {response.status}"}
            except Exception as e:
                self._state = None
                self._attributes = {"error": str(e)}

    def _process_data(self, data):
        """Process data from API response."""
        now = datetime.now()
        current_hour = now.strftime("%Y-%m-%d %H:00:00")
        matched_entry = next(
            (entry for entry in data.get("value", []) if entry["udtczas"] == current_hour),
            None
        )

        if matched_entry:
            znacznik = matched_entry["znacznik"]
            self._state = STATE_MAPPING.get(znacznik, "UNKNOWN")
        else:
            self._state = "NO DATA"

        self._attributes = {
            "all_data": data.get("value", []),
            "last_update": datetime.now().isoformat()
        }