from __future__ import annotations

import re
from pathlib import PurePosixPath
from urllib.parse import urlsplit, urlunsplit

import attr
from typing_extensions import Protocol

from cloudshell.shell.flows.utils.errors import ShellFlowsException


class UrlError(ShellFlowsException):
    ...


class ErrorParsingUrl(UrlError):
    def __init__(self, url_str: str, scheme: str | None = None):
        self.url_str = url_str
        self.scheme = scheme
        msg = f"Failed to parse URL str '{url_str}'"
        if scheme:
            msg = f" with scheme '{scheme}'"
        super().__init__(msg)


class ValidationError(UrlError):
    ...


class NotSupportedUrlScheme(ValidationError):
    def __init__(self, scheme: str):
        self.scheme = scheme
        super().__init__(f"Scheme '{scheme}' is not supported")


class HostCannotBeEmpty(ValidationError):
    def __init__(self):
        super().__init__("Hostname cannot be empty")


class PathIsNotPosixPath(ValidationError):
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Path '{path}' cannot be converted to Posix Path")


class PathShouldStartFromRoot(ValidationError):
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Path '{path}' should start from root")


class FileNameIsNotPresent(UrlError):
    def __init__(self, url):
        super().__init__(f"URL {url} do not include file name")


def _validate_url_scheme(self, attribute, value: str) -> str:
    if value not in self.SUPPORTED_URL_SCHEMES:
        raise NotSupportedUrlScheme(value)
    return value


def _validate_host_is_not_empty(self, attribute, value) -> str:
    if not value:
        raise HostCannotBeEmpty
    return value


def _validate_posix_path(self, attribute, value: str) -> str:
    try:
        PurePosixPath(value)
    except Exception:
        raise PathIsNotPosixPath(value)
    return value


def _validate_path_starts_from_root(self, attribute, value: str) -> str:
    if not value.startswith("/"):
        raise PathShouldStartFromRoot(value)
    return value


def _convert_path_to_start_from_root(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return path


class UrlInterface(Protocol):
    scheme: str
    path: str
    username: str | None = None
    password: str | None = None

    @classmethod
    def from_str(cls, url_str: str, scheme: str | None = None):
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    @property
    def url(self) -> str:
        # Full URL that can contain credentials
        raise NotImplementedError

    @property
    def safe_url(self) -> str:
        # URL without credentials
        raise NotImplementedError

    @property
    def filename(self) -> str | None:
        raise NotImplementedError

    def support_auth(self) -> bool:
        raise NotImplementedError

    def add_filename(self, name: str) -> None:
        raise NotImplementedError

    def replace_filename(self, name: str) -> None:
        raise NotImplementedError

    def get_folder(self) -> str:
        raise NotImplementedError


@attr.s(auto_attribs=True, slots=True, str=False, kw_only=True)
class AbstractUrlWithPosixPath(UrlInterface):
    path: str = attr.ib(
        default="/",
        converter=_convert_path_to_start_from_root,
        validator=(_validate_posix_path, _validate_path_starts_from_root),
        on_setattr=(_validate_posix_path, _validate_path_starts_from_root),
    )

    def __str__(self) -> str:
        return self.url

    @property
    def filename(self) -> str | None:
        return PurePosixPath(self.path).name

    def validate_filename_is_present(self) -> None:
        if not self.filename:
            raise FileNameIsNotPresent(self)

    def add_filename(self, name: str) -> None:
        self.path = str(PurePosixPath(self.path) / name)

    def replace_filename(self, name: str) -> None:
        self.path = str(PurePosixPath(self.path).with_name(name))

    def get_folder(self) -> str:
        return str(PurePosixPath(self.path).parent)


@attr.s(auto_attribs=True, slots=True, str=False, kw_only=True)
class RemoteURL(AbstractUrlWithPosixPath):
    """Parse and builds URLs.

    scheme://[user[:password]@]host[:port][/path]
    ftp://user:password@host/path
    scp://user@host/path
    tftp://host/path
    """

    SUPPORTED_URL_SCHEMES = {"ftp", "sftp", "tftp", "scp", "http", "https"}
    SCHEMES_WITH_AUTH_SUPPORT = {"ftp", "sftp", "scp"}

    scheme: str = attr.ib(
        converter=str.lower,
        validator=_validate_url_scheme,
        on_setattr=_validate_url_scheme,
    )
    host: str = attr.ib(
        validator=_validate_host_is_not_empty, on_setattr=_validate_host_is_not_empty
    )
    port: int | None = None
    username: str | None = None
    password: str | None = None
    query: str = ""
    fragment: str = ""

    @classmethod
    def from_str(cls, url_str: str, scheme: str | None = None) -> RemoteURL:
        if scheme:
            url_str = f"{scheme}://{url_str}"
        args = None
        try:
            args = urlsplit(url_str)
            port = args.port
        except Exception:
            if args and args.scheme.lower() in cls.SUPPORTED_URL_SCHEMES:
                raise ErrorParsingUrl(url_str, scheme)
            raise ValidationError

        return cls(
            scheme=args.scheme,
            host=args.hostname,
            port=port,
            username=args.username,
            password=args.password,
            path=args.path,
            query=args.query,
            fragment=args.fragment,
        )

    @property
    def safe_netloc(self) -> str:
        # safe netloc is host[:port]
        port_str = f":{self.port}" if self.port else ""
        return f"{self.host}{port_str}"

    @property
    def netloc(self) -> str:
        # netloc is [user[:password]@]host[:port]
        password_str = f":{self.password}" if self.password else ""
        credentials = f"{self.username}{password_str}@" if self.username else ""
        return f"{credentials}{self.safe_netloc}"

    @property
    def safe_url(self) -> str:
        return self.__build_url(self.safe_netloc)

    @property
    def url(self) -> str:
        return self.__build_url(self.netloc)

    def support_auth(self) -> bool:
        return self.scheme in self.SCHEMES_WITH_AUTH_SUPPORT

    def __build_url(self, netloc: str) -> str:
        path = self.path
        if path == "/":
            path = ""
        return urlunsplit((self.scheme, netloc, path, self.query, self.fragment))


@attr.s(auto_attribs=True, slots=True, str=False, kw_only=True)
class BasicLocalUrl(AbstractUrlWithPosixPath):
    """Simple Local URL.

    Scheme is first substring before "/"
    Path is the Posix Path
    flash:/path - scheme = flash: | path = path
    disk0:/path - scheme = disk0: | path = path
    flash://path - scheme = flash"" | path = path:/ | path = path
    /path - scheme =
    """

    PATTERN = re.compile(r"^(.+?)/([^/].+)$")
    scheme: str

    @classmethod
    def from_str(cls, url_str: str, scheme: str | None = None) -> BasicLocalUrl:
        if not scheme:
            try:
                scheme, path = cls.PATTERN.search(url_str).groups()
            except (ValueError, AttributeError):
                raise ValidationError
        else:
            path = url_str

        return cls(scheme=scheme, path=path)

    @property
    def url(self) -> str:
        return f"{self.scheme}{self.path}"

    @property
    def safe_url(self) -> str:
        return self.url

    def support_auth(self) -> bool:
        return False


@attr.s(auto_attribs=True, slots=True, str=False, kw_only=True)
class LocalFileURL(AbstractUrlWithPosixPath):
    """File URL.

    file://localhost/path
    file:///path
    file://path
    """

    PATTERN = re.compile(r"^file://(localhost/)?/?(.+)$")
    SCHEME = "file:/"
    scheme: str = "file:/"

    @classmethod
    def from_str(cls, url_str: str, scheme: str | None = None) -> LocalFileURL:
        if scheme:
            assert scheme == cls.SCHEME
            path = url_str
        else:
            try:
                path = cls.PATTERN.search(url_str).group(2)
            except (AttributeError, ValidationError):
                raise ValidationError

        return cls(path=path)

    @property
    def url(self) -> str:
        return f"{self.scheme}/localhost{self.path}"

    @property
    def safe_url(self) -> str:
        return self.url

    def support_auth(self) -> bool:
        return False
