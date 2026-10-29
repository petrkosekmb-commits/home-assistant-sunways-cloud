"""Coordinated polling for Sunways stations."""

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api.client import SunwaysClient
from .api.exceptions import LoginFailed, SunwaysClientException
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, HISTORY_INTERVAL
from .device import normalize_device
from .history import history_payload, parse_history
from .quality import normalize_overview

_LOGGER = logging.getLogger(__name__)


class SunwaysDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: SunwaysClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"Sunways {entry.title}",
            update_interval=timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
        )
        self.client, self.station_id = client, entry.data["station_id"]
        self._history_next, self._history_data, self._history_error = 0.0, None, None
        self._device_list: list[dict[str, Any]] | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(15):
                raw = await self.client.get_station_overview(self.station_id)
            sensors, quality = normalize_overview(raw)
        except LoginFailed as err:
            raise ConfigEntryAuthFailed from err
        except (TimeoutError, SunwaysClientException, TypeError, ValueError, KeyError) as err:
            raise UpdateFailed(f"Sunways response unavailable or invalid: {err}") from err
        if time.monotonic() >= self._history_next:
            self._history_next = time.monotonic() + HISTORY_INTERVAL.total_seconds()
            try:
                async with asyncio.timeout(20):
                    self._history_data = await self.client.get_station_history(
                        history_payload(self.station_id, raw.get("runType"), dt_util.now())
                    )
                self._history_error = None
            except (TimeoutError, SunwaysClientException, TypeError, ValueError, KeyError):
                self._history_data, self._history_error = None, "query_failed"
        history = parse_history(self._history_data, dt_util.utcnow())
        if self._history_error:
            history["history_status"] = self._history_error
        sensors.update(history)
        sensors["cloud_received_at"] = dt_util.utcnow()
        devices = await self._async_update_devices()
        quality.update(
            {
                "history_status": history["history_status"],
                "history_sample_time": history["history_sample_time"],
                "history_poll_interval_seconds": int(HISTORY_INTERVAL.total_seconds()),
                "grid_sign": "positive_import_negative_export",
                "control_ready": False,
            }
        )
        return {"station_id": self.station_id, "sensors": sensors, "devices": devices, "quality": quality}

    async def _async_update_devices(self) -> list[dict[str, Any]]:
        """Fetch per-inverter details without failing the station overview."""
        try:
            async with asyncio.timeout(20):
                if self._device_list is None:
                    self._device_list = await self.client.get_devices(self.station_id)
                details = []
                for device in self._device_list:
                    info = await self.client.get_device_info(str(device["id"]))
                    details.append(normalize_device(device, info))
                return details
        except LoginFailed as err:
            raise ConfigEntryAuthFailed from err
        except (TimeoutError, SunwaysClientException, TypeError, ValueError, KeyError) as err:
            _LOGGER.debug("Sunways device details unavailable: %s", err)
            return []
