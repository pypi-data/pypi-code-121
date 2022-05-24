# Copyright 2022 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import sys

import pmb_test  # noqa
import pmb.chroot.apk


@pytest.fixture
def args(tmpdir, request):
    import pmb.parse
    sys.argv = ["pmbootstrap.py", "init"]
    args = pmb.parse.arguments()
    args.log = args.work + "/log_testsuite.txt"
    pmb.helpers.logging.init(args)
    request.addfinalizer(pmb.helpers.logging.logfd.close)
    return args


def test_install_is_necessary(args):
    # osk-sdl not installed, nothing to do
    ret = pmb.chroot.apk.install_is_necessary(args, False, "aarch64",
                                              "!osk-sdl",
                                              {"unl0kr": {"unl0kr": {}}})
    assert not ret

    # osk-sdl installed, (un)install necessary
    ret = pmb.chroot.apk.install_is_necessary(args, False, "aarch64",
                                              "!osk-sdl",
                                              {"osk-sdl": {"osk-sdl": {}}})
    assert ret
