"""Wrapper for the WeatherBug Spark API."""
from __future__ import annotations

import aiohttp
from pydantic import BaseModel

from .util import _get_hmac_url


async def get_data(
    lat: str | float, lon: str | float, websession: aiohttp.ClientSession | None = None
) -> SparkResult:
    """Get data from WeatherBug Spark API."""
    if isinstance(lat, float):
        lat = str(lat)
    if isinstance(lon, float):
        lon = str(lon)
    url: str = _get_hmac_url(lat, lon)
    if websession is not None:
        async with websession.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"\nError: {resp.status}\n{await resp.text()}")
            data = await resp.json()
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"\nError: {resp.status}\n{await resp.text()}")
                data = await resp.json()

    SparkResult.update_forward_refs()
    return SparkResult(**data["result"])


class SparkResult(BaseModel):
    """Pydantic model for Spark API response."""

    pulseListAlert: list[LightningStrike]
    pulseListGlobal: list[LightningStrike]
    alertCode: int
    alertColor: str
    closestPulseDistance: float
    closestPulseDirection: float
    shortMessage: str
    safetyMessage: str


class LightningStrike(BaseModel):
    """Pydantic model for LightningStrike."""

    latitude: float
    longitude: float
    dateTimeUtc: int
    dateTimeUtcStr: str
    dateTimeLocalStr: str
