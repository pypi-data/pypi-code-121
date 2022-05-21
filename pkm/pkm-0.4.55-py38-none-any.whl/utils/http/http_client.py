import hashlib
import json
import locale
import shutil
import socket
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import datetime
from gzip import GzipFile
from http.client import HTTPSConnection, HTTPConnection, HTTPResponse
from pathlib import Path
from socket import AddressFamily
from threading import Lock
from typing import Deque, Dict, Type, Optional, cast, Any, ContextManager, IO, Union, Iterable
from urllib.parse import urlsplit

from pkm.config.configuration import TomlFileConfiguration
from pkm.utils.commons import Closeable, IllegalStateException
from pkm.utils.dicts import get_or_put
from pkm.utils.http.cache_directive import TF_HTTP, CacheDirective
from pkm.utils.http.http_monitors import FetchResourceMonitoredOp, FetchResourceCacheHitEvent, \
    FetchResourceDownloadStartEvent
from pkm.utils.promises import Promise, Deferred
from pkm.utils.properties import clear_cached_properties, cached_property

_next_connection_number = 0
HTTPConnection.debuglevel = 0

# Sad Hacks:
# ------------
# this sad hack is made because http timestamp parsing requires en_us locale, I can probably write my own parser/writer
# to remove this hack
try:
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# this sad hack is made because for some reason,
# many services still has problem with ipv6 (like cloudfront occasionally have)
# and some are just slower to accept connections (like pypi)
original_getaddrinfo = socket.getaddrinfo


# noinspection PyShadowingBuiltins
def get_addr_info_prefer_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    result = original_getaddrinfo(host, port, family, type, proto, flags)
    result.sort(key=lambda it: it[0] == AddressFamily.AF_INET6)
    return result


socket.getaddrinfo = get_addr_info_prefer_ipv4


class HttpException(IOError):

    def __init__(self, msg: str, response: Optional[HTTPResponse] = None) -> None:
        super().__init__(msg)
        self.response = response


@dataclass(frozen=True, eq=True)
class Url:
    scheme: str
    host: str
    port: int
    path: str
    query_string: str
    fragment: str

    def connection_part(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"

    def resource_part(self) -> str:
        query_str = "" if not self.query_string else f"?{self.query_string}"
        fragment_str = "" if not self.fragment else f"#{self.fragment}"
        return f"{self.path}{query_str}{fragment_str}"

    def __str__(self):
        default_port = (self.scheme == 'https' and self.port == 443) or (self.scheme == 'http' and self.port == 80)
        port_str = "" if default_port else f":{self.port}"
        query_str = "" if not self.query_string else f"?{self.query_string}"
        fragment_str = "" if not self.fragment else f"#{self.fragment}"
        return f"{self.scheme}://{self.host}{port_str}{self.path}{query_str}{fragment_str}"

    @property
    def connection_type(self) -> Type[HTTPConnection]:
        if self.scheme == 'https':
            return HTTPSConnection
        return HTTPConnection

    @classmethod
    def parse(cls, url: str) -> "Url":
        parts = urlsplit(url)
        scheme = parts.scheme
        if ':' in parts.netloc:
            host, port = parts.netloc.split(':')
        else:
            host = parts.netloc
            port = '80' if scheme == 'http' else '443'

        # if not scheme or not host:
        #     raise ValueError("no schema or host in url")
        return Url(scheme, host, int(port), parts.path, parts.query, parts.fragment)


class _ConnectionProxy(Closeable):
    def __init__(self, conn: HTTPConnection, owner: "_Connections"):
        self._conn = conn
        self._owner = owner

    def __getattr__(self, item):
        if self._conn is None:
            raise ConnectionError("connection closed")

        return getattr(self._conn, item)

    def __del__(self):
        self.close()

    def close(self):
        if self._conn is not None:
            # noinspection PyProtectedMember
            self._owner._release(self._conn)
            self._conn = None


class _Connections(Closeable):
    def __init__(self, ctype: Type[HTTPConnection], host: str, port: int, cached_amount: int):
        self._ctype = ctype
        self._host = host
        self._port = port
        self._connections: Deque[HTTPConnection] = deque()
        self._lock = Lock()
        self._cached_amount = cached_amount
        self._closed = False

    def acquire(self) -> HTTPConnection:
        result: Optional[HTTPConnection] = None
        with self._lock:
            if self._connections:
                result = self._connections.pop()

        if not result:
            result = self._ctype(host=self._host, port=self._port, timeout=10)
            global _next_connection_number
            result.number = _next_connection_number
            _next_connection_number += 1
        return cast(HTTPConnection, _ConnectionProxy(result, self))

    def _release(self, conn: HTTPConnection):
        with self._lock:
            if conn in self._connections:
                return
            if not self._closed and len(self._connections) < self._cached_amount:
                self._connections.append(conn)
            else:
                conn.close()

    def close(self):
        with self._lock:
            self._closed = True
            for c in self._connections:
                c.close()
            self._connections.clear()


class _ConnectionPool(Closeable):

    def __init__(self, cached_amount: int = 24):
        self._connections: Dict[str, _Connections] = {}
        self._cached_amount = cached_amount
        self._lock = Lock()
        self._closed = False

    def connection_for(self, url: Url) -> HTTPConnection:
        connection_key = url.connection_part()
        with self._lock:
            if self._closed:
                raise IllegalStateException("already closed")

            return get_or_put(
                self._connections, connection_key,
                lambda: _Connections(url.connection_type, url.host, url.port, cached_amount=self._cached_amount)) \
                .acquire()

    def close(self):
        with self._lock:
            self._closed = True
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()


@dataclass
class FetchedResource:
    fetch_info: Path
    data: Path
    _root: Path

    def delete(self):
        self.fetch_info.unlink(missing_ok=True)
        self.data.unlink(missing_ok=True)

        p = self.fetch_info.parent
        while p != self._root:
            if any(p.iterdir()):
                break

            p.unlink()
            p = p.parent

        clear_cached_properties(self)

    def exists(self) -> bool:
        return self.data.exists() and self.fetch_info.exists()

    def read_data_as_json(self) -> Any:
        with self.data.open('r') as inp:
            return json.load(inp)

    @cached_property
    def fetch_info_data(self) -> TomlFileConfiguration:
        return TomlFileConfiguration.load(self.fetch_info)

    def is_hash_valid(self, hash_function: str, hash_hex_value: str):

        fetch_info = self.fetch_info_data
        fetch_hash = fetch_info[f'hash.{hash_function}']

        if not fetch_hash:
            hash_ = hashlib.new(hash_function)
            with open(self.data, 'rb') as f:
                while True:
                    next_ = f.read(8192)
                    if not next_:
                        break
                    hash_.update(next_)

            fetch_hash = hash_.hexdigest()
            fetch_info[f'hash.{hash_function}'] = fetch_hash
            fetch_info.save()

        return fetch_hash == hash_hex_value

    def save(self, response: HTTPResponse):
        self.data.parent.mkdir(exist_ok=True, parents=True)
        if self.fetch_info.exists():
            self.fetch_info.unlink()

        try:
            with open(self.data, 'wb') as df:
                shutil.copyfileobj(response, df)

            rheaders = response.headers
            last_modified = rheaders.get('last-modified', rheaders.get('date'))

            # noinspection PyPropertyAccess
            fetch_info = self.fetch_info_data = TomlFileConfiguration(path=self.fetch_info)
            fetch_info['fetch-time'] = last_modified or datetime.utcnow().strftime(TF_HTTP)
            fetch_info['etag'] = rheaders.get("etag") or ''

            fetch_info.save()
        except:  # noqa
            self.delete()
            raise


class _GzipResponseWrapper:
    def __init__(self, response: HTTPResponse):
        self._response = response
        self._stream = GzipFile(fileobj=self._response)

    def read(self, amt: Optional[int] = None):
        return self._stream.read(amt if amt is not None else -1)

    def readinto(self, b: bytearray):
        return self._stream.readinto(b)

    def __getattr__(self, item):
        return getattr(self._response, item)


def _add_standard_headers(headers: Dict[str, str]):
    headers['user-agent'] = f'pkm'
    headers['accept-encoding'] = 'gzip'
    headers['connection'] = 'keep-alive'


class HttpClient:

    def __init__(self, workspace: Path, max_redirects: int = 3, max_connection_retries: int = 2):
        self.workspace = workspace
        workspace.mkdir(exist_ok=True, parents=True)

        self._pool = _ConnectionPool()
        self._fetch_inprogress: Dict[str, Promise[FetchedResource]] = {}
        self._fetch_lock = Lock()
        self._max_redirects = max_redirects
        self._max_connection_retries = max_connection_retries

    def _resource_files_of(self, url: Url) -> FetchedResource:
        url_hash = hashlib.md5(str(url).encode('ascii')).hexdigest()
        url_path = Path(url.path.lstrip('/'))

        if url_path.parent:
            cache_dir = self.workspace / url.host / url_path.parent / url_hash
        else:
            cache_dir = self.workspace / url.host / url_hash

        data_file = cache_dir / url_path.name
        fetch_file = data_file.with_suffix(".fetch.toml")

        return FetchedResource(fetch_file, data_file, self.workspace)

    @contextmanager
    def _request(
            self, mtd: str, url: Url, headers: Dict[str, str],
            payload: Union[IO, str, bytes, None, Iterable[bytes]] = None, *,
            max_redirects: int = -1
    ) -> ContextManager[HTTPResponse]:

        conn: HTTPConnection
        num_redirects_performed = 0
        num_connection_retries = 0

        max_redirects = self._max_redirects if max_redirects < 0 else max_redirects

        while num_connection_retries < self._max_connection_retries and num_redirects_performed <= max_redirects:
            with self._pool.connection_for(url) as conn:
                try:
                    # print(f"[CONN] using connection {conn.number} to connect to {str(url)}")  # noqa
                    conn.request(mtd, url.resource_part(), headers=headers, body=payload)
                    with conn.getresponse() as response:
                        if response.status in (301, 302, 303, 307, 308):
                            num_redirects_performed += 1
                            num_connection_retries = 0
                            if not (new_location := response.headers.get("Location")):
                                raise HttpException(
                                    "server responded with redirect but without supplying a new location")
                            if new_location.startswith("/"):
                                url = replace(url, path=new_location)
                            else:
                                url = Url.parse(new_location)
                            response.read()
                        else:
                            if response.headers.get('Content-Encoding') == 'gzip':
                                yield cast(HTTPResponse, _GzipResponseWrapper(response))
                            else:
                                yield response
                            return
                except ConnectionError:
                    num_connection_retries += 1

        error = "max redirects reached" if num_redirects_performed > self._max_redirects else "connection failed"
        raise HttpException(error)

    @contextmanager
    def post(
            self, url: str, payload: Union[IO, str, bytes, None, Iterable[bytes]] = None,
            headers: Optional[Dict[str, str]] = None, *, max_redirects: int = -1) -> ContextManager[HTTPResponse]:

        headers = headers or {}
        url = Url.parse(url)
        _add_standard_headers(headers)

        with self._request("POST", url, headers, payload, max_redirects=max_redirects) as response:
            yield response

    @contextmanager
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, *,
            max_redirects: int = -1) -> ContextManager[HTTPResponse]:

        headers = headers or {}
        url = Url.parse(url)
        _add_standard_headers(headers)

        with self._request("GET", url, headers, max_redirects=max_redirects) as response:
            yield response

    def fetch_resource(
            self, url: str, cache: Optional[CacheDirective] = None,
            resource_name: Optional[str] = None) -> Optional[FetchedResource]:

        parsed_url = Url.parse(url)
        resource_name = resource_name or parsed_url.path.split("/")[-1]

        with FetchResourceMonitoredOp(resource_name, url) as mop:
            if not cache:
                cache = CacheDirective.allways()

            cached = True
            with self._fetch_lock:

                # If I am already requesting this url - no need to actually do it twice, note that
                # this may pose a problem if one of the recipients will delete the files, if it revealed to be a problem
                # we can fix it by adding a ref-counting delete operation for the FetchedResource for example
                promise = self._fetch_inprogress.get(url)

                if not promise:
                    cached = False

                    def _fetch() -> Optional[FetchedResource]:
                        headers = {}
                        cache_files = self._resource_files_of(parsed_url)
                        fetch_info = TomlFileConfiguration.load(
                            cache_files.fetch_info)  # TODO: maybe add the response headers
                        _add_standard_headers(headers)

                        use_cached_data = cache_files.exists() and cache.is_cache_valid(fetch_info)
                        if use_cached_data:
                            mop.notify(FetchResourceCacheHitEvent())
                        else:
                            # console.log(f"[Start]: GET {url}...")
                            response: Optional[HTTPResponse] = None

                            # noinspection PyShadowingNames
                            try:
                                cache.add_headers(fetch_info, headers)
                                with self._request("GET", parsed_url, headers=headers) as response:
                                    clength = int(response.headers.get('content-length', '-1'))
                                    mop.notify(FetchResourceDownloadStartEvent(clength, cache_files.data))

                                    # print(f"[MID] GET {url} resulted with status code: {response.status}...")

                                    if response.status == 200:
                                        cache_files.save(response)
                                    elif response.status != 304:
                                        raise HttpException(
                                            f"request to {url} ended with unexpected status code:"
                                            f" {response.status} ({response.msg})", response)
                            except Exception as e:
                                if isinstance(e, HttpException):
                                    raise
                                else:
                                    raise HttpException(str(e), response) from e
                            finally:
                                # print(f"thread: {threading.current_thread().ident} attempting to release task")
                                with self._fetch_lock:
                                    del self._fetch_inprogress[url]
                                # print(f"thread: {threading.current_thread().ident} succss to release task")

                        # print(f"[END] GET {url} resulted with cache files: {cache_files}")
                        return cache_files

                    deffered: Deferred[Optional[FetchedResource]] = Deferred()
                    promise = self._fetch_inprogress[url] = deffered.promise()

            if cached:
                mop.notify(FetchResourceCacheHitEvent())
                return promise.result()

            try:
                deffered.complete(_fetch())
            except Exception as e:
                deffered.fail(e)

            return promise.result()

    def clear_resources(self):
        shutil.rmtree(self.workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
