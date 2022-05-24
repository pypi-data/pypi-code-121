from __future__ import annotations

import pytest

from cloudshell.shell.flows.utils.url import (
    BasicLocalUrl,
    ErrorParsingUrl,
    HostCannotBeEmpty,
    LocalFileURL,
    NotSupportedUrlScheme,
    PathIsNotPosixPath,
    PathShouldStartFromRoot,
    RemoteURL,
    UrlInterface,
    ValidationError,
)


@pytest.mark.parametrize(
    ("url_str", "url_obj"),
    (
        ("tftp://192.168.2.3", RemoteURL(scheme="tftp", host="192.168.2.3")),
        (
            "scp://user:pass@192.168.2.3/d:/some_path/test_file_name.ext",
            RemoteURL(
                scheme="scp",
                host="192.168.2.3",
                path="/d:/some_path/test_file_name.ext",
                username="user",
                password="pass",
            ),
        ),
        (
            "scp://user@192.168.2.3:2020/some_path/test_file_name.ext",
            RemoteURL(
                scheme="scp",
                host="192.168.2.3",
                path="/some_path/test_file_name.ext",
                username="user",
                port=2020,
            ),
        ),
        (
            "ftp://user@192.168.2.3",
            RemoteURL(
                scheme="ftp",
                host="192.168.2.3",
                path="/",
                username="user",
            ),
        ),
        (
            "ftp://cisco:securePassword!1@test.host.com:22"
            "/some_path/test_file_name.ext?arg=val",
            RemoteURL(
                scheme="ftp",
                host="test.host.com",
                port=22,
                username="cisco",
                password="securePassword!1",
                path="/some_path/test_file_name.ext",
                query="arg=val",
            ),
        ),
    ),
)
def test_remote_url_handler_parse_str(url_str, url_obj):
    url = RemoteURL.from_str(url_str)
    assert url == url_obj
    assert url.url == url_str

    if url.username:
        assert url.username not in url.safe_url
    if url.password:
        assert url.password not in url.safe_url


def test_remote_url_with_scheme():
    url = RemoteURL.from_str("192.168.8.5", "ftp")
    assert url.host == "192.168.8.5"
    assert url.scheme == "ftp"
    assert url.path == "/"


@pytest.mark.parametrize(("scheme",), (("invalid scheme",), ("",)))
def test_remote_url_with_not_supported_schemes(scheme):
    with pytest.raises(NotSupportedUrlScheme):
        RemoteURL(scheme=scheme, host="host")


def test_remote_url_without_host():
    with pytest.raises(HostCannotBeEmpty):
        RemoteURL(scheme="ftp", host="")


def test_remote_url_failed_to_parse():
    with pytest.raises(ErrorParsingUrl):
        # not supported SCP syntax - raise Parsing exception
        RemoteURL.from_str("scp://host:path")
    with pytest.raises(ErrorParsingUrl):
        RemoteURL.from_str("host:path", scheme="scp")


def test_remote_url_invalid_scheme_from_str():
    with pytest.raises(ValidationError):
        # not supported syntax with unknown scheme - Validation Error
        RemoteURL.from_str("sscp://host:path")


def test_adding_extra_data_later():
    url = RemoteURL.from_str("ftp://ftp-host.com")

    url.port = 4013
    assert url.url == url.safe_url
    assert url.url == "ftp://ftp-host.com:4013"

    url.username = "ftp-user"
    assert url.url == "ftp://ftp-user@ftp-host.com:4013"
    assert url.safe_url == "ftp://ftp-host.com:4013"

    url.password = "ftp-password"
    assert url.url == "ftp://ftp-user:ftp-password@ftp-host.com:4013"
    assert url.safe_url == "ftp://ftp-host.com:4013"


def test_remote_url_path_startswith_root():
    url1 = RemoteURL.from_str("ftp://host.com")
    assert url1.path == "/"
    assert url1.filename == ""
    assert url1.get_folder() == "/"

    url1.add_filename("file.ext")
    assert url1.path == "/file.ext"
    assert url1.filename == "file.ext"
    assert url1.get_folder() == "/"


def test_getting_and_setting_filename():
    url1 = RemoteURL.from_str("ftp://host.com")
    url1.add_filename("file.ext")
    assert url1.filename == "file.ext"
    assert url1.get_folder() == "/"
    assert url1.path == "/file.ext"

    url1.replace_filename("another-file.ext")
    assert url1.filename == "another-file.ext"
    assert url1.get_folder() == "/"
    assert url1.path == "/another-file.ext"

    url2 = RemoteURL.from_str("scp://host/folder_path/file.txt")
    assert url2.filename == "file.txt"
    assert url2.get_folder() == "/folder_path"
    assert url2.path == "/folder_path/file.txt"

    url3 = RemoteURL.from_str("ftp://host/file.txt")
    assert url3.filename == "file.txt"
    assert url3.path == "/file.txt"


def test_validation_posix_path():
    url = RemoteURL(scheme="ftp", host="host")
    with pytest.raises(PathIsNotPosixPath):
        url.path = 1


def test_validation_path_starts_from_root():
    url = RemoteURL(scheme="ftp", host="host")
    with pytest.raises(PathShouldStartFromRoot):
        url.path = "path"


@pytest.mark.parametrize(
    ("url_str", "expected_url"),
    (
        ("flash:/path", BasicLocalUrl(scheme="flash:", path="/path")),
        (
            "flash:/path/folder/folder/file",
            BasicLocalUrl(scheme="flash:", path="/path/folder/folder/file"),
        ),
        ("flash://path", BasicLocalUrl(scheme="flash:/", path="/path")),
        (
            "flash://path/folder/folder/file",
            BasicLocalUrl(scheme="flash:/", path="/path/folder/folder/file"),
        ),
    ),
)
def test_basic_local_url(url_str, expected_url):
    url = BasicLocalUrl.from_str(url_str)
    assert url == expected_url
    assert url.url == url.safe_url == url_str


def test_basic_local_url_wrong():
    with pytest.raises(ValidationError):
        BasicLocalUrl.from_str("path")


@pytest.mark.parametrize(
    ("url_str", "expected_url"),
    (
        ("file://localhost/path/file", LocalFileURL(path="/path/file")),
        ("file:///path/file", LocalFileURL(path="/path/file")),
        ("file://path/file", LocalFileURL(path="/path/file")),
    ),
)
def test_local_file_url(url_str, expected_url):
    url = LocalFileURL.from_str(url_str)
    assert url == expected_url
    assert url.url == url.safe_url == f"file://localhost{url.path}"


def test_local_file_url_with_scheme():
    url = LocalFileURL.from_str("file", scheme="file:/")
    assert url.url == "file://localhost/file"


def test_local_file_url_support_only_file_scheme():
    with pytest.raises(AssertionError):
        LocalFileURL.from_str("", scheme="scheme")


def test_local_file_url_wrong_url():
    with pytest.raises(ValidationError):
        LocalFileURL.from_str("f://path")


def test_local_file_url_do_not_support_auth():
    url = LocalFileURL(path="path")
    assert url.support_auth() is False


def test_interface_methods_not_implemented():
    class TestURL(UrlInterface):
        @classmethod
        def from_str(cls, url_str: str, scheme: str | None = None):
            super().from_str(url_str, scheme)

        def __str__(self):
            super().__str__()

        @property
        def url(self) -> str:
            return super().url

        @property
        def safe_url(self) -> str:
            return super().safe_url

        @property
        def filename(self) -> str | None:
            return super().filename

        def support_auth(self) -> bool:
            return super().support_auth()

        def add_filename(self, name: str) -> None:
            super().add_filename(name)

        def replace_filename(self, name: str) -> None:
            super().replace_filename(name)

        def get_folder(self) -> str:
            return super().get_folder()

    url = TestURL()
    with pytest.raises(NotImplementedError):
        url.from_str("")
    with pytest.raises(NotImplementedError):
        str(url)
    with pytest.raises(NotImplementedError):
        _ = url.url
    with pytest.raises(NotImplementedError):
        _ = url.safe_url
    with pytest.raises(NotImplementedError):
        _ = url.filename
    with pytest.raises(NotImplementedError):
        url.support_auth()
    with pytest.raises(NotImplementedError):
        url.add_filename("")
    with pytest.raises(NotImplementedError):
        url.replace_filename("")
    with pytest.raises(NotImplementedError):
        url.get_folder()
