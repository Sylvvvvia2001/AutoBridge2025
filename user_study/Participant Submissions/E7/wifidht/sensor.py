"""在 HA 中创建两个传感器实体：温度和湿度。"""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    async_add_entities(
        [
            DHTTemperatureSensor(coordinator, entry.entry_id),
            DHTHumiditySensor(coordinator, entry.entry_id),
        ]
    )


class DHTBaseSensor(CoordinatorEntity, SensorEntity):
    """公共基类，负责把 coordinator 数据映射成状态。"""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}-{self.key}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self.key)

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()


class DHTTemperatureSensor(DHTBaseSensor):
    key = "temperature"
    _attr_device_class = "temperature"
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_translation_key = "temperature"


class DHTHumiditySensor(DHTBaseSensor):
    key = "humidity"
    _attr_device_class = "humidity"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "humidity"