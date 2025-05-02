import logging
from yeelight import Bulb, BulbException
import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_HS_COLOR, SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR, LightEntity, PLATFORM_SCHEMA
)
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Yeelight 1S"
SUPPORT_YEELIGHT = SUPPORT_BRIGHTNESS | SUPPORT_COLOR

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    ip = config[CONF_IP_ADDRESS]
    name = config[CONF_NAME]

    try:
        bulb = Bulb(ip)
        bulb.get_properties()
    except BulbException as e:
        _LOGGER.error(f"Could not connect to Yeelight bulb at {ip}: {e}")
        return

    add_entities([Yeelight1SLight(bulb, name)], True)


class Yeelight1SLight(LightEntity):
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
    def is_on(self):
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    @property
    def hs_color(self):
        return self._hs_color

    @property
    def supported_features(self):
        return SUPPORT_YEELIGHT

    def turn_on(self, **kwargs):
        self._is_on = True
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
            brightness_pct = int((self._brightness / 255) * 100)
            self._bulb.set_brightness(brightness_pct)
        if ATTR_HS_COLOR in kwargs:
            self._hs_color = kwargs[ATTR_HS_COLOR]
            h, s = self._hs_color
            self._bulb.set_hsv(h, s)
        self._bulb.turn_on()

    def turn_off(self, **kwargs):
        self._bulb.turn_off()
        self._is_on = False

    def update(self):
        try:
            props = self._bulb.get_properties()
            self._is_on = props["power"] == "on"
            self._brightness = int(int(props["bright"]) * 2.55)
            self._hs_color = (float(props["hue"]), float(props["sat"]))
        except BulbException as e:
            _LOGGER.error(f"Failed to update Yeelight bulb: {e}")