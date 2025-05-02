"""Config flow for my_temp_humid integration."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from . import DOMAIN

DEFAULT_HOST = "192.168.137.60"
DEFAULT_PORT = 80
DEFAULT_PATH = "/data"


class MyTempHumidFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for my_temp_humid."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._host = DEFAULT_HOST
        self._port = DEFAULT_PORT
        self._path = DEFAULT_PATH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self._host = user_input["host"]
            self._port = user_input["port"]
            self._path = user_input["path"]

            return self.async_create_entry(
                title=f"My Temp&Humid @ {self._host}",
                data={
                    "host": self._host,
                    "port": self._port,
                    "path": self._path
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required("host", default=self._host): str,
                vol.Required("port", default=self._port): int,
                vol.Required("path", default=self._path): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MyTempHumidOptionsFlowHandler(config_entry)


class MyTempHumidOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for my_temp_humid."""

    def __init__(self, config_entry):
        """Initialize."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({})
        return self.async_show_form(step_id="init", data_schema=data_schema)
