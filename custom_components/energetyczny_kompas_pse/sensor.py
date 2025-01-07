from homeassistant.helpers.entity import Entity
from .const import DOMAIN, SENSOR_NAME, STATES
import random

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Energetyczny Kompas PSE sensor."""
    async_add_entities([EnergetycznyKompasSensor()])


class EnergetycznyKompasSensor(Entity):
    """Representation of the Energetyczny Kompas sensor."""

    def __init__(self):
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return SENSOR_NAME

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

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

    async def async_update(self):
        """Fetch new state data for the sensor."""
        self._state = random.choice(STATES)  # Symulacja losowego stanu