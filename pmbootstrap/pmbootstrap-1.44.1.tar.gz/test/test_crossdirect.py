# Copyright 2022 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import sys

import pmb_test  # noqa
import pmb.chroot.apk_static
import pmb.config.pmaports
import pmb.parse.apkindex
import pmb.helpers.logging
import pmb.helpers.run
import pmb.parse.bootimg


@pytest.fixture
def args(request):
    import pmb.parse
    sys.argv = ["pmbootstrap.py", "chroot"]
    args = pmb.parse.arguments()
    args.log = args.work + "/log_testsuite.txt"
    pmb.helpers.logging.init(args)
    request.addfinalizer(pmb.helpers.logging.logfd.close)
    return args


def pmbootstrap_run(args, parameters, check=True):
    """Execute pmbootstrap.py with a test pmbootstrap.conf."""
    return pmb.helpers.run.user(args, ["./pmbootstrap.py"] + parameters,
                                working_dir=pmb.config.pmb_src,
                                check=check)


def test_crossdirect_rust(args):
    """ Set up buildroot_armv7 chroot for building, but remove /usr/bin/rustc.
        Build hello-world-rust for armv7, to verify that it uses
        /native/usr/bin/rustc instead of /usr/bin/rustc. The package has a
        check() function, which makes sure that the built program is actually
        working. """
    pmbootstrap_run(args, ["-y", "zap"])

    # Remember previously selected device
    cfg = pmb.config.load(args)
    old_device = cfg['pmbootstrap']['device']

    try:
        # First, switch to device that is known to exist on all channels,
        # such as qemu-amd64. Currently selected device may not exist in
        # stable branch!
        cfg['pmbootstrap']['device'] = 'qemu-amd64'
        pmb.config.save(args, cfg)

        # Switch to "v20.05" channel, as a stable release of alpine is more
        # likely to have the same rustc version across various architectures.
        # If armv7/x86_64 have a different rustc version, this test will fail:
        # 'found crate `std` compiled by an incompatible version of rustc'
        pmb.config.pmaports.switch_to_channel_branch(args, "v21.03")

        pmbootstrap_run(args, ["build_init", "-barmv7"])
        pmbootstrap_run(args, ["chroot", "--add=rust", "-barmv7", "--",
                               "mv", "/usr/bin/rustc", "/usr/bin/rustc_"])
        pmbootstrap_run(args, ["build", "hello-world-rust", "--arch=armv7",
                               "--force"])
        # Make /native/usr/bin/rustc unusuable too, to make the build fail
        pmbootstrap_run(args, ["chroot", "--", "rm", "/usr/bin/rustc"])
        assert pmbootstrap_run(args, ["build", "hello-world-rust",
                                      "--arch=armv7", "--force"],
                               check=False) == 1

        # Make /usr/bin/rustc usable again, to test fallback with qemu
        pmbootstrap_run(args, ["chroot", "-barmv7", "--",
                               "mv", "/usr/bin/rustc_", "/usr/bin/rustc"])
        pmbootstrap_run(args, ["build", "hello-world-rust", "--arch=armv7",
                               "--force"])
    finally:
        # Clean up
        pmb.config.pmaports.switch_to_channel_branch(args, "edge")
        pmbootstrap_run(args, ["-y", "zap"])

        # Restore previously selected device
        cfg['pmbootstrap']['device'] = old_device
        pmb.config.save(args, cfg)
