"""Config flow for Yeelight LED Bulb 1S integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from yeelight import Bulb, BulbException

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class YeelightS1ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yeelight LED Bulb 1S."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # 尝试连接到灯泡
                bulb = Bulb(user_input[CONF_HOST])
                await self.hass.async_add_executor_job(bulb.get_properties)

                # 创建条目
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )
            except BulbException:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_NAME): str,
                }
            ),
            errors=errors,
        ) 