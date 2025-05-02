"""The Yeelight LED Bulb 1S integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
import yeelight

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.LIGHT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Yeelight LED Bulb 1S from a config entry."""
    try:
        bulb = yeelight.Bulb(
            entry.data["host"],
            effect="smooth",
            duration=500,
            auto_gamma=True,
            power_mode=yeelight.PowerMode.NORMAL,
        )
        await hass.async_add_executor_job(bulb.get_properties)
    except yeelight.BulbException as ex:
        _LOGGER.error("Failed to initialize bulb: %s", ex)
        raise ConfigEntryNotReady from ex

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = bulb

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok 