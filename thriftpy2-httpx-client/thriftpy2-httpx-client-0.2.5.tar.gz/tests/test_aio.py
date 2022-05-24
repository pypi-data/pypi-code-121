from numbers import Real

from urllib3.exceptions import ReadTimeoutError

import pytest

import httpx

from thriftpy2.thrift import TApplicationException
from thriftpy2.contrib.aio.client import TAsyncClient

from thriftpy2_httpx_client.aio import make_client

import addressbook_thrift  # noqa

try:
    from contextlib import asynccontextmanager
except ImportError:
    from async_generator import asynccontextmanager


@asynccontextmanager
async def client(timeout: Real = 3) -> TAsyncClient:
    c = await make_client(
        addressbook_thrift.AddressBookService,
        host="127.0.0.1",
        port=6080,
        timeout=timeout,
    )
    try:
        yield c
    finally:
        c.close()


@asynccontextmanager
async def client_with_url(timeout: Real = 3) -> TAsyncClient:
    c = await make_client(
        addressbook_thrift.AddressBookService,
        url="http://127.0.0.1:6080",
        timeout=timeout,
    )
    try:
        yield c
    finally:
        c.close()


@pytest.mark.asyncio
async def test_client_host_port_vs_url():
    async with client() as c1, client_with_url() as c2:
        assert await c1.hello("world") == await c2.hello("world")


@pytest.mark.asyncio
async def test_void_api():
    async with client() as c:
        assert await c.ping() is None


@pytest.mark.asyncio
async def test_string_api():
    async with client() as c:
        assert await c.hello("world") == "hello world"


@pytest.mark.asyncio
async def test_required_argument():
    async with client() as c:
        with pytest.raises(TApplicationException):
            await c.hello()

        assert await c.hello(name="") == "hello "


@pytest.mark.asyncio
async def test_huge_res():
    async with client() as c:
        big_str = "world" * 10000
        assert await c.hello(big_str) == f"hello {big_str}"


@pytest.mark.asyncio
async def test_tstruct_req(person):
    async with client() as c:
        assert await c.add(person) is True


@pytest.mark.asyncio
async def test_tstruct_res(person):
    async with client() as c:
        assert person == await c.get("Alice")


@pytest.mark.asyncio
async def test_complex_tstruct():
    async with client() as c:
        assert len(await c.get_phonenumbers("Alice", 0)) == 0
        assert len(await c.get_phonenumbers("Alice", 1000)) == 1000


@pytest.mark.asyncio
async def test_exception():
    with pytest.raises(addressbook_thrift.PersonNotExistsError):
        async with client() as c:
            await c.remove("Bob")


@pytest.mark.asyncio
async def test_client_timeout():
    with pytest.raises((httpx.ReadTimeout, ReadTimeoutError)):
        async with client(timeout=0.1) as c:
            await c.sleep(400)
