"""Sunways cloud integration."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api.client import SunwaysClient
from .config_flow import create_sunways_client
from .coordinator import SunwaysDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]


@dataclass(slots=True)
class SunwaysRuntimeData:
    client: SunwaysClient
    coordinator: SunwaysDataUpdateCoordinator


type SunwaysConfigEntry = ConfigEntry[SunwaysRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: SunwaysConfigEntry) -> bool:
    client = create_sunways_client(hass, entry.data)
    coordinator = SunwaysDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = SunwaysRuntimeData(client, coordinator)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SunwaysConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: SunwaysConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
