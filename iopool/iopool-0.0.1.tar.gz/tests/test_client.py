from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pytest

import iopool

from iopool.const import ROUTES
from iopool.types import Pool, Advice, Measure, PoolMode, MeasureMode

if TYPE_CHECKING:
    from respx import MockRouter


MOCK_POOLS: list[Pool] = [
    MOCK_STANDARD_POOL := Pool(
        id="standard-pool",
        title="Standard Pool",
        mode=PoolMode.STANDARD,
        advice=Advice(filtrationDuration=8.5),
        hasAnActionRequired=False,
        latestMeasure=Measure(
            ecoId="standard-eco",
            isValid=True,
            measuredAt="2022-05-15T14:54:00.000",
            mode=MeasureMode.standard,
            orp=660,
            ph=7.1989619377162635,
            temperature=22.13634603251586,
        ),
    ),
    MOCK_WINTER_POOL := Pool(
        id="winter-pool",
        title="Winter Pool",
        mode=PoolMode.WINTER,
        advice=Advice(filtrationDuration=3.5),
        hasAnActionRequired=False,
        latestMeasure=Measure(
            ecoId="winter-eco",
            isValid=True,
            measuredAt="2021-10-16T13:41:00.000",
            mode=MeasureMode.standard,
            orp=637,
            ph=7.216262975778547,
            temperature=12.799624711754063,
        ),
    ),
]


@pytest.mark.asyncio
async def test_pools(get, respx_mock: MockRouter):
    respx_mock.get(ROUTES.url_for("pools")).respond(json=MOCK_POOLS)

    pools = await get("pools")
    assert len(pools) == 2
    assert pools[0]["title"] == "Standard Pool"


@pytest.mark.asyncio
async def test_pool(get, respx_mock: MockRouter):
    POOL_ID = "fake-pool-id"
    respx_mock.get(ROUTES.url_for("pool", pool_id=POOL_ID)).respond(json=MOCK_STANDARD_POOL)

    pool = await get("pool", POOL_ID)
    assert pool["title"] == "Standard Pool"
