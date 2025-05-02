"""Constants for the Temp Humidity Sensor integration."""
DOMAIN = "temp_humidity_sensor"

DEFAULT_HOST = "http://192.168.137.60"
DEFAULT_PORT = 80
DEFAULT_PATH = "/data"

# Sensor types
SENSOR_TEMPERATURE = "temperature"
SENSOR_HUMIDITY = "humidity"

# Sensor names
SENSOR_NAMES = {
    SENSOR_TEMPERATURE: "Temperature",
    SENSOR_HUMIDITY: "Humidity",
}

# Sensor units
SENSOR_UNITS = {
    SENSOR_TEMPERATURE: "°C",
    SENSOR_HUMIDITY: "%",
} 