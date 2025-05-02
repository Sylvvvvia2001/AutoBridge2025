import logging
import requests
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

DEFAULT_HOST = "http://192.168.137.60" 
DEFAULT_PORT = 80
DEFAULT_PATH = "/data" 

def setup_platform(hass, config, add_entities, discovery_info=None):

    host = config.get("host", DEFAULT_HOST)
    port = config.get("port", DEFAULT_PORT)
    path = config.get("path", DEFAULT_PATH)
    
    add_entities([ESP8266TemperatureHumiditySensor(host, port, path)], True)

class ESP8266TemperatureHumiditySensor(SensorEntity):

    def __init__(self, host, port, path):
        self._host = host
        self._port = port
        self._path = path
        self._temperature = None
        self._humidity = None
        self._name = "ESP8266 Temperature & Humidity Sensor"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._temperature

    @property
    def extra_state_attributes(self):
        return {
            "humidity": self._humidity
        }

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def device_class(self):
        return "temperature"

    @Throttle(SCAN_INTERVAL)
    def update(self):

        url = f"{self._host}:{self._port}{self._path}"
        try:
            response = requests.get(url)
            data = response.json()  
            self._temperature = data.get("temperature")
            self._humidity = data.get("humidity")
        except Exception as e:
            _LOGGER.error(f"Error fetching data from ESP8266: {e}")