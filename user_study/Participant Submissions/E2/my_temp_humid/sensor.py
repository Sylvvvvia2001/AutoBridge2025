"""Sensor platform for my_temp_humid integration."""
import logging
import asyncio
import async_timeout
import aiohttp
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant

from homeassistant.const import (
    TEMP_CELSIUS,
    PERCENTAGE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
)

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)  # 每 30 秒轮询一次


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform."""
    # 读取我们在 config_flow 里存储的配置信息
    config = hass.data[DOMAIN][entry.entry_id]
    host = config["host"]
    port = config["port"]
    path = config["path"]

    coordinator = MyTempHumidDataUpdateCoordinator(hass, host, port, path)
    # 第一次立即更新数据
    await coordinator.async_config_entry_first_refresh()

    # 创建两个实体：温度、湿度
    sensors = [
        MyTempHumidTemperatureSensor(coordinator),
        MyTempHumidHumiditySensor(coordinator),
    ]
    async_add_entities(sensors, update_before_add=True)


class MyTempHumidDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the device endpoint."""

    def __init__(self, hass, host, port, path):
        """Initialize."""
        self._host = host
        self._port = port
        self._path = path

        super().__init__(
            hass,
            _LOGGER,
            name="my_temp_humid_coordinator",
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from the sensor's REST API."""
        url = f"http://{self._host}:{self._port}{self._path}"
        _LOGGER.debug("Requesting data from %s", url)

        try:
            async with async_timeout.timeout(10):  # 超时设置
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Request failed with status {response.status}")
                        data = await response.json()
                        # data 形如: {"temperature": 25.3, "humidity": 41.2}
                        return data
        except asyncio.TimeoutError as ex:
            raise UpdateFailed(f"Timeout error fetching data from {url}") from ex
        except aiohttp.ClientError as ex:
            raise UpdateFailed(f"Error fetching data from {url}: {ex}") from ex


class MyTempHumidBaseSensor(SensorEntity):
    """Base class for temperature/humidity sensor."""

    def __init__(self, coordinator: MyTempHumidDataUpdateCoordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator

    @property
    def should_poll(self):
        """No polling needed, we use DataUpdateCoordinator."""
        return False

    async def async_update(self):
        """Manual updates are handled by the coordinator."""

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        # 可以加一些额外属性
        return {
            "host": self.coordinator._host,
            "port": self.coordinator._port,
            "path": self.coordinator._path,
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    @property
    def available(self):
        """Return True if coordinator last update was successful."""
        return not self.coordinator.last_update_failed


class MyTempHumidTemperatureSensor(MyTempHumidBaseSensor):
    """Temperature sensor for the custom integration."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "My Temperature"

    @property
    def unique_id(self):
        """Unique ID for this sensor."""
        # 可以把 host + "temp" 等组合起来，以防重复
        return f"{self.coordinator._host}_temperature"

    @property
    def state(self):
        """Return the current temperature."""
        data = self.coordinator.data
        # 根据真实字段名称提取
        return data.get("temperature")

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE


class MyTempHumidHumiditySensor(MyTempHumidBaseSensor):
    """Humidity sensor for the custom integration."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "My Humidity"

    @property
    def unique_id(self):
        """Unique ID for this sensor."""
        return f"{self.coordinator._host}_humidity"

    @property
    def state(self):
        """Return the current humidity."""
        data = self.coordinator.data
        return data.get("humidity")

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def device_class(self):
        return DEVICE_CLASS_HUMIDITY
