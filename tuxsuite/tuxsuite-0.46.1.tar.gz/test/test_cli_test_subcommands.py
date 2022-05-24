# -*- coding: utf-8 -*-

import sys
import json
import pytest
from tuxsuite.cli.argparse import setup_parser
from tuxsuite.cli.requests import headers
from tuxsuite.cli.test import (
    handle_get,
    handle_list,
    handle_logs,
    handle_results,
    handle_wait,
    handle_submit,
)


@pytest.fixture
def test_json():
    test = {
        "project": "tuxsuite/senthil",
        "device": "qemu-x86_64",
        "uid": "1t2giU7PHbVdarV0ZFIohd0PvFb",
        "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
        "ap_romfw": None,
        "mcp_fw": None,
        "mcp_romfw": None,
        "modules": None,
        "parameters": None,
        "rootfs": None,
        "scp_fw": None,
        "scp_romfw": None,
        "fip": None,
        "tests": ["boot", "ltp-smoke"],
        "user": None,
        "user_agent": None,
        "state": "finished",
        "result": "pass",
        "results": {"boot": "pass", "ltp-smoke": "pass"},
        "plan": "1t2ghz9i7oeLHa2pW1a8EsR1RLP",
        "waiting_for": None,
        "boot_args": None,
        "provisioning_time": "2021-05-25T19:58:44.093685",
        "running_time": "2021-05-25T19:58:44.493457",
        "finished_time": "2021-05-25T19:59:45.311189",
        "duration": 61,
    }
    return json.dumps(test).encode("utf-8")


@pytest.fixture
def test_error_json():
    test = {
        "project": "tuxsuite/senthil",
        "device": "qemu-x86_64",
        "uid": "1t2giU7PHbVdarV0ZFIohd0PvFb",
        "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
        "ap_romfw": None,
        "mcp_fw": None,
        "mcp_romfw": None,
        "modules": None,
        "parameters": None,
        "rootfs": None,
        "scp_fw": None,
        "scp_romfw": None,
        "fip": None,
        "tests": ["boot", "ltp-smoke"],
        "user": None,
        "user_agent": None,
        "state": "finished",
        "result": "error",
        "results": {"boot": "pass", "ltp-smoke": "pass"},
        "plan": "1t2ghz9i7oeLHa2pW1a8EsR1RLP",
        "waiting_for": None,
        "boot_args": None,
        "provisioning_time": "2021-05-25T19:58:44.093685",
        "running_time": "2021-05-25T19:58:44.493457",
        "finished_time": "2021-05-25T19:59:45.311189",
        "duration": 61,
    }
    return json.dumps(test).encode("utf-8")


@pytest.fixture
def test_fail_json():
    test = {
        "project": "tuxsuite/senthil",
        "device": "qemu-x86_64",
        "uid": "1t2giU7PHbVdarV0ZFIohd0PvFb",
        "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
        "ap_romfw": None,
        "mcp_fw": None,
        "mcp_romfw": None,
        "modules": None,
        "parameters": None,
        "rootfs": None,
        "scp_fw": None,
        "scp_romfw": None,
        "fip": None,
        "tests": ["boot", "ltp-smoke"],
        "user": None,
        "user_agent": None,
        "state": "finished",
        "result": "fail",
        "results": {"boot": "pass", "ltp-smoke": "pass"},
        "plan": "1t2ghz9i7oeLHa2pW1a8EsR1RLP",
        "waiting_for": None,
        "boot_args": None,
        "provisioning_time": "2021-05-25T19:58:44.093685",
        "running_time": "2021-05-25T19:58:44.493457",
        "finished_time": "2021-05-25T19:59:45.311189",
        "duration": 61,
    }
    return json.dumps(test).encode("utf-8")


@pytest.fixture
def test_list_json():
    test_list = {
        "count": 1,
        "results": [
            {
                "project": "tuxsuite/senthil",
                "device": "qemu-i386",
                "uid": "1t2gzwpOVhU7ahus1FvS7swPeG7",
                "kernel": "https://storage.tuxboot.com/i386/bzImage",
                "ap_romfw": None,
                "mcp_fw": None,
                "mcp_romfw": None,
                "modules": None,
                "parameters": None,
                "rootfs": None,
                "scp_fw": None,
                "scp_romfw": None,
                "fip": None,
                "tests": ["boot", "ltp-smoke"],
                "user": None,
                "user_agent": None,
                "state": "finished",
                "result": "pass",
                "results": {"boot": "pass", "ltp-smoke": "pass"},
                "plan": "1t2gzLqkWHi2ldxDETNMVHPYBYo",
                "waiting_for": None,
                "boot_args": None,
                "provisioning_time": "2021-05-25T20:01:03.057613",
                "running_time": "2021-05-25T20:01:03.318610",
                "finished_time": "2021-05-25T20:01:54.490403",
                "duration": 51,
            }
        ],
        "next": None,
    }
    return json.dumps(test_list).encode("utf-8")


@pytest.fixture
def result_json():
    result = {
        "lava": {
            "validate": {"result": "pass"},
            "file-download": {
                "duration": "3.78",
                "level": "1.5.1",
                "namespace": "caommon",
                "result": "pass",
            },
            "test-overlay": {
                "duration": "0.00",
                "level": "1.1.3.2",
                "namespace": "common",
                "result": "pass",
            },
            "test-1": {
                "duration": "0.00",
                "level": "1.1.3.2",
                "namespace": "common",
                "result": "fail",
            },
            "test-2": {
                "duration": "0.00",
                "level": "1.1.3.2",
                "namespace": "common",
                "result": "error",
            },
        }
    }
    return json.dumps(result).encode("utf-8")


def test_test_handle_get(mocker, test_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = test_json
    get_req = mocker.patch("requests.get", return_value=response)
    result = handle_get(options, config)
    assert result == 0
    assert get_req.call_count == 1

    # Test json out
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFb", "--json"],
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = test_json
    get_req = mocker.patch("requests.get", return_value=response)
    result = handle_get(options, config)
    assert result == 0
    assert get_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        result = handle_get(options, config)
    assert get_req.call_count == 1


def test_test_handle_get_error(mocker, test_error_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = test_error_json
    get_req = mocker.patch("requests.get", return_value=response)
    result = handle_get(options, config)
    assert result == 0
    assert get_req.call_count == 1


def test_test_handle_get_fail(mocker, test_fail_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = test_fail_json
    get_req = mocker.patch("requests.get", return_value=response)
    result = handle_get(options, config)
    assert result == 0
    assert get_req.call_count == 1


def test_test_handle_list(mocker, test_list_json, config, response, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "test", "list"])
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = test_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exit:
        handle_list(options, config)
    assert exit.value.code == 0
    assert list_req.call_count == 2

    # Test json out
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "test", "list", "--json"])
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = test_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    handle_list(options, config)
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        handle_list(options, config)
    assert list_req.call_count == 1


def test_test_handle_logs(mocker, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "logs", "1yiYkYq26HbT5i304xElM5Czj2d"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = b"""- {"dt": "2021-09-27T09:58:08.499180", "lvl": "info", "msg": "msg-1"}
- {"dt": "2021-09-27T09:58:08.499454", "lvl": "info", "msg": "msg-2"}
- {"dt": "2021-09-27T09:58:08.500845", "lvl": "debug", "msg": "msg-3"}
"""
    logs_req = mocker.patch("requests.get", return_value=response)
    result = handle_logs(options, config)
    assert result == 0
    assert logs_req.call_count == 1

    # test raw output
    options.raw = True
    result = handle_logs(options, config)
    assert result == 0
    assert logs_req.call_count == 2

    # Test failure case when the response is not 200
    response.status_code = 500
    logs_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        result = handle_logs(options, config)
    assert logs_req.call_count == 1


def test_test_handle_results(mocker, config, result_json, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "results", "1yiYkYq26HbT5i304xElM5Czj2d"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = result_json
    logs_req = mocker.patch("requests.get", return_value=response)
    result = handle_results(options, config)
    assert result == 0
    assert logs_req.call_count == 1

    # test raw output
    options.raw = True
    result = handle_results(options, config)
    assert result == 0
    assert logs_req.call_count == 2

    # Test failure case when the response is not 200
    response.status_code = 500
    logs_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        result = handle_results(options, config)
    assert logs_req.call_count == 1


def test_test_handle_wait(mocker, test_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "wait", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = test_json
    wait_req = mocker.patch("requests.get", return_value=response)
    result = handle_wait(options, config)
    assert result == 0
    assert wait_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    wait_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        result = handle_wait(options, config)
    assert wait_req.call_count == 1


def test_test_handle_submit(mocker, config, response, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "test",
            "submit",
            "--device",
            "qemu-i386",
            "--kernel",
            "http://example.com/image/",
            "--tests",
            "ltp-smoke",
        ],
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 201
    response._content = b'{"a": "b"}'
    post_req = mocker.patch("requests.post", return_value=response)
    mocker.patch("tuxsuite.cli.models.Test.new", return_value={"a": "b"})
    handle_submit(options, config)
    post_req.assert_called_with(
        f"{config.tuxapi_url}/v1/groups/{config.group}/projects/{config.project}/tests",
        headers=headers(config),
        json={
            "device": "qemu-i386",
            "kernel": "http://example.com/image/",
            "tests": ["ltp-smoke"],
        },
    )
    assert post_req.call_count == 1

    # Test failure case when the response is not 201
    response.status_code = 500
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(NotImplementedError):
        handle_submit(options, config)
    assert post_req.call_count == 1
