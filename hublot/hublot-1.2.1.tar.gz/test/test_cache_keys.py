#!/usr/bin/env python3

# standards
from collections import OrderedDict
from itertools import count, product

# 3rd parties
import pytest
from requests import Request

# hublot
from hublot.cache import CacheKey
from hublot.logs import LogEntry
from .utils import assert_responses_equal, dummy_prepared_request, dummy_response, iter_equal_pairs, iter_nonequal_pairs


def test_simple_cache_use(client):
    preq = dummy_prepared_request(client)
    log = LogEntry(preq)
    cache = client.cache
    assert cache.get(preq, log) is None
    assert log.cache_key_str is not None
    cache.put(preq, log, dummy_response(preq))
    assert_responses_equal(cache.get(preq, log), dummy_response(preq))


EQUIVALENCIES = [
    # For every attribute of a PreparedRequest, lists groups values such that values within the same group should be cached under
    # the same key, but not across groups

    # Obviously requests using different methods should be cached separately
    [{'method': 'GET'}],
    [{'method': 'POST'}],

    # URLs are case sensitive
    [{'url': 'http://cache-test/url'}],
    [{'url': 'http://cache-test/URL'}],
    [{'url': 'http://cache-test/URL/'}],

    # The ordering of the parameters in the URL string matters. They're not parsed at all, so a final '&' is also a cache breaker
    [{'url': 'http://cache-test/TEST?a=1&b=2'}],
    [{'url': 'http://cache-test/TEST?b=2&a=1'}],
    [{'url': 'http://cache-test/TEST?a=1&b=2&'}],

    # `params` are also part of the URL key
    [{'url': 'http://cache-test/params', 'params': {}}],
    [{'url': 'http://cache-test/params', 'params': {'x': 'a'}}],

    # `params` get appended to the URL, so these are equivalent. Using OrderedDict for pythons before 3.7.
    [
        {'url': 'http://cache-test/params-test', 'params': OrderedDict([('a', '1'), ('b', '2')])},
        {'url': 'http://cache-test/params-test?', 'params': OrderedDict([('a', '1'), ('b', '2')])},
        {'url': 'http://cache-test/params-test?a=1', 'params': OrderedDict([('b', '2')])},
        {'url': 'http://cache-test/params-test?a=1&b=2', 'params': OrderedDict()},
    ],

    # The presence, absence, or value of a header are all enough to bust the cache
    [{'url': 'http://cache-test/header-test', 'headers': {}}],
    [{'url': 'http://cache-test/header-test', 'headers': {'X-Test': '1'}}],
    [{'url': 'http://cache-test/header-test', 'headers': {'X-Test': '2'}}],

    # The `requests` library will normalise the case of headers before sending them off to the server, and so headers are
    # case-insensitive, and so all of these get the same cache key
    [
        {'url': 'http://cache-test/header-test-2', 'headers': {'X-Test': '1'}},
        {'url': 'http://cache-test/header-test-2', 'headers': {'x-test': '1'}},
        {'url': 'http://cache-test/header-test-2', 'headers': {'X-TEST': '1'}},
    ],

    # The order of the headers in the dict doesn't matter of course
    [
        {'url': 'http://cache-test/header-order-test', 'headers': {'X-Test-A': 'a', 'X-Test-B': 'b'}},
        {'url': 'http://cache-test/header-order-test', 'headers': {'X-Test-B': 'b', 'X-Test-A': 'a'}},
    ],

    # Setting a cookie via `cookies` is the same as setting it manually in a header
    [
        {'url': 'http://cache-test/cookie-test', 'cookies': {'a': '1'}, 'headers': {}},
        {'url': 'http://cache-test/cookie-test', 'cookies': {}, 'headers': {'Cookie': 'a=1'}},
    ],

    # Setting `data` as a dict is equivalent to setting it manually as bytes
    [
        {'url': 'http://cache-test/data-test', 'data': {'a': '1'}},
        {
            'url': 'http://cache-test/data-test',
            'data': b'a=1',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': '3'},
        },
    ],

    # Setting `json` is equivalent to manually building the request
    [
        {'url': 'http://cache-test/json-test', 'json': {'a': '1'}},
        {
            'url': 'http://cache-test/json-test',
            'data': b'{"a": "1"}',
            'headers': {'Content-Type': 'application/json'},
        },
    ],

    # requests can be specified as `Request` objects
    [
        {'url': 'http://cache-test/request-objects', 'method': 'GET'},
        {'url': 'http://cache-test/request-objects', 'method': 'GET', 'params': {}},
        {'url': Request(url='http://cache-test/request-objects', method='GET')},
        {'url': Request(url='http://cache-test/request-objects', method='GET', params={})},
    ],
    [
        {'url': 'http://cache-test/request-objects', 'method': 'POST', 'data': {}},
        {'url': Request(url='http://cache-test/request-objects', method='POST', data={})},
    ],
    [
        {
            'url': 'http://cache-test/request-objects',
            'method': 'POST',
            'data': {'a': '1'},
        },
        {
            'url': 'http://cache-test/request-objects',
            'method': 'POST',
            'data': 'a=1',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
        },
        {
            'url': Request(
                url='http://cache-test/request-objects',
                method='POST',
                data={'a': '1'},
            ),
        },
        {
            'url': Request(
                url='http://cache-test/request-objects',
                method='POST',
                data='a=1',
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            ),
        },
    ],

]


@pytest.mark.parametrize(
    'config_1, config_2',
    iter_nonequal_pairs(EQUIVALENCIES),
)
def test_unique_keys(client, config_1, config_2):
    key = CacheKey.compute(dummy_prepared_request(client, **config_1))
    other_key = CacheKey.compute(dummy_prepared_request(client, **config_2))
    assert key != other_key


@pytest.mark.parametrize(
    'config_1, config_2',
    iter_nonequal_pairs(EQUIVALENCIES),
)
def test_unique_requests(client, config_1, config_2):
    cache = client.cache
    preq_1 = dummy_prepared_request(client, **config_1)
    preq_2 = dummy_prepared_request(client, **config_2)
    cache.put(preq_1, LogEntry(preq_1), dummy_response(preq_1))
    assert cache.get(preq_2, LogEntry(preq_2)) is None


@pytest.mark.parametrize(
    'config_1, config_2',
    iter_equal_pairs(EQUIVALENCIES),
)
def test_equivalent_keys(client, config_1, config_2):
    key_1 = CacheKey.compute(dummy_prepared_request(client, **config_1))
    key_2 = CacheKey.compute(dummy_prepared_request(client, **config_2))
    print(dummy_prepared_request(client, **config_1).__dict__)
    print(dummy_prepared_request(client, **config_2).__dict__)
    assert key_1 == key_2, (config_1, config_2)


@pytest.mark.parametrize(
    'config_1, config_2',
    iter_equal_pairs(EQUIVALENCIES),
)
def test_equivalent_requests(client, config_1, config_2):
    cache = client.cache
    preq_1 = dummy_prepared_request(client, **config_1)
    preq_2 = dummy_prepared_request(client, **config_2)
    response = dummy_response(preq_1)
    assert cache.get(preq_2, LogEntry(preq_2)) is None  # else test is invalid
    cache.put(preq_1, LogEntry(preq_1), response)
    assert_responses_equal(
        cache.get(preq_2, LogEntry(preq_2)),
        response,
    )


def test_cache_updates_log_entry_attributes(client):
    cache = client.cache
    preq = dummy_prepared_request(client)
    log = LogEntry(preq)
    assert log.cache_key_str is None
    assert log.cached is None
    cache.get(preq, log)
    assert log.cache_key_str is not None
    assert log.cached is False
    cache.put(preq, log, dummy_response(preq))
    cache.get(preq, log)
    assert log.cached is True


TEST_KEYS = [
    ('simple-string', '/simple-string', 'simple-string'),
    ('space string', '/space%20string', 'space%20string'),
    ('slash/string', '/slash/string', 'slash/string'),
    ('/slash/string', '/slash/string', 'slash/string'),
    ('slash/string/', '/slash/string', 'slash/string'),
    (('item', '123'), '/item/123', 'item/123'),
    (('slash', '/'), '/slash/%2F', 'slash/%2F'),
]


@pytest.mark.parametrize(
    'user_specified, expected_path, expected_unique_str',
    TEST_KEYS
)
def test_cache_key_parsing(user_specified, expected_path, expected_unique_str):
    parsed = CacheKey.parse(user_specified)
    assert ''.join(f'/{p}' for p in parsed.path_parts) == expected_path
    assert parsed.unique_str == expected_unique_str


@pytest.mark.parametrize(
    'user_specified',
    [spec[0] for spec in TEST_KEYS]
)
def test_cache_key_parsing_from_path_parts(user_specified):
    parsed = CacheKey.parse(user_specified)
    assert CacheKey.from_path_parts(parsed.path_parts) == parsed


def test_user_specified_cache_key(client, server):
    counter = count()
    all_keys = ['one', 'two', 'three']
    all_values = [
        client.get(
            f'{server}/unique-number',
            cache_key=key,
            params={'unique': str(next(counter))}
        ).text
        for key in all_keys
    ]
    assert len(set(all_values)) == len(all_values)  # they're all different
    for key, expected in zip(all_keys, all_values):
        obtained = client.get(
            f'{server}/unique-number',
            cache_key=key,
            # the param is actually different, but the cache key isn't, so we should get the same value back
            params={'unique': str(next(counter))}
        ).text
        assert obtained == expected


def test_user_specified_cache_key_on_redirect(client, server):
    res = client.get(
        f'{server}/redirect/chain/1',
        cache_key='fixed',
    )
    assert res.text == 'Landed'
    all_keys_in_cache = sorted(k.unique_str for k in client.cache.storage.iter_all_keys())
    assert all_keys_in_cache == ['fixed', 'fixed.1', 'fixed.2']


@pytest.mark.parametrize(
    'key_1, key_2, should_match',
    [
        (key_1, key_2, group_1 is group_2)
        for group_1, group_2 in product(
            # Keys from the same line here should match each other, and keys from different lines shouldn't
            [
                (CacheKey(parts=('a', 'b')), ('a', 'b'), 'a/b'),
                (CacheKey(parts=('A', 'B')), ('A', 'B'), 'A/B'),
                (CacheKey(parts=('b', 'c')), ('b', 'c'), 'b/c'),
            ],
            repeat=2,
        )
        for key_1 in group_1
        for key_2 in group_2
    ]
)
def test_different_ways_to_express_cache_keys(client, server, key_1, key_2, should_match):
    counter = count()
    response_1, response_2 = (
        client.get(
            f'{server}/unique-number',
            cache_key=key,
            params={'unique': str(next(counter))}
        ).text
        for key in (key_1, key_2)
    )
    if should_match:
        assert response_1 == response_2
    else:
        assert response_1 != response_2


def test_cache_key_of_unknown_class(client):
    class MyRandoClass:
        pass

    with pytest.raises(TypeError):
        client.fetch(
            'http://whatever/',
            cache_key=MyRandoClass(),
        )
