"""The Temperature & Humidity Sensor integration."""
import logging
import asyncio
import aiohttp
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    PLATFORMS,
    DEFAULT_SCAN_INTERVAL,
    CONF_HOST,
    CONF_PORT,
    CONF_PATH,
)



_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Temperature & Humidity Sensor from a config entry."""
    # 获取配置
    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT)
    path = entry.data.get(CONF_PATH)
    
    # 确保主机地址格式正确
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    
    url = f"{host}:{port}{path}"
    
    # 创建会话
    session = async_get_clientsession(hass)
    
    # 创建数据协调器
    coordinator = TempHumidCoordinator(
        hass=hass,
        logger=_LOGGER,
        name=DOMAIN,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        url=url,
        session=session,
    )
    
    # 初始数据获取
    await coordinator.async_config_entry_first_refresh()
    
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady(
            f"Failed to fetch initial data from sensor at {url}"
        )
    
    # 存储协调器以供平台使用
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # 设置平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # 添加更新监听器
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # 卸载平台
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # 移除数据
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class TempHumidCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the sensor."""

    def __init__(self, hass, logger, name, update_interval, url, session):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
        )
        self.url = url
        self.session = session

    async def _async_update_data(self):
        """Fetch data from the sensor."""
        try:
            async with self.session.get(self.url, timeout=10) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                
                data_text = await response.text()
                self.logger.debug("Received data: %s", data_text)
                
                # 解析数据 - 根据实际设备的响应格式调整
                try:
                    # 尝试解析为JSON
                    import json
                    data = json.loads(data_text)
                    return {
                        "temperature": float(data.get("temperature", 0)),
                        "humidity": float(data.get("humidity", 0)),
                        "battery": float(data.get("battery", 100)),
                        "last_update": data.get("timestamp", ""),
                    }
                except (json.JSONDecodeError, ValueError):
                    # 如果不是JSON，尝试解析文本格式
                    import re
                    temp_match = re.search(r"Temperature:\s*([\d.]+)", data_text)
                    humid_match = re.search(r"Humidity:\s*([\d.]+)", data_text)
                    
                    if not temp_match or not humid_match:
                        raise UpdateFailed("Could not parse sensor data")
                    
                    temperature = float(temp_match.group(1))
                    humidity = float(humid_match.group(1))
                    
                    return {
                        "temperature": temperature,
                        "humidity": humidity,
                        "battery": 100,  # 默认值
                        "last_update": "",
                    }
                    
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with sensor: {err}")