import logging
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    LightEntity,
)
from yeelight import Bulb, discover_bulbs

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    ip_address = config.get("ip")
    if not ip_address:
        _LOGGER.info("Discovering Yeelight devices...")
        bulbs = discover_bulbs()
        if bulbs:
            ip_address = bulbs[0]['ip']
            _LOGGER.info(f"Found Yeelight bulb at {ip_address}")
        else:
            _LOGGER.error("No Yeelight bulbs found.")
            return

    bulb = Bulb(ip_address)
    add_entities([YeelightCustomLight(bulb)], True)

class YeelightCustomLight(LightEntity):
    def __init__(self, bulb):
        self._bulb = bulb
        self._name = "Yeelight 1S Custom"
        self._state = False
        self._brightness = 255
        self._hs_color = (0, 0)

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def brightness(self):
        return self._brightness

    @property
    def hs_color(self):
        return self._hs_color

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR

    def turn_on(self, **kwargs):
        brightness = kwargs.get(ATTR_BRIGHTNESS, self._brightness)
        hs_color = kwargs.get(ATTR_HS_COLOR, self._hs_color)

        rgb = self.hs_to_rgb(*hs_color)
        try:
            self._bulb.set_rgb(*rgb)
            self._bulb.set_brightness(int(brightness / 255 * 100))
            self._state = True
            self._brightness = brightness
            self._hs_color = hs_color
        except Exception as e:
            _LOGGER.error(f"Error turning on bulb: {e}")

    def turn_off(self, **kwargs):
        try:
            self._bulb.turn_off()
            self._state = False
        except Exception as e:
            _LOGGER.error(f"Error turning off bulb: {e}")

    def update(self):
        try:
            props = self._bulb.get_properties()
            self._state = props["power"] == "on"
            self._brightness = int(int(props["bright"]) / 100 * 255)
            rgb = int(props["rgb"])
            self._hs_color = self.rgb_to_hs((rgb >> 16 & 0xFF, rgb >> 8 & 0xFF, rgb & 0xFF))
        except Exception as e:
            _LOGGER.error(f"Error updating bulb status: {e}")

    @staticmethod
    def hs_to_rgb(h, s):
        import colorsys
        rgb = colorsys.hsv_to_rgb(h / 360, s / 100, 1)
        return tuple(int(x * 255) for x in rgb)

    @staticmethod
    def rgb_to_hs(rgb):
        import colorsys
        hsv = colorsys.rgb_to_hsv(*(x / 255 for x in rgb))
        return (hsv[0] * 360, hsv[1] * 100)