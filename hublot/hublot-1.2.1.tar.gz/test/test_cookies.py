#!/usr/bin/env python3

# hublot
from hublot import Client


def test_cookies_are_saved(client, server):
    assert client.get(f'{server}/cookies/get').json() == {}
    client.get(f'{server}/cookies/set?coo=kie')
    assert client.get(f'{server}/cookies/get').json() == {'coo': 'kie'}


def test_cookies_are_available_via_client(cache, server):
    for _ in (1, 2):
        client = Client(cache=cache)  # keep cache, clear cookies
        client.get(f'{server}/cookies/set?coo=kie')
        assert dict(client.cookies) == {'coo': 'kie'}


def test_cookies_are_available_via_session(cache, server):
    for _ in (1, 2):
        client = Client(cache=cache)  # keep cache, clear cookies
        client.get(f'{server}/cookies/set?coo=kie')
        assert dict(client.session.cookies) == {'coo': 'kie'}


def test_cookies_are_available_via_response(cache, server):
    for _ in (1, 2):
        client = Client(cache=cache)  # keep cache, clear cookies
        response = client.get(f'{server}/cookies/set?coo=kie')
        assert dict(response.cookies) == {'coo': 'kie'}


def test_cookies_are_set_when_running_from_cache(reinstantiable_client, server):
    for _ in (1, 2):
        client = reinstantiable_client()
        assert client.get(f'{server}/cookies/get').json() == {}
        client.get(f'{server}/cookies/set?coo=kie')
        assert client.get(f'{server}/cookies/get').json() == {'coo': 'kie'}


def test_cached_redirects(cache, server):
    for _ in (1, 2):
        client = Client(cache=cache)
        client.get(f'{server}/redirect/chain/1')
        cookies = {c.name: c.value for c in client.session.cookies}
        assert cookies == {'redirect1': 'yes', 'redirect2': 'yes', 'redirect3': 'yes'}


def test_cookies_can_be_disabled(cache, server):
    for _ in (1, 2):
        client = Client(cache=cache, cookies_enabled=False)
        assert client.get(f'{server}/cookies/get').json() == {}
        client.get(f'{server}/cookies/set?coo=kie')
        assert client.get(f'{server}/cookies/get').json() == {}


def test_multiple_cookies_headers(reinstantiable_client, server):
    for reading_from_cache in (False, True):
        client = reinstantiable_client()
        response = client.get(f'{server}/cookies/set-two-cookies')
        if not reading_from_cache:
            # Check that the mock server returns cookies in 2 separate headers, else this test isn't testing what it meant to test.
            # Can't run this test on the second iteration, because we don't have `response.raw` when coming from cache.
            response_cookies = sorted(
                (key, value)
                for key, value in response.raw.headers.items()
                if key == 'Set-Cookie'
            )
            assert response_cookies == [('Set-Cookie', 'a=1'), ('Set-Cookie', 'b=2')]
        assert sorted(response.cookies.items()) == [('a', '1'), ('b', '2')]
        assert sorted(client.session.cookies.items()) == [('a', '1'), ('b', '2')]


def test_response_that_redirects_to_same_url_with_cookie(client, server):
    assert client.get(f'{server}/self-redirect').text == 'ok'


def test_set_cookie_manually(client, server):
    client.cookies.set('x', '1')
    assert client.get(f'{server}/cookies/get').json() == {'x': '1'}
