import logging
from miio import Device, DeviceException
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP,
    LightEntity, PLATFORM_SCHEMA
)
from homeassistant.const import CONF_HOST, CONF_TOKEN, CONF_NAME
from homeassistant.exceptions import PlatformNotReady
from homeassistant.util.color import color_temperature_mired_to_kelvin as mired_to_kelvin, color_temperature_kelvin_to_mired as kelvin_to_mired

_LOGGER = logging.getLogger(__name__) 

CONF_MODEL = "model"
DEFAULT_NAME = "Mi Smart Desk Lamp Lite"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MODEL, default='philips.light.lite'): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Mi Smart Desk Lamp Lite light platform."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config[CONF_NAME]

    try:
        device = Device(host, token)
        mi_light = MiDeskLampLite(name, device)
        async_add_entities([mi_light], update_before_add=True)
    except DeviceException as ex:
        _LOGGER.error("Failed to setup Mi Smart Desk Lamp Lite: %s", ex)
        raise PlatformNotReady

class MiDeskLampLite(LightEntity):
    """Representation of the Mi Smart Desk Lamp Lite."""

    def __init__(self, name, device):
        """Initialize the lamp."""
        self._name = name
        self._device = device
        self._state = None
        self._brightness = None
        self._color_temp = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def brightness(self):
        """Return the brightness of the light if available."""
        return self._brightness

    @property
    def color_temp(self):
        """Return the color temperature of the light in mireds if available."""
        return self._color_temp

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on with optional brightness and color temperature."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            await self.hass.async_add_executor_job(self._device.send, 'set_bright', [brightness])
        if ATTR_COLOR_TEMP in kwargs:
            color_temp = mired_to_kelvin(kwargs[ATTR_COLOR_TEMP])
            await self.hass.async_add_executor_job(self._device.send, 'set_ct_abx', [color_temp, "smooth", 500])
        if not self._state:
            await self.hass.async_add_executor_job(self._device.send, 'set_power', ['on', "smooth", 500])
        self._state = True

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        await self.hass.async_add_executor_job(self._device.send, 'set_power', ['off', "smooth", 500])
        self._state = False

    async def async_update(self):
        """Fetch new state data for this light."""
        try:
            data = await self.hass.async_add_executor_job(self._device.status)
            self._state = data.is_on()
            self._brightness = data.brightness()
            self._color_temp = kelvin_to_mired(data.color_temperature())
        except DeviceException as ex:
            _LOGGER.error("Failed to update Mi Smart Desk Lamp Lite status: %s", ex)
            self._state = None
            self._brightness = None
            self._color_temp = None
