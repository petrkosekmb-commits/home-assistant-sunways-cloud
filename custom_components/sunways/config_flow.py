"""Config and options flows for Sunways."""

import logging
import time
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api.client import SunwaysClient, SunwaysStation
from .api.connection import TokenJar
from .api.exceptions import ConnectionFailed, LoginFailed, SunwaysClientException
from .const import (
    CONF_INITIAL_TOKEN,
    CONF_SCAN_INTERVAL,
    CONF_STATION_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


def create_sunways_client(hass: HomeAssistant, data: Mapping[str, Any]) -> SunwaysClient:
    token = data.get(CONF_INITIAL_TOKEN)
    return SunwaysClient(
        data[CONF_EMAIL],
        data[CONF_PASSWORD],
        async_get_clientsession(hass),
        TokenJar(token, time.time()) if token else None,
    )


class SunwaysConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._stations: list[SunwaysStation] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors = {}
        if user_input is not None:
            try:
                self._stations = await create_sunways_client(self.hass, user_input).get_stations()
                if not self._stations:
                    errors["base"] = "no_stations_found"
                else:
                    self._data = user_input
                    return await self.async_step_station()
            except ConnectionFailed:
                errors["base"] = "cannot_connect"
            except LoginFailed:
                errors["base"] = "invalid_auth"
            except (SunwaysClientException, TimeoutError, KeyError, TypeError):
                errors["base"] = "unknown"
        schema = vol.Schema(
            {vol.Required(CONF_EMAIL): str, vol.Required(CONF_PASSWORD): str, vol.Optional(CONF_INITIAL_TOKEN): str}
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_station(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is None:
            selector = SelectSelector(
                SelectSelectorConfig(
                    options=[SelectOptionDict(value=s.id, label=s.name) for s in self._stations],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            )
            return self.async_show_form(
                step_id="station", data_schema=vol.Schema({vol.Required(CONF_STATION_ID): selector})
            )
        station_id = user_input[CONF_STATION_ID]
        await self.async_set_unique_id(station_id)
        self._abort_if_unique_id_configured()
        self._data.update(user_input)
        return self.async_create_entry(
            title=next(s.name for s in self._stations if s.id == station_id), data=self._data
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        self._data = dict(entry_data)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors = {}
        if user_input is not None:
            candidate = {**self._data, **user_input}
            candidate.pop(CONF_INITIAL_TOKEN, None)
            try:
                await create_sunways_client(self.hass, candidate).get_stations()
                return self.async_update_reload_and_abort(self._get_reauth_entry(), data=candidate)
            except LoginFailed:
                errors["base"] = "invalid_auth"
            except (SunwaysClientException, TimeoutError, KeyError, TypeError):
                errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {vol.Required(CONF_EMAIL, default=self._data.get(CONF_EMAIL)): str, vol.Required(CONF_PASSWORD): str}
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return SunwaysOptionsFlow()


class SunwaysOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        selector = NumberSelector(
            NumberSelectorConfig(
                min=MIN_SCAN_INTERVAL,
                max=MAX_SCAN_INTERVAL,
                step=10,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="s",
            )
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): selector
                }
            ),
        )
