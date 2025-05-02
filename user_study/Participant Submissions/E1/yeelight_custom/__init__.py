"""Yeelight LED Bulb 1S (Color) integration."""
import logging

import voluptuous as vol

from homeassistant.const import CONF_DEVICES, CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import load_platform

DOMAIN = "yeelight_custom"
_LOGGER = logging.getLogger(__name__)

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    """Set up the Yeelight component."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    devices = conf[CONF_DEVICES]
    
    hass.data[DOMAIN] = {}
    
    for device_conf in devices:
        host = device_conf[CONF_HOST]
        name = device_conf.get(CONF_NAME, f"Yeelight {host}")
        
        hass.data[DOMAIN][host] = {
            "host": host,
            "name": name,
        }
    
    load_platform(hass, "light", DOMAIN, {}, config)
    
    return True 