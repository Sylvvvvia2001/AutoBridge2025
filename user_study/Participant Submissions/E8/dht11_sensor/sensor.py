# custom_components/dht11_sensor/sensor.py
import logging
import aiohttp
import async_timeout
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    config = entry.data
    
    coordinator = DHT11Coordinator(hass, config)
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        DHT11TemperatureSensor(coordinator, config),
        DHT11HumiditySensor(coordinator, config)
    ]
    async_add_entities(sensors)

class DHT11Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        super().__init__(
            hass,
            _LOGGER,
            name="DHT11 Sensor",
            update_interval=timedelta(seconds=60)
        )
        self.config = config
        self.session = aiohttp.ClientSession()

    async def _async_update_data(self):
        try:
            url = f"http://{self.config['host']}:{self.config['port']}{self.config['path']}"
            async with async_timeout.timeout(5):
                async with self.session.get(url) as response:
                    data = await response.json()
                    return {
                        "temperature": data.get("temperature"),
                        "humidity": data.get("humidity")
                    }
        except Exception as e:
            _LOGGER.error("Error fetching data: %s", e)
            raise

class DHT11Sensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, config):
        super().__init__(coordinator)
        self._config = config

    @property
    def device_info(self):
        return {
            "identifiers": {("dht11_sensor", self._config["host"])},
            "name": f"DHT11 {self._config['host']}",
            "manufacturer": "DIY",
            "model": "ESP8266 DHT11"
        }

class DHT11TemperatureSensor(DHT11Sensor):
    @property
    def unique_id(self):
        return f"dht11_{self._config['host']}_temperature"

    @property
    def name(self):
        return f"DHT11 {self._config['host']} Temperature"

    @property
    def native_value(self):
        return self.coordinator.data.get("temperature")

    @property
    def native_unit_of_measurement(self):
        return "°C"

class DHT11HumiditySensor(DHT11Sensor):
    @property
    def unique_id(self):
        return f"dht11_{self._config['host']}_humidity"

    @property
    def name(self):
        return f"DHT11 {self._config['host']} Humidity"

    @property
    def native_value(self):
        return self.coordinator.data.get("humidity")

    @property
    def native_unit_of_measurement(self):
        return "%"