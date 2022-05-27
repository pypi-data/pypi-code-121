#!/usr/bin/env python3

# standards
from http.cookiejar import CookiePolicy
from typing import Callable, Dict, TypeVar

# 3rd parties
from requests import Response

# hublot
from .exceptions import ScraperError


class HublotCookiePolicy(CookiePolicy):  # pragma: no cover, we don't care how this gets called, as long as it works

    netscape = True
    rfc2965 = False
    hide_cookie2 = False

    def __init__(self, cookies_enabled: bool):
        super().__init__()
        self.cookies_enabled = cookies_enabled

    def set_ok(self, cookie, request):
        return self.cookies_enabled

    def return_ok(self, cookie, request):
        return self.cookies_enabled

    def domain_return_ok(self, domain, request):
        return self.cookies_enabled

    def path_return_ok(self, path, request):
        return self.cookies_enabled


class MockResponse: # pragma: no cover -- again, as long as it works, we don't care how urllib3 or whatever it is calls this

    def __init__(self, response: Response):
        self.response = response

    def info(self):
        return self

    def get_all(self, name, failobj=None):
        # This is a mock of `email.message.EmailMessage.get_all` -- ``Return a list of all the values for the field named name. If
        # there are no such named headers in the message, failobj is returned''
        #
        # See https://docs.python.org/3.8/library/email.message.html#email.message.EmailMessage.get_all
        if callable(getattr(self.response.headers, 'get_all', None)):
            # It must be that `headers` is a `MultipleCaseInsensitiveDict` that we created when loading from cache. It gives us the
            # un-joined cookies, use that
            return self.response.headers.get_all(name, failobj)
        else:
            # Fall back to reading from the ', '-joined string.
            if name in self.response.headers:
                return [self.response.headers[name]]
        return failobj


KeyType = TypeVar('KeyType')

ValueType = TypeVar('ValueType')

class LookupFailure(ScraperError):
    pass

def lookup(values: Dict[KeyType, ValueType]) -> Callable[[KeyType], ValueType]:
    def _lookup(key: KeyType):
        try:
            return values[key]
        except KeyError as error:
            raise LookupFailure(repr(key)) from error
    return _lookup
