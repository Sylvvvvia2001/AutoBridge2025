"""The Yeelight LED Bulb 1S (Color) integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import asyncio

_LOGGER = logging.getLogger(__name__)

DOMAIN = "yeelight_s1"
PLATFORMS = ["light"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Yeelight LED Bulb 1S component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Yeelight LED Bulb 1S from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok 