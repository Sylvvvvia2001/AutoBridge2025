"""Support for Temperature Humidity Sensor."""
from datetime import timedelta
import logging
import asyncio
import aiohttp
import async_timeout
import json
from urllib.parse import urljoin

import voluptuous as vol

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_PATH,
    TEMP_CELSIUS,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.helpers.config_validation as cv

from .const import (
    DEFAULT_NAME,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PATH,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_PATH, default=DEFAULT_PATH): cv.string,
    }
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Temperature Humidity Sensor platform."""
    name = config.get(CONF_NAME, DEFAULT_NAME)
    host = config.get(CONF_HOST, DEFAULT_HOST)
    port = config.get(CONF_PORT, DEFAULT_PORT)
    path = config.get(CONF_PATH, DEFAULT_PATH)

    if not host:
        _LOGGER.error("Host cannot be empty")
        return

    # 构建基础URL
    base_url = str(host)  # 确保host是字符串
    if not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}"
    if port:
        base_url = f"{base_url}:{port}"

    _LOGGER.debug("Setting up sensor with base_url: %s, path: %s", base_url, path)

    async_add_entities(
        [
            TemperatureSensor(name, base_url, path),
            HumiditySensor(name, base_url, path),
        ],
        True,
    )

class TempHumidSensorBase(SensorEntity):
    """Base class for Temperature Humidity Sensor."""

    def __init__(self, name, base_url, path):
        """Initialize the sensor."""
        self._base_url = base_url
        self._path = path
        self._name = name
        self._state = None
        self._available = True

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    async def async_update(self):
        """Get the latest data from the sensor."""
        try:
            url = urljoin(self._base_url, self._path.lstrip('/'))
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(10):
                    async with session.get(url) as response:
                        if response.status != 200:
                            self._available = False
                            _LOGGER.error("Error fetching data: HTTP status %s", response.status)
                            return
                        try:
                            data = await response.json()
                            _LOGGER.debug("Received data: %s", data)
                            self._process_data(data)
                            self._available = True
                        except json.JSONDecodeError as err:
                            self._available = False
                            _LOGGER.error("Error decoding JSON: %s", err)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self._available = False
            _LOGGER.error("Error fetching data: %s", err)
        except Exception as err:
            self._available = False
            _LOGGER.exception("Unexpected error: %s", err)

    def _process_data(self, data):
        """Process the data from the sensor."""
        raise NotImplementedError

class TemperatureSensor(TempHumidSensorBase):
    """Representation of a Temperature Sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = TEMP_CELSIUS

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} Temperature"

    def _process_data(self, data):
        """Process temperature data."""
        try:
            if isinstance(data, dict) and "temperature" in data:
                self._state = float(data["temperature"])
            else:
                _LOGGER.error("Invalid data format: %s", data)
                self._state = None
        except (ValueError, TypeError) as err:
            _LOGGER.error("Error processing temperature data: %s", err)
            self._state = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

class HumiditySensor(TempHumidSensorBase):
    """Representation of a Humidity Sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} Humidity"

    def _process_data(self, data):
        """Process humidity data."""
        try:
            if isinstance(data, dict) and "humidity" in data:
                self._state = float(data["humidity"])
            else:
                _LOGGER.error("Invalid data format: %s", data)
                self._state = None
        except (ValueError, TypeError) as err:
            _LOGGER.error("Error processing humidity data: %s", err)
            self._state = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state 