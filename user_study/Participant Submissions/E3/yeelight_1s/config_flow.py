"""Config flow for Yeelight LED Bulb 1S integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import yeelight

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

class YeelightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yeelight LED Bulb 1S."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                bulb = yeelight.Bulb(user_input[CONF_HOST])
                await self.hass.async_add_executor_job(bulb.get_properties)
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
            except yeelight.BulbException as ex:
                _LOGGER.error("Failed to initialize bulb: %s", ex)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        ) 