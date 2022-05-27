from __future__ import annotations
from dataclasses import dataclass

from typing import TYPE_CHECKING, Any

import pytest

import iopool


async def std_client(route: str, *args, **kwargs) -> Any:
    return getattr(iopool.Client("api-key"), route)(*args, **kwargs)


async def async_client(route: str, *args, **kwargs) -> Any:
    return await getattr(iopool.AsyncClient("api-key"), route)(*args, **kwargs)


@pytest.fixture(params=[std_client, async_client])
def get(request) -> Any:
    return request.param
