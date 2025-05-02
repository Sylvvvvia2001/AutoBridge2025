import voluptuous as vol
from yeelight import Bulb
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_NAME

DATA_SCHEMA = vol.Schema({
    vol.Required("host"): str,
    vol.Optional("name", default=DEFAULT_NAME): str,
})

class YeelightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """配置流：让用户输入灯泡 IP 并校验连通性。"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input["host"]
            # 尝试通过 blocking I/O 获取属性，放到 executor 中
            try:
                bulb = Bulb(host)
                await self.hass.async_add_executor_job(bulb.get_properties)
                await self.hass.async_add_executor_job(bulb.close)
            except Exception:
                errors["host"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input["name"],
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors
        )