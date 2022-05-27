#!/usr/bin/env python3

# standards
from datetime import timedelta
from pathlib import Path

# 3rd parties
import pytest
from requests import Response

# hublot
from hublot import Client
from hublot.cache.storage import DiskStorage
from hublot.logs import LogEntry
from .utils import assert_responses_equal, dummy_prepared_request, dummy_response


def iter_pairs(client):
    for url in ('http://one/', 'http://two/'):
        for method, body in [('GET', None), ('POST', b'dummy body')]:
            for headers in ({}, {'X-Test': '1'}, {'X-Test': '2'}):
                # NB there's more comprehensive tests for cache key equivalent in `test_cache_keys.py`, but here's a sample
                request_kwargs = {'url': url, 'method': method, 'headers': headers, 'data': body}
                preq = dummy_prepared_request(client, **request_kwargs)
                res = dummy_response(preq)
                yield request_kwargs, res


def test_cache(reinstantiable_client):
    client = reinstantiable_client()
    pairs = [
        (dummy_prepared_request(client, **req), res)
        for req, res in iter_pairs(client)
    ]
    log_entries = [
        LogEntry(preq)
        for preq, _res_unused in pairs
    ]
    cache = client.cache
    for (preq, _res_unused), log in zip(pairs, log_entries):
        assert cache.get(preq, log) is None  # else test is invalid
        assert log.cached is False
    for (preq, res), log in zip(pairs, log_entries):
        cache.put(preq, log, res)
    cache = reinstantiable_client().cache
    for (preq, res), log in zip(pairs, log_entries):
        assert_responses_equal(cache.get(preq, log), res)
        assert log.cached is True


def test_client_caching(mocker, reinstantiable_client):
    client = reinstantiable_client()
    for req, res in iter_pairs(client):
        request = mocker.patch.object(client.session, 'request', return_value=res)
        assert_responses_equal(client.fetch(**req), res)
        request.assert_called_once()
    client = reinstantiable_client()
    for req, res in iter_pairs(client):
        request = mocker.patch.object(client.session, 'request', return_value=res)
        assert_responses_equal(client.fetch(**req), res)
        request.assert_not_called()


def test_http_errors_are_cached(client, server):
    one = client.get(f'{server}/fail-with-random-value', raise_for_status=False)
    assert one.status_code == 500
    two = client.get(f'{server}/fail-with-random-value', raise_for_status=False)
    assert two.status_code == 500
    three = client.get(f'{server}/fail-with-random-value', raise_for_status=False, force_cache_stale=True)
    assert three.status_code == 500
    assert one.text == two.text
    assert two.text != three.text


def test_repeated_http_headers_are_cached(reinstantiable_client, server):
    client = reinstantiable_client()
    res = client.get(f'{server}/cookies/set-two-cookies')
    assert res.headers.get('Set-Cookie') == 'a=1, b=2'
    assert res.raw._fp.headers.get_all('Set-Cookie') == ['a=1', 'b=2']   # pylint: disable=protected-access
    unique = res.text

    client = reinstantiable_client()
    res = client.get(f'{server}/cookies/set-two-cookies')
    assert res.text == unique  # check that it was cached
    assert res.headers.get('Set-Cookie') == 'a=1, b=2'
    #if callable(getattr(res.headers, 'get_all', None)):
    assert res.headers.get_all('Set-Cookie') == ['a=1', 'b=2']

    assert [f'{c.name}={c.value!r}' for c in client.session.cookies] == ["a='1'", "b='2'"]


def test_cache_wont_save_body_with_wrong_length(client):
    preq = dummy_prepared_request(
        client,
        data=b'More than one byte',
    )
    preq.headers['Content-Length'] = '1'
    response = Response()
    response.request = preq
    with pytest.raises(Exception) as ex:
        client.cache.put(preq, LogEntry(preq), response)
    assert 'body has 18 bytes but Content-Length is 1' in str(ex)


def test_cache_wont_save_get_request_with_content_length(client):
    preq = dummy_prepared_request(
        client,
        method='GET',
    )
    preq.headers['Content-Length'] = '999'
    response = Response()
    response.request = preq
    with pytest.raises(Exception) as ex:
        client.cache.put(preq, LogEntry(preq), response)
    assert 'body has 0 bytes but Content-Length is 999' in str(ex)


def test_cache_can_handle_empty_post_request(client, server):
    for _from_cache_unused in (False, True):
        res = client.fetch(f'{server}/echo', data={})
        obtained = res.json()
        obtained.pop('headers')
        assert obtained == {'method': 'POST', 'args': {}, 'files': {}, 'form': {}, 'json': None}


def test_cant_pass_cache_kwargs_and_preinstantiated_cache(cache):
    with pytest.raises(Exception) as ex:
        Client(cache=cache, max_cache_age=timedelta(10))
    assert "can't specify a max_age" in str(ex)


def test_cache_can_be_specified_as_path():
    client = Client(cache=Path('/cache'))
    assert isinstance(client.cache.storage, DiskStorage)
    assert client.cache.storage.root_path == Path('/cache')


def test_cache_cannot_be_specified_as_str():
    # The idea of not accepting strings is mostly to just keep the client code readable, and maybe preserve forward flexibility.
    # But if this ever a problem, we could consider auto-converting str objects to Path objects.
    with pytest.raises(ValueError):
        Client(cache='/cache')


def test_from_cache_attribute(client, server):
    for from_cache in (False, True):
        res = client.fetch(f'{server}/hello')
        assert res.from_cache == from_cache


def test_cache_can_handle_empty_http_reason(client, server):
    for _from_cache_unused in (False, True):
        res = client.fetch(f'{server}/no-reason')
        assert res.reason == ''
        assert res.text == 'hello'
