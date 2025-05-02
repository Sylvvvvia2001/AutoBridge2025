import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_HS_COLOR, SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR, LightEntity
)
from homeassistant.const import CONF_IP_ADDRESS
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from yeelight import Bulb, BulbException
from .const import DOMAIN, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Optional("name", default=DEFAULT_NAME): cv.string,
})

SUPPORT_YEELIGHT = SUPPORT_BRIGHTNESS | SUPPORT_COLOR

def setup_platform(hass, config, add_entities, discovery_info=None):
    ip = config[CONF_IP_ADDRESS]
    name = config.get("name")

    try:
        bulb = Bulb(ip)
        bulb.get_properties()
    except BulbException as ex:
        _LOGGER.error(f"Could not connect to Yeelight Bulb at {ip}: {ex}")
        return

    add_entities([YeelightLANLight(bulb, name)], True)

class YeelightLANLight(LightEntity):
    def __init__(self, bulb, name):
        self._bulb = bulb
        self._name = name
        self._is_on = False
        self._brightness = 255
        self._hs_color = (0, 0)

    @property
    def name(self):
        return self._name

    @property
    def supported_features(self):
        return SUPPORT_YEELIGHT

    @property
    def is_on(self):
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    @property
    def hs_color(self):
        return self._hs_color

    def turn_on(self, **kwargs):
        self._bulb.turn_on()
        self._is_on = True

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] * 100 / 255)
            self._bulb.set_brightness(brightness)
            self._brightness = kwargs[ATTR_BRIGHTNESS]

        if ATTR_HS_COLOR in kwargs:
            hue, sat = kwargs[ATTR_HS_COLOR]
            self._bulb.set_hsv(hue, sat)
            self._hs_color = (hue, sat)

    def turn_off(self, **kwargs):
        self._bulb.turn_off()
        self._is_on = False

    def update(self):
        try:
            props = self._bulb.get_properties()
            self._is_on = props["power"] == "on"
            self._brightness = int(int(props.get("bright", 100)) * 255 / 100)
            self._hs_color = (float(props.get("hue", 0)), float(props.get("sat", 0)))
        except Exception as e:
            _LOGGER.warning(f"Failed to update Yeelight state: {e}")