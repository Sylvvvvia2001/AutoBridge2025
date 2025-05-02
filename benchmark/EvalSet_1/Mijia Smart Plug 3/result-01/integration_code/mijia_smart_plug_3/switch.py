"""Support for Xiaomi Mijia Smart Plug 3."""
import logging
from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.exceptions import PlatformNotReady
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from miio import Device, DeviceException, ChuangmiPlug

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Mijia Smart Plug 3"
DATA_KEY = "switch.mijia_smart_plug_3"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Mijia Smart Plug 3 from config."""
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config[CONF_NAME]

    _LOGGER.info("Initializing Mijia Smart Plug 3 with host %s (token %s...)", host, token[:5])

    try:
        plug = ChuangmiPlug(host, token, model="chuangmi.plug.v3")
        device = MijiaSmartPlug3Switch(name, plug)
        async_add_entities([device], update_before_add=True)
        hass.data[DATA_KEY][host] = device
    except DeviceException as ex:
        raise PlatformNotReady from ex

class MijiaSmartPlug3Switch(SwitchEntity):
    """Representation of a Mijia Smart Plug 3."""

    def __init__(self, name, plug):
        """Initialize the plug switch."""
        self._name = name
        self._plug = plug
        self._state = None
        self._available = False

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the plug on."""
        await self.hass.async_add_executor_job(self._plug.on)
        self._state = True

    async def async_turn_off(self, **kwargs):
        """Turn the plug off."""
        await self.hass.async_add_executor_job(self._plug.off)
        self._state = False

    async def async_update(self):
        """Fetch new state data for the switch."""
        try:
            status = await self.hass.async_add_executor_job(self._plug.status)
            self._state = status.is_on
            self._available = True
        except DeviceException:
            self._available = False
            _LOGGER.error("Could not retrieve status from Mijia Smart Plug 3")
