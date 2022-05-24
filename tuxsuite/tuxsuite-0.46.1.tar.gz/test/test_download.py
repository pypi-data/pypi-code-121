# -*- coding: utf-8 -*-

from io import BytesIO
import json
import pytest
from tuxsuite.download import download
from tuxsuite.download import download_file


@pytest.fixture
def build(mocker):
    b = mocker.MagicMock()
    b.uid = "4c6f477bf568ea2ad409fd68a404492f"
    b.build_data = "https://builds.test/4c6f477bf568ea2ad409fd68a404492f/"
    return b


def test_download(build, get, response, mocker, tmp_path):
    download_file = mocker.patch("tuxsuite.download.download_file")
    response._content = bytes(
        json.dumps(
            {
                "files": [
                    {
                        "Url": "https://builds.test/4c6f477bf568ea2ad409fd68a404492f/status.json"
                    },
                    {
                        "Url": "https://builds.test/4c6f477bf568ea2ad409fd68a404492f/build.log"
                    },
                ]
            }
        ),
        "utf-8",
    )
    download(build, tmp_path)
    assert download_file.call_count == 2


def test_download_file(get, response, tmp_path):
    dest = tmp_path / "foo.txt"
    response.raw = BytesIO(b"Hello World\n")
    with dest.open("wb") as f:
        download_file("https://builds.test/12312321/foo.txt", f)
    assert dest.read_text() == "Hello World\n"
