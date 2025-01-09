from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

class EnergetycznyKompasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energetyczny Kompas PSE."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Energetyczny Kompas PSE", data={"update_interval": user_input["update_interval"]}
            )

        schema = vol.Schema({
            vol.Required(
                "update_interval",
                default=DEFAULT_UPDATE_INTERVAL
            ): vol.All(int, vol.Range(min=1, max=24))
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "update_interval": "Częstotliwość odświeżania danych (w godzinach)"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return EnergetycznyKompasOptionsFlow(config_entry)


class EnergetycznyKompasOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Energetyczny Kompas PSE."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Zastąpienie "update_interval" czytelną nazwą
        schema = vol.Schema({
            vol.Required(
                "update_interval",
                default=self.config_entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL)
            ): vol.All(int, vol.Range(min=1, max=24))
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders=None,
            errors=None
        )
