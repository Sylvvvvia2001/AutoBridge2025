import logging
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import TEMP_CELSIUS, CONF_NAME, CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_NAME, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_PATH

_LOGGER = logging.getLogger(__name__)

CONF_PATH = "path"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_PATH, default=DEFAULT_PATH): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config[CONF_NAME]
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    path = config[CONF_PATH]

    base_url = f"{host}:{port}{path}"

    add_entities([
        TemperatureSensor(name + " Temperature", base_url),
        HumiditySensor(name + " Humidity", base_url),
    ])

class TemperatureSensor(SensorEntity):
    def __init__(self, name, url):
        self._name = name
        self._url = url
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    def update(self):
        try:
            response = requests.get(self._url, timeout=5)
            data = response.json()
            self._state = data.get("temperature")
        except Exception as e:
            _LOGGER.error("Error updating temperature: %s", e)
            self._state = None

class HumiditySensor(SensorEntity):
    def __init__(self, name, url):
        self._name = name
        self._url = url
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return "%"

    def update(self):
        try:
            response = requests.get(self._url, timeout=5)
            data = response.json()
            self._state = data.get("humidity")
        except Exception as e:
            _LOGGER.error("Error updating humidity: %s", e)
            self._state = None