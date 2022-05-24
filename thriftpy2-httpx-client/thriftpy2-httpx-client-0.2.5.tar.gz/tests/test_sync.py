from numbers import Real
from contextlib import contextmanager

from urllib3.exceptions import ReadTimeoutError

import pytest

import httpx

from thriftpy2.thrift import TApplicationException, TClient

from thriftpy2_httpx_client.sync import make_client

import addressbook_thrift  # noqa


@contextmanager
def client(timeout: Real = 3) -> TClient:
    c = make_client(
        addressbook_thrift.AddressBookService,
        host="127.0.0.1",
        port=6080,
        timeout=timeout,
    )
    try:
        yield c
    finally:
        c.close()


@contextmanager
def client_with_url(timeout: Real = 3) -> TClient:
    c = make_client(
        addressbook_thrift.AddressBookService,
        url="http://127.0.0.1:6080",
        timeout=timeout,
    )
    try:
        yield c
    finally:
        c.close()


def test_client_host_port_vs_url():
    with client() as c1, client_with_url() as c2:
        assert c1.hello("world") == c2.hello("world")


def test_void_api():
    with client() as c:
        assert c.ping() is None


def test_string_api():
    with client() as c:
        assert c.hello("world") == "hello world"


def test_required_argument():
    with client() as c:
        with pytest.raises(TApplicationException):
            c.hello()

        assert c.hello(name="") == "hello "


def test_huge_res():
    with client() as c:
        big_str = "world" * 10000
        assert c.hello(big_str) == f"hello {big_str}"


def test_tstruct_req(person):
    with client() as c:
        assert c.add(person) is True


def test_tstruct_res(person):
    with client() as c:
        assert person == c.get("Alice")


def test_complex_tstruct():
    with client() as c:
        assert len(c.get_phonenumbers("Alice", 0)) == 0
        assert len(c.get_phonenumbers("Alice", 1000)) == 1000


def test_exception():
    with pytest.raises(addressbook_thrift.PersonNotExistsError):
        with client() as c:
            c.remove("Bob")


def test_client_timeout():
    with pytest.raises((httpx.ReadTimeout, ReadTimeoutError)):
        with client(timeout=0.1) as c:
            c.sleep(400)
