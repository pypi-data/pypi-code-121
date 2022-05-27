#!/usr/bin/env python3

# standards
from contextlib import contextmanager
from datetime import datetime, timedelta
import gzip
from itertools import count, product
from os import utime

# 3rd parties
import pytest


def _fetch_unique_number_then_move_clock_to_next_day(mocker, reinstantiable_client, server):
    now = datetime.now()
    client = reinstantiable_client()
    unique = client.get(f'{server}/unique-number').text
    mocker.patch('hublot.cache.storage.current_datetime', return_value=now + timedelta(days=1))
    return unique


def test_cache_max_age_defaults(mocker, reinstantiable_client, server):
    # no max_age specified, cache is still valid a day later
    unique = _fetch_unique_number_then_move_clock_to_next_day(mocker, reinstantiable_client, server)
    client = reinstantiable_client()
    assert unique == client.get(f'{server}/unique-number').text


def test_cache_long_max_age(mocker, reinstantiable_client, server):
    # max_age is 2 days, cache is still valid a day later
    unique = _fetch_unique_number_then_move_clock_to_next_day(mocker, reinstantiable_client, server)
    client = reinstantiable_client()
    assert unique == client.get(f'{server}/unique-number', max_cache_age=timedelta(days=2)).text


def test_cache_short_max_age(mocker, reinstantiable_client, server):
    # max_age is 12 hours, cache is no longer valid a day later, we get a new `unique` number
    unique = _fetch_unique_number_then_move_clock_to_next_day(mocker, reinstantiable_client, server)
    client = reinstantiable_client()
    assert unique != client.get(f'{server}/unique-number', max_cache_age=timedelta(hours=12)).text


def test_cache_pruning(mocker, reinstantiable_client, server):
    # client is created with max_age of 12 hours, and a request (of any URL) is run. The cache gets pruned.
    unique = _fetch_unique_number_then_move_clock_to_next_day(mocker, reinstantiable_client, server)
    client = reinstantiable_client(max_age=timedelta(hours=12))
    client.get(f'{server}/hello')
    # now it's no longer cached, we fetch a new `unique` number
    client = reinstantiable_client()
    assert unique != client.get(f'{server}/unique-number').text


def test_override_with_method_kwarg(mocker, reinstantiable_client, server):
    # instantiate cache with a max_age that would accept the cached file, but then call the get() method with a shorter age -- the
    # method kwarg overrides the constructor kwarg, cache is invalidated, a new value is fetched
    unique = _fetch_unique_number_then_move_clock_to_next_day(mocker, reinstantiable_client, server)
    client = reinstantiable_client(max_age=timedelta(days=10))
    assert unique != client.get(f'{server}/unique-number', max_cache_age=timedelta(hours=12)).text


def test_cant_override_with_longer_age(mocker, reinstantiable_client, server):
    # instantiate cache with a max_age that doesn't accept the cached file. Try overriding it with a longer max_cache_age -- that
    # doesn't work. The constructor-given max_cache_age is an upper bound on what the method kwarg accepts (to stay consistent with
    # the fact that the constructor-given max_cache_age triggers full prunes)
    now = datetime.now()
    client = reinstantiable_client(max_age=timedelta(hours=12))
    unique = client.get(f'{server}/unique-number').text
    mocker.patch('hublot.cache.storage.current_datetime', return_value=now + timedelta(days=1))
    # re-use the same client to ensure there's no pruning happening, that would render the test invalid
    assert unique != client.get(f'{server}/unique-number', max_cache_age=timedelta(days=2)).text


def test_cant_override_with_null_age(mocker, reinstantiable_client, server):
    # instantiate cache with a max_age that doesn't accept the cached file. Try overriding it with max_cache_age=None -- that also
    # doesn't work, we fall back to the constructor-given kwarg
    now = datetime.now()
    client = reinstantiable_client(max_age=timedelta(hours=12))
    unique = client.get(f'{server}/unique-number').text
    mocker.patch('hublot.cache.storage.current_datetime', return_value=now + timedelta(days=1))
    # again, re-use the same client to ensure there's no pruning
    assert unique != client.get(f'{server}/unique-number', max_cache_age=None).text


@pytest.mark.parametrize(
    'redirect_step_is_cached',
    product([False, True], repeat=3),
)
def test_max_age_applies_when_following_redirects(mocker, reinstantiable_client, server, redirect_step_is_cached):
    now = datetime.now()
    mocker.patch('hublot.cache.storage.current_datetime', lambda: now)

    @contextmanager
    def mocked_gzip_open(path, *rest, **kwargs):
        with _real_gzip_open(path, *rest, **kwargs) as f:
            yield f
        utime(path, (now.timestamp(), now.timestamp()))
    _real_gzip_open = gzip.open
    mocker.patch('hublot.cache.storage.gzip.open', mocked_gzip_open)

    client = reinstantiable_client(
        cookies_enabled=False,  # disable cookies as they would invalidate the cache
    )

    # first, cache every step of the redirect chain
    client.fetch(f'{server}/redirect/chain/1')

    # then on the next day, freshen the cache for the redirect steps that should be read from cache
    now += timedelta(hours=24)
    for step_num, is_cached in zip(count(1), redirect_step_is_cached):
        if is_cached:
            client.fetch(
                f'{server}/redirect/chain/{step_num}',
                allow_redirects=False,
                force_cache_stale=True,
            )

    # now if you re-fetch the whole chain, only the ones that were freshly fetched should be read from cache
    now += timedelta(hours=12)
    res = client.fetch(
        f'{server}/redirect/chain/1',
        max_cache_age=timedelta(hours=24),
    )

    assert [r.from_cache for r in [*res.history, res]] == list(redirect_step_is_cached)
