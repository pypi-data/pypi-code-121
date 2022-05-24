# -*- coding: utf-8 -*-

import tuxsuite.requests
import pytest


@pytest.fixture(autouse=True)
def reset_seen_warnings():
    tuxsuite.requests.__seen_warnings__.clear()


def test_warnings_on_get(get, response, capsys):
    response.headers = {"X-Tuxsuite-Warning-1": "Something is wrong"}
    tuxsuite.requests.get("https://example.com")
    _, err = capsys.readouterr()
    assert "WARNING: Something is wrong" in err


def test_warnings_on_get_wont_repeat_warnings(get, response, capsys):
    response.headers = {
        "X-Tuxsuite-Warning-1": "Something is wrong",
        "X-Tuxsuite-Warning-2": "Something is wrong",
    }
    tuxsuite.requests.get("https://example.com")
    tuxsuite.requests.get("https://example.com")
    _, err = capsys.readouterr()
    warnings = [line for line in err.split("\n") if line.startswith("WARNING:")]
    assert len(warnings) == 1


def test_warnings_on_post(post, response, capsys):
    response.headers = {"X-Tuxsuite-Warning-1": "Something is wrong"}
    tuxsuite.requests.post("https://example.com")
    _, err = capsys.readouterr()
    assert "WARNING: Something is wrong" in err
