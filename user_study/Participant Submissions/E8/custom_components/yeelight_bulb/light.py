import logging

from homeassistant.components.light import LightEntity
from homeassistant.const import CONF_HOST, CONF_NAME
from yeelight import Bulb

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """设置灯光平台。"""
    host = config[CONF_HOST]
    name = config.get(CONF_NAME, "Yeelight Bulb")

    bulb = Bulb(host)
    async_add_entities([YeelightBulb(bulb, name)])

class YeelightBulb(LightEntity):
    """表示一个Yeelight灯泡。"""

    def __init__(self, bulb, name):
        """初始化灯泡。"""
        self._bulb = bulb
        self._name = name
        self._is_on = False

    @property
    def name(self):
        """返回灯泡的名称。"""
        return self._name

    @property
    def is_on(self):
        """返回灯泡是否打开。"""
        return self._is_on

    def turn_on(self, **kwargs):
        """打开灯泡。"""
        self._bulb.turn_on()
        self._is_on = True

    def turn_off(self, **kwargs):
        """关闭灯泡。"""
        self._bulb.turn_off()
        self._is_on = False 