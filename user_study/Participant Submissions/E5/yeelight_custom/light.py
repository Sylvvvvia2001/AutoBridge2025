import logging
import voluptuous as vol
from yeelight import Bulb, discover_bulbs
from yeelight.main import _BulbRegistry

from homeassistant.components.light import (
    PLATFORM_SCHEMA,
    LightEntity,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_RGB_COLOR,
    SUPPORT_EFFECT,
    SUPPORT_TRANSITION
)
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Yeelight Custom"
DEFAULT_TRANSITION = 350

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

SUPPORT_YEELIGHT = (
    SUPPORT_BRIGHTNESS |
    SUPPORT_COLOR_TEMP |
    SUPPORT_RGB_COLOR |
    SUPPORT_EFFECT |
    SUPPORT_TRANSITION
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """平台初始化"""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)

    # 绕过自动发现
    _BulbRegistry._INSTANCE = None  # 防止官方集成干扰

    bulb = YeelightCustomLight(host, name)
    add_entities([bulb], True)

class YeelightCustomLight(LightEntity):
    """自定义设备类"""

    def __init__(self, host, name):
        self._host = host
        self._name = name
        self._is_on = False
        self._brightness = 255
        self._rgb_color = [255, 255, 255]
        self._color_temp = 4000
        self._bulb = Bulb(host, auto_on=False)

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
    def rgb_color(self):
        return self._rgb_color

    @property
    def color_temp(self):
        return self._color_temp

    @property
    def supported_features(self):
        return SUPPORT_YEELIGHT

    def turn_on(self, **kwargs):
        """开灯"""
        effect = "smooth" if kwargs.get("transition", 0) > 0 else "sudden"
        
        if kwargs.get("brightness"):
            self._bulb.set_brightness(
                int(kwargs["brightness"] / 255 * 100),
                duration=kwargs.get("transition", DEFAULT_TRANSITION),
                effect=effect
            )

        if kwargs.get("rgb_color"):
            self._bulb.set_rgb(
                *kwargs["rgb_color"],
                duration=kwargs.get("transition", DEFAULT_TRANSITION),
                effect=effect
            )

        self._bulb.turn_on()
        self._is_on = True

    def turn_off(self, **kwargs):
        """关灯"""
        self._bulb.turn_off()
        self._is_on = False

    def update(self):
        """主动更新状态"""
        try:
            props = self._bulb.get_properties([
                "power", "bright", "rgb", "ct"
            ])
            
            self._is_on = props["power"] == "on"
            self._brightness = int(int(props["bright"]) / 100 * 255)
            
            if props["rgb"]:
                rgb = int(props["rgb"])
                self._rgb_color = [
                    (rgb >> 16) & 0xFF,
                    (rgb >> 8) & 0xFF,
                    rgb & 0xFF
                ]
                
            self._color_temp = int(props["ct"])

        except Exception as e:
            _LOGGER.error("Yeelight更新状态失败: %s", e)