from homeassistant import config_entries
from .const import DOMAIN

class EnergetycznyKompasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energetyczny Kompas PSE."""

    VERSION = 2  # Aktualizacja wersji

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Od razu utwórz wpis integracji bez formularza
        return self.async_create_entry(
            title="Energetyczny Kompas PSE", data={}
        )