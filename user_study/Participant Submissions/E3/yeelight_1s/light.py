"""Support for Yeelight LED Bulb 1S."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_EFFECT,
    ATTR_FLASH,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ATTR_TRANSITION,
    COLOR_MODE_BRIGHTNESS,
    COLOR_MODE_COLOR_TEMP,
    COLOR_MODE_RGB,
    EFFECT_COLORLOOP,
    EFFECT_OFF,
    FLASH_LONG,
    FLASH_SHORT,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import yeelight

from .const import (
    ATTR_FLOWING,
    ATTR_MUSIC_MODE,
    ATTR_NIGHTLIGHT,
    DEFAULT_MODE,
    DEFAULT_NAME,
    DEFAULT_TRANSITION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_YEELIGHT = (
    yeelight.BulbType.Color
    | yeelight.BulbType.WhiteTemp
    | yeelight.BulbType.WhiteTempMood
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Yeelight LED Bulb 1S light."""
    bulb = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([YeelightLight(bulb, config_entry)], True)

class YeelightLight(LightEntity):
    """Representation of a Yeelight LED Bulb 1S."""

    def __init__(self, bulb: yeelight.Bulb, config_entry: ConfigEntry) -> None:
        """Initialize the light."""
        self._bulb = bulb
        self._config_entry = config_entry
        self._attr_unique_id = config_entry.entry_id
        self._attr_name = DEFAULT_NAME
        self._attr_available = False
        self._attr_supported_color_modes = set()
        self._attr_supported_features = 0
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name=self._attr_name,
            manufacturer="Xiaomi",
            model="Yeelight LED Bulb 1S",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._attr_available

    @property
    def brightness(self) -> Optional[int]:
        """Return the brightness of this light between 0 and 255."""
        return self._bulb.brightness

    @property
    def color_mode(self) -> str:
        """Return the color mode of the light."""
        if self._bulb.color_mode == yeelight.ColorMode.RGB:
            return COLOR_MODE_RGB
        if self._bulb.color_mode == yeelight.ColorMode.COLOR_TEMP:
            return COLOR_MODE_COLOR_TEMP
        return COLOR_MODE_BRIGHTNESS

    @property
    def hs_color(self) -> Optional[Tuple[float, float]]:
        """Return the hs color value."""
        if self.color_mode != COLOR_MODE_RGB:
            return None
        return self._bulb.hs_color

    @property
    def rgb_color(self) -> Optional[Tuple[int, int, int]]:
        """Return the rgb color value."""
        if self.color_mode != COLOR_MODE_RGB:
            return None
        return self._bulb.rgb_color

    @property
    def color_temp(self) -> Optional[int]:
        """Return the color temperature."""
        if self.color_mode != COLOR_MODE_COLOR_TEMP:
            return None
        return self._bulb.color_temp

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        hs_color = kwargs.get(ATTR_HS_COLOR)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        color_temp = kwargs.get(ATTR_COLOR_TEMP)
        transition = kwargs.get(ATTR_TRANSITION, DEFAULT_TRANSITION)
        effect = kwargs.get(ATTR_EFFECT)
        flash = kwargs.get(ATTR_FLASH)

        if flash:
            if flash == FLASH_SHORT:
                await self._bulb.turn_on(effect="sudden", duration=50)
            elif flash == FLASH_LONG:
                await self._bulb.turn_on(effect="sudden", duration=1000)
            return

        if effect:
            if effect == EFFECT_COLORLOOP:
                await self._bulb.start_flow(
                    yeelight.Flow.rainbow,
                    duration=transition * 1000,
                )
            elif effect == EFFECT_OFF:
                await self._bulb.stop_flow()
            return

        if brightness is not None:
            await self._bulb.set_brightness(brightness, duration=transition)

        if hs_color is not None:
            await self._bulb.set_hsv(
                hs_color[0],
                hs_color[1] * 100,
                brightness or self.brightness,
                duration=transition,
            )
        elif rgb_color is not None:
            await self._bulb.set_rgb(
                rgb_color[0],
                rgb_color[1],
                rgb_color[2],
                duration=transition,
            )
        elif color_temp is not None:
            await self._bulb.set_color_temp(
                color_temp,
                brightness or self.brightness,
                duration=transition,
            )
        else:
            await self._bulb.turn_on(duration=transition)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        transition = kwargs.get(ATTR_TRANSITION, DEFAULT_TRANSITION)
        await self._bulb.turn_off(duration=transition)

    async def async_update(self) -> None:
        """Update light properties."""
        try:
            await self._bulb.get_properties()
            self._attr_available = True
        except yeelight.BulbException as ex:
            _LOGGER.error("Failed to update bulb state: %s", ex)
            self._attr_available = False 