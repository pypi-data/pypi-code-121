"""Define an API endpoint manager for Sonic data & actions."""
from __future__ import annotations

from typing import Awaitable, Callable, Optional

from herolabsapi import SONICS_RESOURCE, SONICS_WIFI_RESOURCE


class Sonic:
    """Define the sonic manager object."""

    def __init__(self, async_request: Callable[..., Awaitable]) -> None:
        """Initialize."""
        self._async_request: Callable[..., Awaitable] = async_request

    async def async_get_all_sonic_details(self) -> dict:
        """Return the list of sonic devices."""
        return await self._async_request("get", SONICS_RESOURCE)

    async def async_get_total_sonics(self) -> str:
        """Return the number of sonic devices."""
        data = await self._async_request("get", SONICS_RESOURCE)
        return data["total_entries"]

    async def async_get_sonic_details(self, sonic_id: str) -> dict:
        """this sends a request to get the details of a specified sonic device"""
        sonic_id_url = f"{SONICS_RESOURCE}{sonic_id}"
        return await self._async_request("get", sonic_id_url)

    async def async_get_sonic_wifi(self) -> dict:
        """Should return the sonic wi-fi info, valid response received but no device data returned."""
        return await self._async_request("get", SONICS_WIFI_RESOURCE)

    async def async_update_sonic_name(self, sonic_id: str, sonic_name: str) -> None:
        """Update the sonic device. Name is the only value that can be updated at this endpoint"""
        sonic_id_url = f"{SONICS_RESOURCE}{sonic_id}"
        return await self._async_request("put", sonic_id_url, json={"name": f"{sonic_name}"})

    async def async_sonic_telemetry_by_id(self, sonic_id: str) -> dict:
        """A telemetry object contains the latest telemetry details from a Sonic such as pressure, temperature etc."""
        sonic_id_url = f"{SONICS_RESOURCE}{sonic_id}/telemetry"
        return await self._async_request("get", sonic_id_url)

    async def async_open_sonic_valve(self, sonic_id: str) -> None:
        """Open Sonic Valve by calling a specified sonic_id"""
        sonic_id_url = f"{SONICS_RESOURCE}{sonic_id}/valve"
        return await self._async_request("put", sonic_id_url, json={"action": "open"})

    async def async_close_sonic_valve(self, sonic_id: str) -> None:
        """Close Sonic Valve by calling a specified sonic_id"""
        sonic_id_url = f"{SONICS_RESOURCE}{sonic_id}/valve"
        return await self._async_request("put", sonic_id_url, json={"action": "close"})
