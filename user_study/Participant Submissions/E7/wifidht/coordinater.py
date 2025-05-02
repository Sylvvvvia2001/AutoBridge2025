"""负责从设备轮询数据的 DataUpdateCoordinator。"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_HOST,
    CONF_PORT,
    CONF_PATH,
    CONF_INTERVAL,
    DEFAULT_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class DHTDataUpdateCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """轮询 ESP 板返回的 JSON 数据，形如 {"temperature":25.3,"humidity":58}. """

    def __init__(self, hass: HomeAssistant, entry):
        self._entry = entry
        update_interval = timedelta(
            seconds=entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL)
        )
        super().__init__(
            hass,
            _LOGGER,
            name="Wi‑Fi DHT11 coordinator",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, float]:
        """向 http://host:port/path 取数据。"""
        host = self._entry.data[CONF_HOST]
        port = self._entry.data[CONF_PORT]
        path = self._entry.data[CONF_PATH]

        url = f"http://{host}:{port}{path}"
        _LOGGER.debug("Fetching DHT data from %s", url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status}")
                    data = await resp.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(err) from err

        # 期望拿到 "temperature" 与 "humidity" 字段
        if not {"temperature", "humidity"} <= data.keys():
            raise UpdateFailed(f"Missing keys in response: {data}")

        return data

    async def async_send_oled_text(self, text: str) -> None:
        """可选：把文字发到 OLED。设备需自行实现 /display?text=xxx API。"""
        host = self._entry.data[CONF_HOST]
        port = self._entry.data[CONF_PORT]
        url = f"http://{host}:{port}/display"
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={"text": text}, timeout=5)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.warning("Failed to send text to OLED: %s", err)