"""Platform for Yeelight LED Bulb 1S light integration."""
import logging
from typing import Any, Dict, Optional

from yeelight import Bulb, BulbException
import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_COLOR_TEMP,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
import homeassistant.helpers.config_validation as cv
from homeassistant.util.color import (
    color_temperature_kelvin_to_mired,
    color_temperature_mired_to_kelvin,
)

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Yeelight light platform."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]

    bulb = Bulb(host)
    
    async_add_entities([YeelightS1Bulb(bulb, name)], True)

class YeelightS1Bulb(LightEntity):
    """Representation of a Yeelight LED Bulb 1S."""

    def __init__(self, bulb: Bulb, name: str):
        """Initialize the light."""
        self._bulb = bulb
        self._name = name
        self._available = True
        self._state = None
        self._brightness = None
        self._color_temp = None
        self._hs = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def available(self):
        """Return True if light is available."""
        return self._available

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def hs_color(self):
        """Return the hs color value."""
        return self._hs

    @property
    def color_temp(self):
        """Return the color temperature."""
        return self._color_temp

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_COLOR_TEMP

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        try:
            if not self.is_on:
                await self.hass.async_add_executor_job(self._bulb.turn_on)

            if ATTR_BRIGHTNESS in kwargs:
                brightness = kwargs[ATTR_BRIGHTNESS]
                await self.hass.async_add_executor_job(
                    self._bulb.set_brightness, round((brightness / 255) * 100)
                )

            if ATTR_HS_COLOR in kwargs:
                hs_color = kwargs[ATTR_HS_COLOR]
                await self.hass.async_add_executor_job(
                    self._bulb.set_hsv, hs_color[0], hs_color[1], self._brightness or 100
                )

            if ATTR_COLOR_TEMP in kwargs:
                color_temp = kwargs[ATTR_COLOR_TEMP]
                await self.hass.async_add_executor_job(
                    self._bulb.set_color_temp,
                    color_temperature_mired_to_kelvin(color_temp)
                )

        except BulbException as ex:
            _LOGGER.error("Unable to turn on light: %s", ex)
            self._available = False

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        try:
            await self.hass.async_add_executor_job(self._bulb.turn_off)
        except BulbException as ex:
            _LOGGER.error("Unable to turn off light: %s", ex)
            self._available = False

    async def async_update(self):
        """Fetch new state data for this light."""
        try:
            properties = await self.hass.async_add_executor_job(self._bulb.get_properties)
            
            self._available = True
            self._state = properties["power"] == "on"
            
            if self._state:
                self._brightness = round((int(properties["bright"]) / 100) * 255)
                self._color_temp = color_temperature_kelvin_to_mired(
                    int(properties["ct"])
                )
                self._hs = (
                    float(properties["hue"]),
                    float(properties["sat"]),
                )
                
        except BulbException as ex:
            _LOGGER.error("Unable to update light: %s", ex)
            self._available = False 