import logging
from yeelight import Bulb
from homeassistant.components.light import (
    LightEntity,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """从 entry 中读取配置，创建并注册 Light 实体。"""
    conf = hass.data[DOMAIN][entry.entry_id]
    host = conf["host"]
    name = conf["name"]
    async_add_entities([YeelightColorBulb(name, host)], True)

class YeelightColorBulb(LightEntity):
    """Yeelight LED Bulb 1S (Color) 实体实现。"""

    def __init__(self, name: str, host: str):
        self._name = name
        self._host = host
        self._bulb = Bulb(host)
        self._available = False
        self._is_on = False
        self._brightness = 0  # 1-100
        self._hs_color = (0.0, 0.0)  # (hue, sat)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"yeelight_1s_color_{self._host}"

    @property
    def available(self):
        return self._available

    @property
    def is_on(self):
        return self._is_on

    @property
    def brightness(self):
        # Home Assistant 亮度范围 0-255
        return int(self._brightness / 100 * 255)

    @property
    def hs_color(self):
        return self._hs_color

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR

    async def async_turn_on(self, **kwargs):
        # 设置亮度
        if "brightness" in kwargs:
            bri = max(1, min(100, int(kwargs["brightness"] / 255 * 100)))
            await self.hass.async_add_executor_job(self._bulb.set_brightness, bri)
            self._brightness = bri

        # 设置颜色
        if "hs_color" in kwargs:
            hue, sat = kwargs["hs_color"]
            await self.hass.async_add_executor_job(
                self._bulb.set_hsv, int(hue), int(sat), self._brightness or 100
            )
            self._hs_color = (hue, sat)

        # 开灯
        await self.hass.async_add_executor_job(self._bulb.turn_on)
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._bulb.turn_off)
        self._is_on = False

    async def async_update(self):
        """定期更新状态，从灯泡读取属性。"""
        try:
            props = await self.hass.async_add_executor_job(self._bulb.get_properties)
            self._available = True
            self._is_on = props.get("power") == "on"
            self._brightness = int(props.get("bright", 0))
            hue = float(props.get("hue", 0))
            sat = float(props.get("sat", 0))
            self._hs_color = (hue, sat)
        except Exception as e:
            _LOGGER.warning("无法更新 Yeelight %s 状态: %s", self._name, e)
            self._available = False