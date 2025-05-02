"""Config flow for Temperature & Humidity Sensor integration."""
import logging
import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PATH,
    DEFAULT_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_PATH,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_PATH, default=DEFAULT_PATH): str,
    }
)


async def validate_input(hass: HomeAssistant, data):
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    path = data[CONF_PATH]
    
    # 确保主机地址格式正确
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    
    url = f"{host}:{port}{path}"
    
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                raise CannotConnect(f"Error connecting to the sensor: {response.status}")
            
            # 尝试解析响应以确保它是有效的
            response_data = await response.text()
            _LOGGER.debug("Received data: %s", response_data)
            
            # 这里可以添加更多的响应验证逻辑
            if not response_data:
                raise InvalidData("Received empty response from sensor")
                
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Error connecting to the sensor: {err}")
    
    # 返回要存储在配置条目中的信息
    return {"title": DEFAULT_NAME}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Temperature & Humidity Sensor."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # 检查是否已经配置了这个设备
                await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidData:
                errors["base"] = "invalid_data"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
                
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidData(HomeAssistantError):
    """Error to indicate invalid data was received."""