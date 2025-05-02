"""Support for Yeelight LED Bulb 1S (Color)."""
import logging
import voluptuous as vol

from yeelight import Bulb, BulbException
from homeassistant.components.light import (
    LightEntity, PLATFORM_SCHEMA, SUPPORT_COLOR, SUPPORT_BRIGHTNESS
)
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Yeelight 1S Color"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Yeelight 1S Color light platform."""
    host = config[CONF_HOST]
    name = config[CONF_NAME]

    try:
        bulb = Bulb(host)
        # 测试连接
        bulb.get_properties()
    except BulbException as err:
        _LOGGER.error("无法连接到 %s: %s", host, err)
        return

    add_entities([YeelightColorBulb(name, bulb)], True)


class YeelightColorBulb(LightEntity):
    """Representation of a Yeelight 1S Color bulb."""

    def __init__(self, name, bulb: Bulb):
        """Initialize the bulb."""
        self._name = name
        self._bulb = bulb
        self._is_on = False
        self._brightness = 0
        self._hs_color = (0, 0)

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._is_on

    @property
    def brightness(self):
        """Return the brightness (0..255)."""
        return self._brightness

    @property
    def hs_color(self):
        """Return the current color as HS tuple."""
        return self._hs_color

    @property
    def supported_features(self):
        """Flag supported features: color + brightness."""
        return SUPPORT_COLOR | SUPPORT_BRIGHTNESS

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        # 处理亮度
        if kwargs.get("brightness") is not None:
            bri = int(kwargs["brightness"] / 255 * 100)
            self._bulb.set_brightness(bri)
        # 处理颜色
        if kwargs.get("hs_color") is not None:
            h, s = kwargs["hs_color"]
            self._bulb.set_hsv(int(h), int(s))
        # 最后打开
        self._bulb.turn_on()
        self._is_on = True

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._bulb.turn_off()
        self._is_on = False

    def update(self):
        """Fetch state from the bulb."""
        try:
            props = self._bulb.get_properties(
                ["power", "bright", "hue", "sat"]
            )
        except BulbException as err:
            _LOGGER.warning("更新状态失败: %s", err)
            return

        self._is_on = (props.get("power") == "on")
        # Yeelight 的亮度是 1..100
        self._brightness = int(int(props.get("bright", 0)) / 100 * 255)
        # Hue: 0..360, Sat: 0..100
        hue = int(props.get("hue", 0))
        sat = int(props.get("sat", 0))
        self._hs_color = (hue, sat)