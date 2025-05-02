# sensor.py
import logging
import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS, DEVICE_CLASS_HUMIDITY
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = "http://192.168.137.60"
DEFAULT_PORT = 80
DEFAULT_PATH = "/data"

class MyTempHumiditySensor(SensorEntity):
    """Representation of a Temp/Humidity sensor."""

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, path=DEFAULT_PATH):
        """Initialize the sensor."""
        self._host = host
        self._port = port
        self._path = path
        self._temperature = None
        self._humidity = None

    def update(self):
        """Fetch data from the sensor."""
        url = f"{self._host}:{self._port}{self._path}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self._temperature = data.get("temperature")
                self._humidity = data.get("humidity")
                _LOGGER.info("Successfully fetched data: Temperature: %s, Humidity: %s", self._temperature, self._humidity)
            else:
                _LOGGER.error("Failed to get data, status code: %d", response.status_code)
        except Exception as e:
            _LOGGER.error("Error fetching data from sensor: %s", e)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "My Temp and Humidity Sensor"

    @property
    def state(self):
        """Return the state of the sensor (temperature)."""
        return self._temperature

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement for the sensor."""
        return TEMP_CEL