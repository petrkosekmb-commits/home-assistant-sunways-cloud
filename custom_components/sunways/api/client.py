"""Simple Http client for Sunways REST User API."""

from typing import Any, NamedTuple

from aiohttp.client import ClientSession

from .connection import (
    API_DEVICE_INFO,
    API_DEVICE_LIST,
    API_STATION_LIST,
    API_STATION_OVERVIEW,
    SunwaysApiConnection,
    TokenJar,
)


class SunwaysStation(NamedTuple):
    """Identifies a station registered for the user at sunways."""

    name: str
    id: str


class SunwaysClient:
    """
    Simple client for Sunways API
    """

    def __init__(self, email: str, password: str, websession: ClientSession, token_jar: TokenJar | None = None):
        self._api = SunwaysApiConnection(email, password, websession, token_jar)

    async def __aenter__(self):
        await self._api.__aenter__()
        return self

    async def __aexit__(self, *args) -> bool:
        """Call when the client is disposed."""
        # Close the web session, if we created it (i.e. it was not passed in)
        return await self._api.__aexit__(*args)

    async def get_stations(self) -> list[SunwaysStation]:
        """Get the availabile stations."""
        result = await self._api.request("get", API_STATION_LIST)

        stations = [SunwaysStation(s["name"], s["id"]) for s in result["records"]]
        return stations

    async def get_station_overview(self, station_id: str) -> dict[str, Any]:
        """Get the overview of a single station."""
        result = await self._api.request("get", API_STATION_OVERVIEW, {"id": station_id})

        if not isinstance(result, dict):
            raise TypeError("Unexpected station overview response")
        return result

    async def get_station_history(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get timestamped values for one station."""
        result = await self._api.request(
            "get",
            "/monitor/core/power/station/overview/getGridConnectedData",
            params=params,
        )
        if not isinstance(result, dict):
            raise TypeError("Unexpected station history response")
        return result

    async def get_devices(self, station_id: str) -> list[dict[str, Any]]:
        """Return devices assigned to a station."""
        result = await self._api.request("get", f"{API_DEVICE_LIST}{station_id}")
        if isinstance(result, dict):
            result = result.get("records", result.get("list", result.get("content")))
        if not isinstance(result, list):
            raise TypeError("Unexpected device list response")
        return [device for device in result if isinstance(device, dict) and device.get("id") is not None]

    async def get_device_info(self, device_id: str) -> dict[str, Any]:
        """Return details and runtime values for one device."""
        result = await self._api.request("get", API_DEVICE_INFO, params={"id": device_id})
        if not isinstance(result, dict):
            raise TypeError("Unexpected device info response")
        return result
