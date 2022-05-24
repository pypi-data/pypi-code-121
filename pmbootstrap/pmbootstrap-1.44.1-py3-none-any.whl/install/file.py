# Copyright 2020 Pablo Castellano
# SPDX-License-Identifier: GPL-3.0-or-later
import logging

import pmb.config
import pmb.helpers.git


def write_os_release(args, suffix):
    logging.info("(" + suffix + ") write /etc/os-release")
    revision = pmb.helpers.git.rev_parse(args, args.aports)
    filepath = args.work + "/chroot_" + suffix + "/tmp/os-release"
    os_release = ('PRETTY_NAME="postmarketOS {version}"\n'
                  'NAME="postmarketOS"\n'
                  'VERSION_ID="{version}"\n'
                  'VERSION="{version}-{hash:.8}"\n'
                  'ID="postmarketos"\n'
                  'ID_LIKE="alpine"\n'
                  'HOME_URL="https://www.postmarketos.org/"\n'
                  'SUPPORT_URL="https://gitlab.com/postmarketOS"\n'
                  'BUG_REPORT_URL="https://gitlab.com/postmarketOS/pmbootstrap/issues"\n'
                  'PMOS_HASH="{hash}"\n'
                  ).format(version=pmb.config.version, hash=revision)
    with open(filepath, "w") as handle:
        handle.write(os_release)
    pmb.chroot.root(args, ["mv", "/tmp/os-release", "/etc/os-release"], suffix)
