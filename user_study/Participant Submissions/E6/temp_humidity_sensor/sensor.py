"""Support for Temp Humidity Sensor."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
import async_timeout
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    SENSOR_TEMPERATURE,
    SENSOR_HUMIDITY,
    SENSOR_NAMES,
    SENSOR_UNITS,
    DEFAULT_PATH,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Temp Humidity Sensor."""
    host = config_entry.data["host"]
    port = config_entry.data["port"]
    base_url = f"{host}:{port}{DEFAULT_PATH}"

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="temp_humidity_sensor",
        update_method=lambda: async_get_data(hass, base_url),
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            TempHumiditySensor(coordinator, SENSOR_TEMPERATURE),
            TempHumiditySensor(coordinator, SENSOR_HUMIDITY),
        ]
    )

async def async_get_data(hass: HomeAssistant, base_url: str) -> dict:
    """Get data from the sensor."""
    async with async_timeout.timeout(10):
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as response:
                return await response.json()

class TempHumiditySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Temp Humidity Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"Temp Humidity {SENSOR_NAMES[sensor_type]}"
        self._attr_unique_id = f"{coordinator.data.get('device_id', 'unknown')}_{sensor_type}"
        self._attr_native_unit_of_measurement = SENSOR_UNITS[sensor_type]
        self._attr_device_class = (
            SensorDeviceClass.TEMPERATURE
            if sensor_type == SENSOR_TEMPERATURE
            else SensorDeviceClass.HUMIDITY
        )
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_type) 