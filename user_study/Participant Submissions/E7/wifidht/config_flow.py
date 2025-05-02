"""用户在 UI / YAML 中填写主机地址等信息的入口。"""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_PATH, DEFAULT_PORT, DEFAULT_PATH


class DHTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """配置向导。"""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=f"Wi‑Fi DHT @ {user_input[CONF_HOST]}",
                data={
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
                    CONF_PATH: user_input.get(CONF_PATH, DEFAULT_PATH),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="192.168.137.60"): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_PATH, default=DEFAULT_PATH): str,
                }
            ),
        )

    # 配置完成后允许在「设备 → 选项」里面改轮询间隔
    async def async_step_init(self, _user_input=None):
        return await self.async_step_user()