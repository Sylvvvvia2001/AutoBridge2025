"""Support for DHT11 Temperature and Humidity Sensor with ESP8266."""
from __future__ import annotations

import logging
from typing import Any

import requests
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_PATH,
    TEMP_CELSIUS,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = "http://192.168.137.120"
DEFAULT_PORT = 80
DEFAULT_PATH = "/data"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_PATH, default=DEFAULT_PATH): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the DHT11 sensor platform."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    path = config[CONF_PATH]

    url = f"{host}:{port}{path}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            add_entities(
                [
                    DHT11TemperatureSensor(url, "Temperature"),
                    DHT11HumiditySensor(url, "Humidity"),
                ]
            )
        else:
            _LOGGER.error("Unable to connect to DHT11 sensor at %s", url)
    except requests.exceptions.RequestException as err:
        _LOGGER.error("Error connecting to DHT11 sensor: %s", err)


class DHT11Sensor(SensorEntity):
    """Representation of a DHT11 sensor."""

    def __init__(self, url: str, name: str) -> None:
        """Initialize the sensor."""
        self._url = url
        self._name = name
        self._state = None
        self._available = True

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            response = requests.get(self._url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self._state = self._parse_data(data)
                self._available = True
            else:
                self._available = False
                _LOGGER.error("Unable to fetch data from DHT11 sensor")
        except requests.exceptions.RequestException as err:
            self._available = False
            _LOGGER.error("Error updating DHT11 sensor: %s", err)


class DHT11TemperatureSensor(DHT11Sensor):
    """Representation of a DHT11 temperature sensor."""

    def __init__(self, url: str, name: str) -> None:
        """Initialize the temperature sensor."""
        super().__init__(url, f"{name} Temperature")
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = TEMP_CELSIUS

    def _parse_data(self, data: dict[str, Any]) -> float:
        """Parse temperature from sensor data."""
        return float(data.get("temperature", 0))


class DHT11HumiditySensor(DHT11Sensor):
    """Representation of a DHT11 humidity sensor."""

    def __init__(self, url: str, name: str) -> None:
        """Initialize the humidity sensor."""
        super().__init__(url, f"{name} Humidity")
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_native_unit_of_measurement = PERCENTAGE

    def _parse_data(self, data: dict[str, Any]) -> float:
        """Parse humidity from sensor data."""
        return float(data.get("humidity", 0))