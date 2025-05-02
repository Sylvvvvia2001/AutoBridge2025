"""Constants for the Temperature & Humidity Sensor integration."""
from homeassistant.const import Platform

DOMAIN = "temp_humid_sensor"

# 默认设备配置
DEFAULT_HOST = "http://192.168.137.60"
DEFAULT_PORT = 80
DEFAULT_PATH = "/data"
DEFAULT_NAME = "Temperature & Humidity Sensor"
DEFAULT_SCAN_INTERVAL = 60  # seconds

# 配置项
CONF_HOST = "host"
CONF_PORT = "port"
CONF_PATH = "path"

# 支持的平台
PLATFORMS = [Platform.SENSOR]

# 设备信息
MANUFACTURER = "Sensor Manufacturer"
MODEL = "Temperature & Humidity Sensor v1.0"


CONF_ERROR_CANNOT_CONNECT = "cannot_connect"
CONF_ERROR_INVALID_DATA = "invalid_data" 