import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """仅做基础初始化，无需配置即可加载。"""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """当用户通过 UI 或 yaml 配置完成后，设置实体并转发到 light 平台。"""
    hass.data.setdefault(DOMAIN, {})
    host = entry.data["host"]
    name = entry.data.get("name")
    # 在 light.py 中会读取 hass.data[DOMAIN][entry_id] 作为实体
    hass.data[DOMAIN][entry.entry_id] = {
        "host": host,
        "name": name,
    }
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "light")
    )
    _LOGGER.debug("Yeelight 1S Color entry setup: %s", entry.data)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """卸载配置项时，移除实体。"""
    hass.data[DOMAIN].pop(entry.entry_id)
    return await hass.config_entries.async_forward_entry_unload(entry, "light")