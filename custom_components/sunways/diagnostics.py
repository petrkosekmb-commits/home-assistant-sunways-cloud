"""Diagnostics for Sunways."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import SunwaysConfigEntry

TO_REDACT = {"email", "password", "initial_token", "station_id"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: SunwaysConfigEntry) -> dict[str, Any]:
    """Return redacted configuration and coordinator quality metadata."""
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "update_success": entry.runtime_data.coordinator.last_update_success,
        "quality": async_redact_data(entry.runtime_data.coordinator.data.get("quality", {}), TO_REDACT),
        "available_sensor_keys": sorted(entry.runtime_data.coordinator.data.get("sensors", {})),
    }
