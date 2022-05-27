#!/usr/bin/env python3

# standards
from itertools import count
import json
from random import choices
from string import ascii_letters

# 3rd parties
import pytest
import requests

# hublot
from hublot import ScraperError, retry_on_scraper_error


def test_retry_decorator_no_exception(client, server):
    @retry_on_scraper_error
    def fetch():
        return client.get(f'{server}/hello').text
    assert fetch() == 'hello'


def test_retry_decorator_on_http_error(client, server, unique_key):
    @retry_on_scraper_error
    def fetch():
        return client.get(f'{server}/fail-twice-then-succeed/{unique_key}').text
    assert fetch() == 'success after 2 failures'


def test_retry_decorator_on_value_error():
    counter = count()
    @retry_on_scraper_error
    def fetch():
        i = next(counter)
        if i < 3:
            raise ValueError('x')
        return f'Success on attempt {i}'
    assert fetch() == 'Success on attempt 3'


def test_retry_decorator_num_attempts_just_enough(client, server, unique_key):
    @retry_on_scraper_error(num_attempts=3)
    def fetch():
        return client.get(f'{server}/fail-twice-then-succeed/{unique_key}').text
    assert fetch() == 'success after 2 failures'


def test_retry_decorator_num_attempts_just_not_enough(client, server, unique_key):
    @retry_on_scraper_error(num_attempts=2)
    def fetch():
        return client.get(f'{server}/fail-twice-then-succeed/{unique_key}').text
    with pytest.raises(ScraperError):
        fetch()


def test_retry_decorator_doesnt_catch_other_exceptions():
    @retry_on_scraper_error
    def fetch():
        raise KeyError('x')
    with pytest.raises(KeyError):
        fetch()


def test_retry_decorator_error_types():
    counter = count()
    @retry_on_scraper_error(error_types=[KeyError])
    def fetch():
        i = next(counter)
        if i < 3:
            raise KeyError('x')
        return f'Success on attempt {i}'
    assert fetch() == 'Success on attempt 3'


def test_if_scraper_returns_generator_it_gets_consumed():
    @retry_on_scraper_error
    def fetch():
        yield 1
        yield 2
        yield 3
    assert fetch() == [1, 2, 3]


def test_if_scraper_returns_iterator_it_gets_consumed():
    @retry_on_scraper_error
    def fetch():
        return (i for i in range(1, 4))
    assert fetch() == [1, 2, 3]


def test_if_scraper_returns_map_it_gets_consumed():
    @retry_on_scraper_error
    def fetch():
        return map(lambda x: x, range(1, 4))
    assert fetch() == [1, 2, 3]


def test_if_scraper_returns_filter_it_gets_consumed():
    @retry_on_scraper_error
    def fetch():
        return filter(lambda x: x, range(1, 4))
    assert fetch() == [1, 2, 3]


def test_if_scraper_returns_dict_keys_it_doesnt_get_consumed():
    @retry_on_scraper_error
    def fetch():
        return {1: 1, 2: 2, 3: 3}.keys()
    assert isinstance(fetch(), type({}.keys()))  # you're confused, pylint: disable=isinstance-second-argument-not-valid-type


def test_if_scraper_returns_requests_response_it_doesnt_get_turned_into_a_list():
    # requests.Response is an example of an object that is iterable, but doesn't have a __len__
    @retry_on_scraper_error
    def fetch():
        return requests.Response()
    assert isinstance(fetch(), requests.Response)


def test_scraper_sleeps_increasingly_long_delays(mocked_sleep_on_retry):
    """
    The first sleep must be >= 0 seconds, and then they must all be > than the previous
    """
    counter = count()
    @retry_on_scraper_error
    def fetch():
        i = next(counter)
        if i < 4:
            raise ValueError('x')
        return f'Success on attempt {i}'
    assert fetch() == 'Success on attempt 4'
    assert mocked_sleep_on_retry.call_count == 4
    previous_sleep = -1
    for attempt in range(4):
        called_args = mocked_sleep_on_retry.call_args_list[attempt][0]
        assert len(called_args) == 1, called_args
        sleep, = called_args
        assert sleep > previous_sleep
        previous_sleep = sleep


def test_no_courtesy_sleep_on_retries(mocked_courtesy_sleep, client, server, unique_key):
    client.get(f'{server}/hello')
    @retry_on_scraper_error
    def fetch():
        return client.get(f'{server}/fail-twice-then-succeed/{unique_key}').text
    fetch()
    sleeps = [call[0][0] for call in mocked_courtesy_sleep.call_args_list]
    # we should've slept on the 1st call b/c we'd just called the server, then no sleep on subsequent calls
    assert sleeps == [pytest.approx(5, 0.1)]


def test_decorated_function_fetches_twice(client, server):
    key_1 = ''.join(choices(ascii_letters, k=32))
    key_2 = ''.join(choices(ascii_letters, k=32))

    @retry_on_scraper_error
    def fetch():
        return [
            client.get(f'{server}/fail-twice-then-succeed/{key_1}').text,
            client.get(f'{server}/fail-twice-then-succeed/{key_2}').text,
        ]

    # The call will succeed on the 5th attempt -- the 1st call fails twice (and the 2nd isn't even reached), then the 2nd call
    # fails twice, then they both work. Because force_cache_stale=True on every retry and applies to both calls, the 1st call was
    # not cached, even after it had succeeded -- when the decorator performs a retry, *all* requests within it are uncached. For
    # that reason the 1st endpoint ends up being called 4 times, and the 2nd one 3 times.
    assert fetch() == ['success after 2 failures and 2 successes', 'success after 2 failures']


def test_decorator_on_client_from_outer_scope(reinstantiable_client, server, unique_key):
    client = reinstantiable_client()
    @retry_on_scraper_error
    def fetch():
        return client.get(f'{server}/fail-twice-then-succeed/{unique_key}').text
    assert fetch() == 'success after 2 failures'


def test_decorator_on_client_passed_as_argument(reinstantiable_client, server, unique_key):
    @retry_on_scraper_error
    def fetch(c):
        return c.get(f'{server}/fail-twice-then-succeed/{unique_key}').text
    assert fetch(reinstantiable_client()) == 'success after 2 failures'


def test_decorator_on_client_created_within_function(reinstantiable_client, server, unique_key):
    @retry_on_scraper_error
    def fetch():
        client = reinstantiable_client()
        return client.get(f'{server}/fail-twice-then-succeed/{unique_key}').text
    assert fetch() == 'success after 2 failures'


def test_parsing_html_as_json_is_a_scraper_error():
    with pytest.raises(ScraperError):
        json.loads('<html>')


def test_nested_scraper_functions(client, server, unique_key):

    # What should happen here:
    #
    #  1. the GET call in `inner()` fails, is retried, and so the call to `inner()` returns "success after 2 failures"
    #
    #  2. the GET call in `outer()` fails, and is retried; this does not force the inner call to be retried though -- that one
    #     keeps being served from cache

    @retry_on_scraper_error
    def inner():
        return 'inner: ' + client.get(f'{server}/fail-twice-then-succeed/{unique_key}-inner').text

    @retry_on_scraper_error
    def outer():
        return [
            inner(),
            'outer: ' + client.get(f'{server}/fail-twice-then-succeed/{unique_key}-outer').text,
        ]

    assert outer() == [
        'inner: success after 2 failures',
        'outer: success after 2 failures',
    ]
