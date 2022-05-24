# Copyright 2022 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import pmb.config
import pmb.chroot.apk
import pmb.helpers.mount


def init(args):
    # Validate method
    if hasattr(args, 'flash_method'):
        method = args.flash_method or args.deviceinfo["flash_method"]
    else:
        method = args.deviceinfo["flash_method"]

    if method not in pmb.config.flashers:
        raise RuntimeError(f"Flash method {method} is not supported by the"
                           " current configuration. However, adding a new"
                           " flash method is not that hard, when the flashing"
                           " application already exists.\n"
                           "Make sure, it is packaged for Alpine Linux, or"
                           " package it yourself, and then add it to"
                           " pmb/config/__init__.py.")
    cfg = pmb.config.flashers[method]

    # Install depends
    pmb.chroot.apk.install(args, cfg["depends"])

    # Mount folders from host system
    for folder in pmb.config.flash_mount_bind:
        pmb.helpers.mount.bind(args, folder, args.work +
                               "/chroot_native" + folder)

    # Mount device chroot inside native chroot (required for kernel/ramdisk)
    mountpoint = "/mnt/rootfs_" + args.device
    pmb.helpers.mount.bind(args, args.work + "/chroot_rootfs_" + args.device,
                           args.work + "/chroot_native" + mountpoint)
