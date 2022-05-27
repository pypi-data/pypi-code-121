"""Tests for storage.py."""
import http
import json
from pathlib import Path
import pickle
import re
from typing import Dict, Final, Optional, Type, Union
from unittest.mock import AsyncMock, Mock

import httpx
import msgpack
import pytest
from pytest import fixture
from pytest_httpx import HTTPXMock
from pytest_mock import MockerFixture
import requests
from requests import HTTPError, RequestException
from requests_toolbelt import MultipartDecoder
import responses
from responses.matchers import multipart_matcher

from bitfount import storage, web_utils
from bitfount.storage import (
    _DEFAULT_FILE_NAME,
    _async_download_data_from_s3,
    _async_download_from_s3,
    _async_upload_data_to_s3,
    _async_upload_to_s3,
    _download_data_from_s3,
    _download_file_from_s3,
    _download_from_s3,
    _get_packed_data_object_size,
    _upload_data_to_s3,
    _upload_file_to_s3,
    _upload_to_s3,
)
from bitfount.types import _S3PresignedPOSTFields, _S3PresignedPOSTURL, _S3PresignedURL
from tests.utils.helper import unit_test

_HTTP_STATUS_CODES: Final = tuple(i.value for i in http.HTTPStatus)


@fixture
def data() -> Dict[str, Union[int, str]]:
    """Data to upload."""
    return {"this": "is", "some": "data", "object": 1}


@fixture
def packed_data(data: Dict[str, Union[int, str]]) -> bytes:
    """Data form when it has been packed by msgpack."""
    return msgpack.dumps(json.dumps(data))


@fixture
def file_name() -> str:
    """Filename for data file."""
    return "data_file.txt"


@fixture
def custom_filename() -> str:
    """Custom filename to use for tests."""
    return "custom_filename.txt"


@fixture
def data_file(data: Dict[str, Union[int, str]], file_name: str, tmp_path: Path) -> Path:
    """Data written out as pickled binary to a file."""
    data_file_path = tmp_path / file_name
    with open(data_file_path, "wb") as f:
        pickle.dump(data, f)
    return data_file_path


@fixture
def file_data(data_file: Path) -> bytes:
    """Pickled data form when packed by msgpack."""
    with open(data_file, "rb") as f:
        return f.read()


@fixture
def bad_response_text() -> str:
    """Body text for a bad response."""
    return "BAD BODY"


@unit_test
class TestSynchronousS3Interactions:
    """Tests for the synchronous S3 interactions."""

    @responses.activate
    def test__upload_to_s3(
        self,
        file_name: str,
        packed_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests _upload_to_s3 works correctly.

        Data should be uploaded with the expected fields.
        """
        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields, files={"file": (file_name, packed_data)}
                )
            ],
        )

        _upload_to_s3(
            s3_upload_url, s3_upload_fields, to_upload=packed_data, file_name=file_name
        )

    @responses.activate
    def test__upload_to_s3_default_file_name(
        self,
        packed_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests _upload_to_s3 works correctly.

        Data should be uploaded with the expected fields.
        """
        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, packed_data)},
                )
            ],
        )

        _upload_to_s3(s3_upload_url, s3_upload_fields, to_upload=packed_data)

    @responses.activate
    def test__upload_to_s3_file_handler(
        self,
        packed_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        tmp_path: Path,
    ) -> None:
        """Tests _upload_to_s3 works correctly.

        Data should be uploaded with the expected fields.
        """
        with open(tmp_path / "packed_data", "wb") as f:
            f.write(packed_data)

        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, packed_data)},
                )
            ],
        )

        with open(tmp_path / "packed_data", "rb") as f:
            _upload_to_s3(s3_upload_url, s3_upload_fields, to_upload=f)

    @responses.activate
    def test__upload_to_s3_failure_request_exception(
        self,
        packed_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests _upload_to_s3 fails when RequestException encountered."""
        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, packed_data)},
                )
            ],
            body=RequestException(),
        )

        # Error message
        with pytest.raises(RequestException, match="Issue uploading object to S3$"):
            _upload_to_s3(s3_upload_url, s3_upload_fields, packed_data)

    @pytest.mark.parametrize(
        "status_code",
        (400, 404, 500),
    )
    @responses.activate
    def test__upload_to_s3_failure_status_code(
        self,
        bad_response_text: str,
        packed_data: bytes,
        remove_web_retry_backoff_sleep: Optional[Mock],
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        status_code: int,
    ) -> None:
        """Tests _upload_to_s3 fails when status code is 400+."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, packed_data)},
                )
            ],
            status=status_code,
            body=bad_response_text,
        )

        with pytest.raises(
            HTTPError,
            match=re.escape(
                f"Issue uploading object to S3: ({status_code}) {bad_response_text}"
            ),
        ):
            _upload_to_s3(s3_upload_url, s3_upload_fields, packed_data)

        # Check retries occurred if expected
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_web_retry_backoff_sleep.call_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            remove_web_retry_backoff_sleep.assert_not_called()

    @responses.activate
    def test__upload_to_s3_failure_non_ok_status_code(
        self,
        bad_response_text: str,
        packed_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests _upload_to_s3 fails when status code is not 200 or 201."""
        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, packed_data)},
                )
            ],
            status=300,
            body=bad_response_text,
        )

        with pytest.raises(
            HTTPError,
            match=re.escape(f"Issue uploading object to S3: (300) {bad_response_text}"),
        ):
            _upload_to_s3(s3_upload_url, s3_upload_fields, packed_data)

    @responses.activate
    def test_upload_data_to_s3(
        self,
        data: Dict[str, Union[int, str]],
        packed_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_data_to_s3 works correctly.

        Data should be packed and uploaded with the expected fields.
        """
        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, packed_data)},
                )
            ],
        )

        _upload_data_to_s3(s3_upload_url, s3_upload_fields, data=json.dumps(data))

    @responses.activate
    def test_upload_file_to_s3_with_path(
        self,
        data_file: Path,
        file_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_file_to_s3 works with file path."""
        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (data_file.name, file_data)},
                )
            ],
        )

        _upload_file_to_s3(s3_upload_url, s3_upload_fields, file_path=data_file)

    @responses.activate
    def test_upload_file_to_s3_with_path_and_file_name(
        self,
        custom_filename: str,
        data_file: Path,
        file_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_file_to_s3 works with file path and custom filename."""
        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (custom_filename, file_data)},
                )
            ],
        )

        _upload_file_to_s3(
            s3_upload_url,
            s3_upload_fields,
            file_path=data_file,
            file_name=custom_filename,
        )

    @responses.activate
    def test_upload_file_to_s3_with_str_file_contents(
        self,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_file_to_s3 works with string file-contents."""
        str_contents: str = "Hello, world!"
        bytes_contents: bytes = str_contents.encode("utf-8")

        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, bytes_contents)},
                )
            ],
        )

        _upload_file_to_s3(s3_upload_url, s3_upload_fields, file_contents=str_contents)

    @responses.activate
    def test_upload_file_to_s3_with_str_file_contents_and_custom_filename(
        self,
        custom_filename: str,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_file_to_s3 works with string file-contents and custom filename."""  # noqa: B950
        str_contents: str = "Hello, world!"
        bytes_contents: bytes = str_contents.encode("utf-8")

        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (custom_filename, bytes_contents)},
                )
            ],
        )

        _upload_file_to_s3(
            s3_upload_url,
            s3_upload_fields,
            file_contents=str_contents,
            file_name=custom_filename,
        )

    @responses.activate
    def test_upload_file_to_s3_with_str_file_contents_and_non_standard_encoding(
        self,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_file_to_s3 works with string file-contents and encoding."""
        str_contents: str = "Hello, world!"
        encoding = "ascii"
        bytes_contents: bytes = str_contents.encode(encoding)

        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, bytes_contents)},
                )
            ],
        )

        _upload_file_to_s3(
            s3_upload_url,
            s3_upload_fields,
            file_contents=str_contents,
            file_encoding=encoding,
        )

    @responses.activate
    def test_upload_file_to_s3_with_bytes_file_contents(
        self,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_file_to_s3 works with bytes file-contents."""
        bytes_contents: bytes = b"Hello World!"

        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (_DEFAULT_FILE_NAME, bytes_contents)},
                )
            ],
        )

        _upload_file_to_s3(
            s3_upload_url, s3_upload_fields, file_contents=bytes_contents
        )

    @responses.activate
    def test_upload_file_to_s3_with_bytes_file_contents_and_custom_filename(
        self,
        custom_filename: str,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_file_to_s3 works with bytes file-contents and custom filename."""  # noqa: B950
        bytes_contents: bytes = b"Hello World!"

        responses.add(
            method=responses.POST,
            url=s3_upload_url,
            match=[
                multipart_matcher(
                    data=s3_upload_fields,
                    files={"file": (custom_filename, bytes_contents)},
                )
            ],
        )

        _upload_file_to_s3(
            s3_upload_url,
            s3_upload_fields,
            file_contents=bytes_contents,
            file_name=custom_filename,
        )

    @responses.activate
    def test_upload_file_to_s3_fails_if_contents_and_path_provided(
        self,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests upload_file_to_s3 fails if incompatible args."""
        with pytest.raises(
            ValueError,
            match=re.escape(
                "One of file_path and file_contents must be provided, but not both."
            ),
        ):
            _upload_file_to_s3(
                s3_upload_url, s3_upload_fields, file_path=Mock(), file_contents=Mock()
            )

    @responses.activate
    def test__download_from_s3(
        self, packed_data: bytes, s3_download_url: _S3PresignedURL
    ) -> None:
        """Tests _download_from_s3 works.

        Should download data, which will match the original data.
        """
        responses.add(
            method=responses.GET,
            url=s3_download_url,
            body=packed_data,
        )

        downloaded_data = _download_from_s3(s3_download_url)

        assert downloaded_data == packed_data

    @responses.activate
    def test__download_from_s3_fails_request_exception(
        self,
        s3_download_url: _S3PresignedURL,
    ) -> None:
        """Tests _download_from_s3 fails when RequestException encountered."""
        responses.add(
            method=responses.GET,
            url=s3_download_url,
            body=RequestException(),
        )

        with pytest.raises(
            RequestException, match="Issue whilst retrieving data from S3$"
        ):
            _download_from_s3(s3_download_url)

    @pytest.mark.parametrize("status_code", (400, 404, 500))
    @responses.activate
    def test__download_from_s3_fails_status_code_bad(
        self,
        bad_response_text: str,
        remove_web_retry_backoff_sleep: Optional[Mock],
        s3_download_url: _S3PresignedURL,
        status_code: int,
    ) -> None:
        """Tests _download_from_s3 fails when status code is 400+."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        responses.add(
            method=responses.GET,
            url=s3_download_url,
            status=status_code,
            body=bad_response_text,
        )

        with pytest.raises(
            HTTPError,
            match=re.escape(
                f"Issue whilst retrieving data from S3:"
                f" ({status_code}) {bad_response_text}"
            ),
        ):
            _download_from_s3(s3_download_url)

        # Check retries occurred if expected
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_web_retry_backoff_sleep.call_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            remove_web_retry_backoff_sleep.assert_not_called()

    @responses.activate
    def test__download_from_s3_fails_status_code_not_good(
        self, bad_response_text: str, s3_download_url: _S3PresignedURL
    ) -> None:
        """Tests _download_from_s3 fails when status code is not 200/201."""
        responses.add(
            method=responses.GET,
            url=s3_download_url,
            status=202,
            body=bad_response_text,
        )

        with pytest.raises(
            HTTPError,
            match=re.escape(
                f"Issue whilst retrieving data from S3: (202) {bad_response_text}"
            ),
        ):
            _download_from_s3(s3_download_url)

    @responses.activate
    def test_download_data_from_s3(
        self,
        data: Dict[str, Union[int, str]],
        packed_data: bytes,
        s3_download_url: _S3PresignedURL,
    ) -> None:
        """Tests download_data_from_s3 works correctly.

        Data should be unpacked upon retrieval.
        """
        responses.add(
            method=responses.GET,
            url=s3_download_url,
            body=packed_data,
        )

        downloaded_data = _download_data_from_s3(s3_download_url)

        # Check was unpacked
        assert downloaded_data == json.dumps(data)

    @responses.activate
    def test_download_file_from_s3(
        self, packed_data: bytes, s3_download_url: _S3PresignedURL
    ) -> None:
        """Tests download_file_from_s3 works correctly.

        Data should be downloaded as is, and not encoded.
        """
        responses.add(
            method=responses.GET,
            url=s3_download_url,
            body=packed_data,
        )

        downloaded_data = _download_file_from_s3(s3_download_url)

        # Check was unpacked
        assert downloaded_data == packed_data

    @responses.activate
    def test_download_file_from_s3_with_encoding(
        self,
        s3_download_url: _S3PresignedURL,
    ) -> None:
        """Tests download_file_from_s3 works correctly with encoding.

        Retrieved data should be encoded as a string.
        """
        str_contents: str = "Hello, world!"
        bytes_contents: bytes = str_contents.encode("utf-8")

        responses.add(
            method=responses.GET,
            url=s3_download_url,
            body=bytes_contents,
        )

        downloaded_data = _download_file_from_s3(s3_download_url, encoding="utf-8")

        # Check was encoded correctly
        assert isinstance(downloaded_data, str)
        assert downloaded_data == str_contents

    def test_get_packed_data_object_size(
        self,
        data: Dict[str, Union[int, str]],
        packed_data: bytes,
    ) -> None:
        """Tests that get_packed_data_object_size works correctly."""
        expected_length = len(packed_data)

        assert _get_packed_data_object_size(json.dumps(data)) == expected_length

    @responses.activate
    def test_get_packed_data_object_size_corresponds_to_upload(
        self,
        data: Dict[str, Union[int, str]],
        packed_data: bytes,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests that get_packed_data_object_size matches upload size."""
        # Get output size and check it matches the packed data
        expected_length = _get_packed_data_object_size(json.dumps(data))
        assert len(packed_data) == expected_length

        # Do mocked upload to give us the request
        responses.add(
            method=responses.POST,
            url=s3_upload_url,
        )
        _upload_data_to_s3(s3_upload_url, s3_upload_fields, json.dumps(data))

        # Check request file size as actually uploaded
        request = responses.calls[0].request
        file_contents: Optional[bytes] = None
        # Extract file content bytes from the multipart/form-data request body
        mpd = MultipartDecoder(
            request.body, content_type=request.headers["content-type"]
        )
        # Find the file part of the body (will have "filename" in the disposition)
        for part in mpd.parts:
            content_disposition: bytes = part.headers[b"Content-Disposition"]
            if b"filename" in content_disposition:
                file_contents = part.content

        # Check that bytes length in request body matches expected_length
        assert file_contents is not None
        assert len(file_contents) == expected_length


@unit_test
class TestAsynchronousS3Interactions:
    """Tests for the asynchronous S3 interactions."""

    # -------------------------------------------------------------------------
    # TEST UPLOAD TO S3
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "status_code", storage._OK_UPLOAD_STATUS_CODES, ids=lambda x: f"status_code={x}"
    )
    async def test_async_upload_to_s3(
        self,
        file_name: str,
        httpx_mock: HTTPXMock,
        packed_data: bytes,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        status_code: int,
    ) -> None:
        """Tests _async_upload_to_s3 works correctly.

        Data should be uploaded with the expected fields.
        """
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        def custom_response(request: httpx.Request) -> httpx.Response:
            """Parse HTTP request, make assertions and return a response."""
            assert request.method == "POST"
            assert request.url == s3_upload_url
            assert "multipart/form-data" in request.headers["content-type"]
            assert file_name in request.read().decode("utf-8", errors="ignore")
            assert packed_data in request.content
            return httpx.Response(status_code=status_code)

        httpx_mock.add_callback(custom_response)

        await _async_upload_to_s3(
            s3_upload_url, s3_upload_fields, to_upload=packed_data, file_name=file_name
        )

    @pytest.mark.parametrize(
        "status_code",
        (s for s in _HTTP_STATUS_CODES if 400 <= s < 600),
        ids=lambda x: f"status_code={x}",
    )
    async def test_async_upload_to_s3_returns_bad_response(
        self,
        file_name: str,
        httpx_mock: HTTPXMock,
        packed_data: bytes,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        status_code: int,
    ) -> None:
        """Tests _async_upload_to_s3 works correctly when the response is bad."""
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        def custom_response(request: httpx.Request) -> httpx.Response:
            """Parse HTTP request, make assertions and return a response."""
            assert request.method == "POST"
            assert request.url == s3_upload_url
            assert "multipart/form-data" in request.headers["content-type"]
            assert file_name in request.read().decode("utf-8", errors="ignore")
            assert packed_data in request.content
            return httpx.Response(status_code=status_code)

        httpx_mock.add_callback(custom_response)

        with pytest.raises(
            HTTPError, match=re.escape(f"Issue uploading object to S3: ({status_code})")
        ):
            await _async_upload_to_s3(
                s3_upload_url,
                s3_upload_fields,
                to_upload=packed_data,
                file_name=file_name,
            )

        # If we expected automatic retry to be triggered, check it was
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_async_web_retry_backoff_sleep.await_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            assert remove_async_web_retry_backoff_sleep.await_count == 0

    @pytest.mark.parametrize(
        "status_code",
        (
            s
            for s in _HTTP_STATUS_CODES
            if 100 <= s < 400 and s not in storage._OK_UPLOAD_STATUS_CODES
        ),
        ids=lambda x: f"status_code={x}",
    )
    async def test_async_upload_to_s3_returns_unacceptable_response(
        self,
        file_name: str,
        httpx_mock: HTTPXMock,
        packed_data: bytes,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        status_code: int,
    ) -> None:
        """Tests _async_upload_to_s3 works correctly when the response is unacceptable.

        The response here is not necessarily bad such that it won't raise an exception
        when `raise_for_status` is called but has been defined as not ok by ourselves.
        """
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        httpx_mock.add_response(status_code=status_code)

        with pytest.raises(
            HTTPError, match=re.escape(f"Issue uploading object to S3: ({status_code})")
        ):
            await _async_upload_to_s3(
                s3_upload_url,
                s3_upload_fields,
                to_upload=packed_data,
                file_name=file_name,
            )

    @pytest.mark.parametrize(
        argnames=("exc_to_raise", "expected_exc_cls"),
        argvalues=(
            pytest.param(
                httpx.HTTPStatusError("TEST", request=Mock(), response=Mock()),
                requests.HTTPError,
                id="httpx.HTTPStatusError",
            ),
            pytest.param(
                httpx.ConnectError("TEST", request=Mock()),
                requests.ConnectionError,
                id="httpx.ConnectError",
            ),
            pytest.param(
                httpx.ReadTimeout("TEST", request=Mock()),
                requests.RequestException,
                id="httpx.ReadTimeout",
            ),
            # This exception results in different handling
            pytest.param(
                httpx.ConnectTimeout("TEST", request=Mock()),
                requests.RequestException,
                id="httpx.ConnectTimeout",
            ),
        ),
    )
    async def test_async_upload_to_s3_raises_exception(
        self,
        exc_to_raise: httpx.HTTPError,
        expected_exc_cls: Type[requests.RequestException],
        file_name: str,
        httpx_mock: HTTPXMock,
        packed_data: bytes,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests _async_upload_to_s3 handles exception when request is made.

        Tests that the exception is handled and re-raised.
        """
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        httpx_mock.add_exception(exc_to_raise)

        with pytest.raises(
            expected_exc_cls, match="Issue uploading object to S3.*TEST"
        ):
            await _async_upload_to_s3(
                s3_upload_url,
                s3_upload_fields,
                to_upload=packed_data,
                file_name=file_name,
            )

        # Check expected retry
        if isinstance(exc_to_raise, httpx.ConnectError):
            assert (
                remove_async_web_retry_backoff_sleep.await_count
                == web_utils._DEFAULT_MAX_RETRIES
            )

    async def test_async_upload_data_to_s3(
        self,
        data: Dict[str, Union[int, str]],
        mocker: MockerFixture,
        packed_data: bytes,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Tests _async_download_data_to_s3 works correctly."""
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        mock_async_upload = mocker.patch("bitfount.storage._async_upload_to_s3")
        await _async_upload_data_to_s3(
            s3_upload_url, s3_upload_fields, json.dumps(data)
        )
        mock_async_upload.assert_awaited_once_with(
            s3_upload_url, s3_upload_fields, packed_data
        )

    # -------------------------------------------------------------------------
    # TEST DOWNLOAD FROM S3
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "status_code",
        storage._OK_DOWNLOAD_STATUS_CODES,
        ids=lambda x: f"status_code={x}",
    )
    async def test_async_download_from_s3(
        self,
        httpx_mock: HTTPXMock,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_download_url: _S3PresignedURL,
        status_code: int,
    ) -> None:
        """Tests _async_download_from_s3 works correctly."""
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        def custom_response(request: httpx.Request) -> httpx.Response:
            """Parse HTTP request, make assertions and return a response."""
            assert request.method == "GET"
            assert request.url == s3_download_url
            return httpx.Response(status_code=status_code)

        httpx_mock.add_callback(custom_response)

        await _async_download_from_s3(s3_download_url)

    @pytest.mark.parametrize(
        "status_code",
        (s for s in _HTTP_STATUS_CODES if 400 <= s < 600),
        ids=lambda x: f"status_code={x}",
    )
    async def test_async_download_from_s3_returns_bad_response(
        self,
        httpx_mock: HTTPXMock,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_download_url: _S3PresignedURL,
        status_code: int,
    ) -> None:
        """Tests _async_download_from_s3 works correctly when the response is bad."""
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        def custom_response(request: httpx.Request) -> httpx.Response:
            """Parse HTTP request, make assertions and return a response."""
            assert request.method == "GET"
            assert request.url == s3_download_url
            return httpx.Response(status_code=status_code)

        httpx_mock.add_callback(custom_response)

        with pytest.raises(
            HTTPError,
            match=re.escape(f"Issue whilst retrieving data from S3: ({status_code})"),
        ):
            await _async_download_from_s3(s3_download_url)

    @pytest.mark.parametrize(
        "status_code",
        (
            s
            for s in _HTTP_STATUS_CODES
            if 100 <= s < 400 and s not in storage._OK_DOWNLOAD_STATUS_CODES
        ),
        ids=lambda x: f"status_code={x}",
    )
    async def test_async_download_from_s3_returns_unacceptable_response(
        self,
        httpx_mock: HTTPXMock,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_download_url: _S3PresignedURL,
        status_code: int,
    ) -> None:
        """Tests _async_download_from_s3 works when the response is unacceptable.

        The response here is not necessarily bad such that it won't raise an exception
        when `raise_for_status` is called but has been defined as not ok by ourselves.
        """
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        httpx_mock.add_response(status_code=status_code)

        with pytest.raises(
            HTTPError,
            match=re.escape(f"Issue whilst retrieving data from S3: ({status_code})"),
        ):
            await _async_download_from_s3(s3_download_url)

    @pytest.mark.parametrize(
        argnames=("exc_to_raise", "expected_exc_cls"),
        argvalues=(
            pytest.param(
                httpx.HTTPStatusError("TEST", request=Mock(), response=Mock()),
                requests.HTTPError,
                id="httpx.HTTPStatusError",
            ),
            pytest.param(
                httpx.ConnectError("TEST", request=Mock()),
                requests.ConnectionError,
                id="httpx.ConnectError",
            ),
            pytest.param(
                httpx.ReadTimeout("TEST", request=Mock()),
                requests.RequestException,
                id="httpx.ReadTimeout",
            ),
            # This exception results in different handling
            pytest.param(
                httpx.ConnectTimeout("TEST", request=Mock()),
                requests.RequestException,
                id="httpx.ConnectTimeout",
            ),
        ),
    )
    async def test_async_download_from_s3_raises_exception(
        self,
        exc_to_raise: httpx.HTTPError,
        expected_exc_cls: Type[requests.RequestException],
        httpx_mock: HTTPXMock,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_download_url: _S3PresignedURL,
    ) -> None:
        """Tests _async_download_from_s3 handles exception when request is made.

        Tests that the exception is handled and re-raised.
        """
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        httpx_mock.add_exception(exc_to_raise)

        with pytest.raises(
            expected_exc_cls, match="Issue whilst retrieving data from S3.*TEST"
        ):
            await _async_download_from_s3(s3_download_url)

        # Check expected retry
        if isinstance(exc_to_raise, httpx.ConnectError):
            assert (
                remove_async_web_retry_backoff_sleep.await_count
                == web_utils._DEFAULT_MAX_RETRIES
            )

    async def test_async_download_data_from_s3(
        self,
        data: Dict[str, Union[int, str]],
        mocker: MockerFixture,
        packed_data: bytes,
        remove_async_web_retry_backoff_sleep: Optional[AsyncMock],
        s3_download_url: _S3PresignedURL,
    ) -> None:
        """Tests _async_download_data_from_s3 works correctly."""
        # Check that backoff sleep has been correctly mocked
        assert remove_async_web_retry_backoff_sleep is not None

        mock_async_download = mocker.patch(
            "bitfount.storage._async_download_from_s3", return_value=packed_data
        )
        result = await _async_download_data_from_s3(s3_download_url)
        assert result == json.dumps(data)
        mock_async_download.assert_awaited_once_with(s3_download_url)
