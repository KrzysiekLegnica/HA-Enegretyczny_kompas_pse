from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class EnergetycznyKompasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energetyczny Kompas PSE."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Energetyczny Kompas PSE", data=user_input)

        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return EnergetycznyKompasOptionsFlow(config_entry)


class EnergetycznyKompasOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Energetyczny Kompas PSE."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init")
