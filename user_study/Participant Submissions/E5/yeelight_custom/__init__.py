from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.helpers.discovery.load_platform('light', 'yeelight_custom', {}, config)
    return True