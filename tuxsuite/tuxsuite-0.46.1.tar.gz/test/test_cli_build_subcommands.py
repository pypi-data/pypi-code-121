# -*- coding: utf-8 -*-

import sys
import json
import pytest
from tuxsuite.cli.argparse import setup_parser
from tuxsuite.cli.build import (
    handle_config,
    handle_get,
    handle_list,
    handle_logs,
    handle_wait,
)


@pytest.fixture
def build_json():
    build = {
        "project": "tuxsuite/senthil",
        "uid": "205Yag6znViIi4oLWFVDxJC4avb",
        "plan": None,
        "kconfig": ["tinyconfig"],
        "target_arch": "i386",
        "toolchain": "gcc-9",
        "build_name": "",
        "client_token": "7c76a710-57e4-4f67-84e2-bc592b3f18d9",
        "environment": {},
        "make_variables": {},
        "targets": [],
        "git_repo": "https://github.com/Linaro/linux-canaries.git",
        "git_ref": "v5.9",
        "git_sha": "bbf5c979011a099af5dc76498918ed7df445635b",
        "download_url": "https://builds.stylesen.dev.tuxbuild.com/205Yag6znViIi4oLWFVDxJC4avb/",
        "kernel_image": "",
        "user": "senthil.kumaran@linaro.org",
        "state": "finished",
        "result": "pass",
        "waited_by": [],
        "errors_count": 0,
        "warnings_count": 2,
        "provisioning_time": "2021-10-27T11:59:40.574911",
        "running_time": "2021-10-27T12:01:10.929870",
        "finished_time": "2021-10-27T12:03:22.168886",
        "duration": 131,
        "kernel_version": "5.9.0",
        "kernel_image_name": "bzImage",
        "status_message": "build completed",
        "git_describe": "v5.9",
    }
    return json.dumps(build).encode("utf-8")


@pytest.fixture
def build_list_json():
    build_list = {
        "count": 1,
        "results": [
            {
                "project": "tuxsuite/senthil",
                "uid": "207i1AaccpFZvAMsGFfjas952dX",
                "plan": None,
                "kconfig": ["tinyconfig"],
                "target_arch": "arm64",
                "toolchain": "gcc-10",
                "build_name": "",
                "client_token": "4f30586f-1ca9-4242-bb41-7fe9e2be8a78",
                "environment": {},
                "make_variables": {},
                "targets": [],
                "git_repo": "https://github.com/torvalds/linux.git",
                "git_ref": "master",
                "git_sha": "1fc596a56b334f4d593a2b49e5ff55af6aaa0816",
                "download_url": "https://builds.stylesen.dev.tuxbuild.com/207i1AaccpFZvAMsGFfjas952dX/",
                "kernel_image": "",
                "user": "senthil.kumaran@linaro.org",
                "state": "finished",
                "result": "pass",
                "waited_by": [],
                "errors_count": 0,
                "warnings_count": 0,
                "provisioning_time": "2021-10-28T06:16:48.279774",
                "running_time": "2021-10-28T06:19:06.621554",
                "finished_time": "2021-10-28T06:22:58.242564",
                "duration": 233,
                "build_status": "pass",
                "kernel_version": "5.15.0-rc7",
                "kernel_image_name": "Image.gz",
                "status_message": "build completed",
                "git_describe": "v5.15-rc7-33-g1fc596a56b33",
            }
        ],
        "next": None,
    }
    return json.dumps(build_list).encode("utf-8")


def test_build_handle_config(mocker, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "config", "205Yag6znViIi4oLWFVDxJC4avb"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = b'{"download_url": "b"}'
    config_req = mocker.patch("requests.get", return_value=response)
    result = handle_config(options, config)
    assert result == 0
    assert config_req.call_count == 2

    # Test failure case when the response is not 200
    response.status_code = 500
    config_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        result = handle_config(options, config)
    assert config_req.call_count == 1


def test_build_handle_get(mocker, build_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "get", "205Yag6znViIi4oLWFVDxJC4avb"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    result = handle_get(options, config)
    assert result == 0
    assert get_req.call_count == 1

    # Test json out
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "build", "get", "205Yag6znViIi4oLWFVDxJC4avb", "--json"],
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = build_json
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


def test_build_handle_list(mocker, build_list_json, config, response, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "build", "list"])
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = build_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exit:
        handle_list(options, config)
    assert exit.value.code == 0
    assert list_req.call_count == 2

    # Test json out
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "build", "list", "--json"])
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = build_list_json
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


def test_build_handle_logs(mocker, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "logs", "205Yag6znViIi4oLWFVDxJC4avb"]
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = b'{"download_url": "b"}'
    logs_req = mocker.patch("requests.get", return_value=response)
    result = handle_logs(options, config)
    assert result == 0
    assert logs_req.call_count == 2

    # Test failure case when the response is not 200
    response.status_code = 500
    logs_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        result = handle_logs(options, config)
    assert logs_req.call_count == 1

    # Test when log is unavailable - due to infra error
    response.status_code = 404
    logs_req = mocker.patch("requests.get", return_value=response)
    result = handle_logs(options, config)
    assert result == 0
    assert logs_req.call_count == 1


def test_build_handle_wait(mocker, build_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "build", "wait", "205Yag6znViIi4oLWFVDxJC4avb"],
    )
    options = setup_parser(config.group, config.project).parse_args()
    response.status_code = 200
    response._content = build_json
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
