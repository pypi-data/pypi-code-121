#!/usr/bin/env python3

# standards
from io import BytesIO
from itertools import combinations, product
from typing import Dict, Optional

# 3rd parties
from requests import PreparedRequest, Request, Response
from requests.structures import CaseInsensitiveDict

# hublot
from hublot import Client


def dummy_prepared_request(client: Client, **kwargs):
    url = kwargs.pop('url', 'http://example.com/test')
    if not isinstance(url, Request):
        kwargs.setdefault('method', 'POST')
        if kwargs['method'] in ('POST', 'PUT'):
            kwargs.setdefault('data', b'This is my request data')
    return client._prepare(client.build_request(url, **kwargs))  # pylint: disable=protected-access


def dummy_response(
    preq: PreparedRequest,
    status_code: int = 200,
    reason: str = 'OK',
    headers: Optional[Dict[str, str]] = None,
    data: bytes = b'This is my response data',
):
    res = Response()
    res.request = preq
    res.status_code = status_code
    res.reason = reason
    res.headers = CaseInsensitiveDict(headers or {})
    res.url = preq.url  # type: ignore
    res.raw = BytesIO(data)
    return res


def iter_nonequal_pairs(equivalencies):
    for index, group in enumerate(equivalencies):
        all_other_elems = [
            other_group[0]
            for other_index, other_group in enumerate(equivalencies)
            if other_index > index  # Using > to avoid wastefully comparing A to B and B to A
        ]
        for elem, other_elem in product(group, all_other_elems):
            yield elem, other_elem


def iter_equal_pairs(equivalencies):
    for group in equivalencies:
        if len(group) > 2:
            for elem_1, elem_2 in combinations(group, 2):
                yield elem_1, elem_2


def assert_responses_equal(res1, res2):
    state1 = res1.__getstate__()
    state2 = res2.__getstate__()
    state1['request'] = state1['request'] and state1['request'].__dict__
    state2['request'] = state2['request'] and state2['request'].__dict__
    try:
        assert state1 == state2
    except AssertionError:  # pragma: no cover, if the tests pass then this won't get called
        print(state1)
        print(state2)
        raise
