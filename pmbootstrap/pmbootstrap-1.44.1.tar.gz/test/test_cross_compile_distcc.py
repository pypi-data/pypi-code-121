# Copyright 2022 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import pytest
import sys

import pmb_test  # noqa
import pmb.build
import pmb.chroot.distccd
import pmb.helpers.logging


@pytest.fixture
def args(tmpdir, request):
    import pmb.parse
    sys.argv = ["pmbootstrap", "init"]
    args = pmb.parse.arguments()
    args.log = args.work + "/log_testsuite.txt"
    pmb.helpers.logging.init(args)
    request.addfinalizer(pmb.helpers.logging.logfd.close)
    return args


def test_cross_compile_distcc(args):
    # Delete old distccd log
    pmb.chroot.distccd.stop(args)
    distccd_log = args.work + "/chroot_native/home/pmos/distccd.log"
    if os.path.exists(distccd_log):
        pmb.helpers.run.root(args, ["rm", distccd_log])

    # Force usage of distcc (no fallback, no ccache)
    args.verbose = True
    args.ccache = False
    args.distcc_fallback = False

    # Compile, print distccd and sshd logs on error
    try:
        pmb.build.package(args, "hello-world", arch="armhf", force=True)
    except RuntimeError:
        print("distccd log:")
        pmb.helpers.run.user(args, ["cat", distccd_log], output="stdout",
                             check=False)
        print("sshd log:")
        sshd_log = args.work + "/chroot_native/home/pmos/.distcc-sshd/log.txt"
        pmb.helpers.run.root(args, ["cat", sshd_log], output="stdout",
                             check=False)
        raise
