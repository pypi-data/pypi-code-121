"""Define an API endpoint manager for Signals data & actions."""
from __future__ import annotations

from datetime import datetime
from typing import Awaitable, Callable, Optional

from herolabsapi import SIGNALS_RESOURCE, PROPERTIES_RESOURCE


class Signals:
    """Define the signal manager object.
    A signal object is a representation of a Signal device (sometimes called hub)
    that communicates with Wi-Fi and Sonic (a valve installed on a pipe)."""

    def __init__(self, async_request: Callable[..., Awaitable]) -> None:
        """Initialize."""
        self._async_request: Callable[..., Awaitable] = async_request

    async def async_get_total_signals(self) -> str:
        """Return the number of signal devices."""
        data = await self._async_request("get", SIGNALS_RESOURCE)
        return data["total_entries"]

    async def async_get_signal_details(self) -> dict:
        """Return the list of Signal devices."""
        return await self._async_request("get", SIGNALS_RESOURCE)

    async def async_get_signal_details(self, signal_id: str) -> dict:
        """this sends a request to get the details of a specified signal device"""
        signal_id_url = f"{SIGNALS_RESOURCE}{signal_id}"
        return await self._async_request("get", signal_id_url)

    async def async_get_signal_details_by_property_id(self, property_id: str) -> dict:
        """this sends a request to get the details of signal devices registered to a specified property"""
        property_signals_url = f"{PROPERTIES_RESOURCE}{property_id}/signals"
        return await self._async_request("get", property_signals_url)

    async def async_update_signal_details(self, signal_id: str, signal_name: str) -> dict:
        """this sends a request to update the name of the specified signal device
        name is the only value that can be updated at this endpoint"""
        signal_id_url = f"{SIGNALS_RESOURCE}{signal_id}"
        return await self._async_request("put", signal_id_url, json={"name": f"{signal_name}"})
