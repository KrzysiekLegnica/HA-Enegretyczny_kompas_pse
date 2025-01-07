from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class EnergetycznyKompasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energetyczny Kompas PSE."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Validate the input
            interval = user_input.get("update_interval", 6)
            if interval < 1 or interval > 24:
                return self.async_show_form(
                    step_id="user",
                    errors={"update_interval": "invalid_interval"}
                )

            return self.async_create_entry(
                title="Energetyczny Kompas PSE", data={"update_interval": interval}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                {
                    "update_interval": int,
                },
                {
                    "update_interval": 6,  # Default to every 6 hours
                },
            ),
        )

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

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                {
                    "update_interval": int,
                },
                self.config_entry.options,
            ),
        )
