# -*- coding: utf-8 -*-

from tuxsuite.gitutils import public_git_url
from tuxsuite.gitutils import get_tuxsuite_remote
from tuxsuite.gitutils import get_remote_url
from tuxsuite.gitutils import get_head
from tuxsuite.gitutils import push_head
from tuxsuite.gitutils import get_git_head

import pytest


class TestPublicGitUrl:
    def test_github_ssh(self):
        out = public_git_url("git@github.com:foo/linux.git")
        assert out == "https://github.com/foo/linux.git"

    def test_github_https(self):
        out = public_git_url("https://github.com/foo/linux.git")
        assert out == "https://github.com/foo/linux.git"

    def test_https(self):
        out = public_git_url("https://git.example.com/linux.git")
        assert out == "https://git.example.com/linux.git"

    def test_https_subpath(self):
        out = public_git_url("https://git.example.com/foo/bar/linux.git")
        assert out == "https://git.example.com/foo/bar/linux.git"


@pytest.fixture
def check_output(mocker):
    return mocker.patch("tuxsuite.gitutils.check_output")


def test_get_tuxsuite_remote(check_output):
    check_output.return_value = "foobar\n"
    assert get_tuxsuite_remote() == "foobar"


def test_get_remote_url(check_output):
    check_output.return_value = "git@foo.com/foo/linux.git\n"
    assert get_remote_url("myremote") == "git@foo.com/foo/linux.git"
    check_output.assert_called_with(["git", "remote", "get-url", "myremote"], text=True)


def test_get_head(check_output):
    check_output.return_value = "deafbee\n"
    assert get_head() == "deafbee"
    check_output.assert_called_with(["git", "rev-parse", "HEAD"], text=True)


def test_push_head(mocker):
    check_call = mocker.patch("tuxsuite.gitutils.check_call")
    push_head("theremote", "deafbee")
    check_call.assert_called_with(
        ["git", "push", "theremote", "HEAD:refs/tuxsuite/deafbee"]
    )


def test_get_git_head(mocker):
    get_tuxsuite_remote = mocker.patch("tuxsuite.gitutils.get_tuxsuite_remote")
    get_tuxsuite_remote.return_value = "origin"

    url = "https://git.example.com/foo/linux.git"
    get_remote_url = mocker.patch("tuxsuite.gitutils.get_remote_url")
    get_remote_url.return_value = url

    get_head = mocker.patch("tuxsuite.gitutils.get_head")
    get_head.return_value = "deafbee"

    push_head = mocker.patch("tuxsuite.gitutils.push_head")

    assert get_git_head() == (url, "deafbee")
    get_tuxsuite_remote.assert_called()
    get_remote_url.assert_called_with("origin")
    get_head.assert_called()
    push_head.assert_called_with("origin", "deafbee")
