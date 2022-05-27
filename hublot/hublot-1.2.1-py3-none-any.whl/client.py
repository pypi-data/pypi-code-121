#!/usr/bin/env python3

# standards
from abc import ABC
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
import re
from typing import Any, Dict, Optional, Set, Union
from urllib.parse import urljoin

# 3rd parties
from requests import PreparedRequest, Request, Response, Session, TooManyRedirects
from requests.cookies import MockRequest, RequestsCookieJar
import urllib3.util.url

# hublot
from .cache import Cache, CacheKey, UserSpecifiedCacheKey
from .courtesy import CourtesySleep
from .decorator import SCRAPER_LOCAL
from .logs import LOGGER, LogEntry
from .utils import HublotCookiePolicy, MockResponse
from .version import HUBLOT_VERSION


MAX_REDIRECTS = 10


class RequestableABC(ABC):
    """ Umbrella type for values that can be passed to the `request` method """

RequestableABC.register(str)
RequestableABC.register(Request)

# Sadly mypy doesn't understand ABC.register, so AFAICT we need `RequestableABC` for run-time `isinstance` checks, and
# `Requestable` for static analysis type checks
Requestable = Union[RequestableABC, str, Request]


class Client:

    def __init__(
        self,
        cache: Union[Cache, Path, str, None] = None,
        courtesy_sleep: Union[CourtesySleep, timedelta, None] = timedelta(seconds=5),
        session: Optional[Session] = None,
        max_cache_age: Optional[timedelta] = None,
        user_agent: str = f'hublot/{HUBLOT_VERSION}',
        cookies_enabled: bool = True,
        proxies: Optional[Dict[str, str]] = None,
    ):
        self.cache = Cache.load(cache, max_cache_age)
        if not isinstance(courtesy_sleep, CourtesySleep):
            courtesy_sleep = CourtesySleep(courtesy_sleep)  # malkovitch malkovitch
        self.courtesy_sleep = courtesy_sleep
        self.session = session or Session()
        self.session.cookies.set_policy(HublotCookiePolicy(cookies_enabled))
        if proxies:
            self.session.proxies = proxies
        self.user_agent = user_agent

    @property
    def cookies(self) -> RequestsCookieJar:
        return self.session.cookies

    def fetch(  # pylint: disable=too-many-locals
        self,
        url: Requestable,
        courtesy_sleep: Optional[timedelta] = None,
        raise_for_status: bool = True,
        force_cache_stale: bool = False,
        allow_redirects: bool = True,
        cache_key: Optional[UserSpecifiedCacheKey] = None,
        max_cache_age: Optional[timedelta] = None,
        proxies: Optional[Dict[str, str]] = None,
        verify: Optional[bool] = True,
        _redirected_from: Optional[Response] = None,
        **kwargs,
    ) -> Response:
        """
        NB the first parameter is called `url`, even though it could also be a `Request` object, simply because that's shorter and
        nicer than `requestable`. Hey, `urllib.request.urlopen` does the same thing, so.
        """
        frame = SCRAPER_LOCAL.stack[-1]
        if frame.is_retry:
            force_cache_stale = True
            courtesy_sleep = timedelta(0)
        with patched_encode_invalid_chars():
            req = self.build_request(url, **kwargs)
            preq = self._prepare(req)
            log = LogEntry(preq, is_redirect=(_redirected_from is not None))
            res = self._fetch_response(
                req,
                preq,
                log,
                courtesy_sleep,
                force_cache_stale,
                cache_key,
                max_cache_age,
                proxies,
                verify,
            )
            if res.from_cache:  # type: ignore[attr-defined]  # we add that attribute
                self.session.cookies.extract_cookies(MockResponse(res), MockRequest(preq))  # type: ignore[arg-type]
        if _redirected_from:
            res.history = [*_redirected_from.history, _redirected_from]
        LOGGER.info('%s', log)
        return self._handle_response(
            preq,
            res,
            raise_for_status,
            force_cache_stale,
            allow_redirects,
            cache_key,
            max_cache_age,
            _redirected_from,
        )

    @staticmethod
    def build_request(url: Requestable, **kwargs) -> Request:
        """
        Takes a `Requestable` and compiles it into a `requests.Request` object.
        """
        if isinstance(url, Request):
            if kwargs:
                # I'm putting this here to avoid unforeseen behaviour, but if it ever becomes a problem, could consider relaxing
                # this constraint.
                kwargs_str = ', '.join(sorted(map(repr, kwargs)))
                raise TypeError(f"If passing a Request object to `fetch`, can't specify kwargs: {kwargs_str}")
            return url
        else:
            method = kwargs.pop(
                'method',
                'POST' if (
                    kwargs.get('data') is not None
                    or kwargs.get('files') is not None
                    or kwargs.get('json') is not None
                )
                else 'GET'
            ).upper()
            return Request(method, url, **kwargs)

    def _prepare(self, req: Request) -> PreparedRequest:
        """
        Given the user-supplied arguments to the `request`, method, compile a `PreparedRequest` object. Normally this is done
        within Requests (and it will still be done by Requests when we call it), but we need this in order to compute the cache
        key.

        NB this modifies the given `params` dict to remove the 'method', if any.
        """
        req.data = self._read_files_to_memory(req.data)
        req.files = self._read_files_to_memory(req.files)
        req.headers.setdefault('User-Agent', self.user_agent)
        return self.session.prepare_request(req)

    def _fetch_response(
        self,
        req: Request,
        preq: PreparedRequest,
        log: LogEntry,
        courtesy_sleep: Optional[timedelta],
        force_cache_stale: bool,
        cache_key: Optional[UserSpecifiedCacheKey],
        max_cache_age: Optional[timedelta],
        proxies: Optional[Dict[str, str]],
        verify: Optional[bool],
    ) -> Response:
        """
        Either read the Response from cache, or perform the HTTP transaction and save the response to cache
        """
        if self.cache and not force_cache_stale:
            res = self.cache.get(preq, log, cache_key, max_cache_age)
            if res is not None:
                res.from_cache = True  # type: ignore[attr-defined]  # we add that attribute
                return res
        with self.courtesy_sleep(preq, log, courtesy_sleep):
            res = self.session.request(
                allow_redirects=False,
                proxies=proxies,
                verify=verify,
                **req.__dict__,
            )
        res.from_cache = False  # type: ignore[attr-defined]  # we add that attribute
        if self.cache:
            self.cache.put(preq, log, res, cache_key)
        return res

    def _handle_response(
        self,
        preq: PreparedRequest,
        res: Response,
        raise_for_status: bool,
        force_cache_stale: bool,
        allow_redirects: bool,
        cache_key: Optional[UserSpecifiedCacheKey],
        max_cache_age: Optional[timedelta],
        _redirected_from: Optional[Response],
    ):
        """
        Examine the `Response` we just got, and decide what to do with it: follow a redirect (if any), raise an exception, or just
        return the response.
        """
        if allow_redirects and res.is_redirect:
            if _redirected_from and len(_redirected_from.history) >= MAX_REDIRECTS:
                raise TooManyRedirects(f'Exceeded {MAX_REDIRECTS} redirects')
            return self.fetch(
                urljoin(preq.url, res.headers['Location']),  # type: ignore  # we've checked that `preq.url` is not None
                courtesy_sleep=timedelta(0),
                raise_for_status=raise_for_status,
                force_cache_stale=force_cache_stale,
                cache_key=cache_key and CacheKey.parse(cache_key).next_in_sequence(),
                max_cache_age=max_cache_age,
                _redirected_from=res,
            )
        if raise_for_status:
            res.raise_for_status()
        return res

    def _read_files_to_memory(self, obj: Any) -> Any:
        """
        If `data` or `files` are open file objects, read their contents to memory. We need to see their data in order to include the
        request body in the cache key.
        """
        if callable(getattr(obj, 'read', None)):
            body = obj.read()
            obj.close()
            return body
        elif isinstance(obj, dict):
            return {key: self._read_files_to_memory(value) for key, value in obj.items()}
        else:
            return obj

    ### for a thin layer of Requests compatibility

    def request(self, method: str, url: str, **kwargs) -> Response:
        return self.fetch(url, method=method, **kwargs)

    def get(self, url: str, **kwargs) -> Response:
        return self.fetch(url, method='GET', **kwargs)

    def post(self, url: str, data=None, **kwargs) -> Response:
        return self.fetch(url, method='POST', data=data, **kwargs)


_encode_invalid_chars = urllib3.util.url._encode_invalid_chars  # pylint: disable=protected-access


def _encode_invalid_chars_preserve_case(component: str, allowed_chars: Set[str], encoding: str = 'utf-8') -> str:
    new = _encode_invalid_chars(component, allowed_chars, encoding=encoding)
    if new != component:
        # `urllib3`, which is used internally by `requests`, changes the casing of %xx escapes, always forcing them to uppercase.
        # This means that if a server is set up such that when you ask for a URL with uppercase escapes it redirects you to the
        # same URL with lowercase escapes, then `requests` is unable to fetch that page -- the URL in the redirect response
        # 'location' will be re-uppercased, leading to a redirect loop. Here we work around that by chaging it back to lowercase.
        #
        # You could argue that the HTTP spec says %-escapes are case-insensitive, so it's the server described above that's
        # buggy, but browsers have no problem fetching such a page, so I'd argue it's a `requests` bug.
        #
        new = re.sub(r'%[0-9a-fA-F]{2}', lambda m: m.group().lower(), new)
    return new


@contextmanager
def patched_encode_invalid_chars():
    # pylint: disable=protected-access
    original = urllib3.util.url._encode_invalid_chars
    urllib3.util.url._encode_invalid_chars = _encode_invalid_chars_preserve_case
    try:
        yield
    finally:
        urllib3.util.url._encode_invalid_chars = original
