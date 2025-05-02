"""The Yeelight 1S Color custom component."""
import asyncio
import logging

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "yeelight_1s_color"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Yeelight 1S Color component (nothing to do here)."""
    _LOGGER.debug("Yeelight 1S Color custom component is initialized.")
    return True