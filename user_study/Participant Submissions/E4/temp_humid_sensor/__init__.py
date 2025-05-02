"""The Temperature Humidity Sensor integration."""
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_PATH,
    DEFAULT_NAME,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PATH,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Required(CONF_HOST, default=DEFAULT_HOST): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_PATH, default=DEFAULT_PATH): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Temperature Humidity Sensor component."""
    if DOMAIN not in config:
        return True

    hass.data.setdefault(DOMAIN, {})
    conf = config[DOMAIN]
    
    # Store configuration
    hass.data[DOMAIN] = conf

    # Set up platforms
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(
            Platform.SENSOR, DOMAIN, conf, config
        )
    )
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Temperature Humidity Sensor from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Convert the config entry to the format expected by the platform
    platform_config = {
        CONF_NAME: entry.data.get(CONF_NAME, DEFAULT_NAME),
        CONF_HOST: entry.data.get(CONF_HOST, DEFAULT_HOST),
        CONF_PORT: entry.data.get(CONF_PORT, DEFAULT_PORT),
        CONF_PATH: entry.data.get(CONF_PATH, DEFAULT_PATH),
    }
    
    hass.data[DOMAIN][entry.entry_id] = platform_config

    # Set up platform using async_setup_platform
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(
            Platform.SENSOR, DOMAIN, platform_config, {}
        )
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove the config entry data
    hass.data[DOMAIN].pop(entry.entry_id, None)
    
    # The platform will handle cleanup of entities
    return True 