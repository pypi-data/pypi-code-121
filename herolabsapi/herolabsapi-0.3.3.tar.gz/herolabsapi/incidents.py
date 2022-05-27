"""Define an API endpoint manager for Incidents data & actions."""
from __future__ import annotations

from typing import Awaitable, Callable

from herolabsapi import INCIDENTS_RESOURCE, PROPERTIES_RESOURCE


class Incidents:
    """Define the incident manager object.
    An incident is created whenever the hero labs platform detects leakage, disconnection, low battery etc."""

    def __init__(self, async_request: Callable[..., Awaitable]) -> None:
        """Initialize."""
        self._async_request: Callable[..., Awaitable] = async_request

    async def async_get_incidents(self) -> dict:
        """Return the list of Incidents."""
        return await self._async_request("get", INCIDENTS_RESOURCE)

    async def async_get_open_incidents(self) -> dict:
        """Return the list of Open Incidents."""
        all_incidents = await self._async_request("get", INCIDENTS_RESOURCE)
        open_incidents = [v for v in all_incidents['data'] if v['open'] is True]
        open_incident_count = len([ele for ele in open_incidents if isinstance(ele, dict)])
        return open_incidents, open_incident_count

    async def async_get_incident_details(self, incident_id) -> dict:
        """Return the details on specified incident. (leakage detection, disconnection, low battery etc.)"""
        incident_id_url = f"{INCIDENTS_RESOURCE}{incident_id}"
        return await self._async_request("get", incident_id_url)

    async def async_get_incidents_by_property(self, property_id) -> dict:
        """Return the details of incidents on a specified property.
        (leakage detection, disconnection, low battery etc.)"""
        incident_id_url = f"{PROPERTIES_RESOURCE}{property_id}/incidents"
        return await self._async_request("get", incident_id_url)

    async def async_get_open_incidents_by_property(self, property_id) -> dict:
        """Return the details of incidents on a specified property.
        (leakage detection, disconnection, low battery etc.)"""
        incident_id_url = f"{PROPERTIES_RESOURCE}{property_id}/incidents"
        all_incidents = await self._async_request("get", incident_id_url)
        open_incidents = [v for v in all_incidents['data'] if v['open'] is True]
        open_incident_count = len([ele for ele in open_incidents if isinstance(ele, dict)])
        return open_incidents, open_incident_count

    async def async_close_incident(self, incident_id: str) -> str:
        """Close an incident"""
        incident_id_url = f"{INCIDENTS_RESOURCE}{incident_id}/action"
        await self._async_request("put", incident_id_url, json={"action": "dismiss"})
        return "Incident has been closed"

    async def async_reopen_incident(self, incident_id: str) -> str:
        """Reopen an incident"""
        incident_id_url = f"{INCIDENTS_RESOURCE}{incident_id}/action"
        await self._async_request("put", incident_id_url, json={"action": "reopen"})
        return "Incident has been reopened"
