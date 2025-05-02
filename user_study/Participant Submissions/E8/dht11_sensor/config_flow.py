# custom_components/dht11_sensor/config_flow.py
import voluptuous as vol
import aiohttp
import json
from homeassistant import config_entries

DEFAULT_HOST = "192.168.137.60"
DEFAULT_PORT = 80
DEFAULT_PATH = "/data"

class DHT11ConfigFlow(config_entries.ConfigFlow, domain="dht11_sensor"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                url = f"http://{user_input['host']}:{user_input['port']}{user_input['path']}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as response:
                        data = await response.json()
                        if "temperature" not in data or "humidity" not in data:
                            errors["base"] = "invalid_data"
                        else:
                            return self.async_create_entry(
                                title=f"DHT11 {user_input['host']}",
                                data=user_input
                            )
            except (aiohttp.ClientError, json.JSONDecodeError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default=DEFAULT_HOST): str,
                vol.Required("port", default=DEFAULT_PORT): int,
                vol.Required("path", default=DEFAULT_PATH): str,
            }),
            errors=errors
        )