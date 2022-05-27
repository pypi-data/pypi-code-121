#!/usr/bin/env python3

# 3rd parties
from requests import Request

# hublot
from hublot import RequestableABC


def test_requestable_is_runtime_type():
    """ `hublot.RequestableABC` is not a type annotation, it's an ABC class that can be used with `isinstance` """
    assert isinstance('http://blah/', RequestableABC)
    assert isinstance(Request('GET', 'http://blah/'), RequestableABC)
