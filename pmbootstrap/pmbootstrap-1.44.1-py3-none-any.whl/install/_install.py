# Copyright 2022 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import re
import glob
import shlex

import pmb.chroot
import pmb.chroot.apk
import pmb.chroot.other
import pmb.chroot.initfs
import pmb.config
import pmb.config.pmaports
import pmb.helpers.devices
import pmb.helpers.run
import pmb.install.blockdevice
import pmb.install.recovery
import pmb.install.ui
import pmb.install


def mount_device_rootfs(args, suffix_rootfs, suffix_mount="native"):
    """
    Mount the device rootfs.
    :param suffix_rootfs: the chroot suffix, where the rootfs that will be
                          installed on the device has been created (e.g.
                          "rootfs_qemu-amd64")
    :param suffix_mount: the chroot suffix, where the device rootfs will be
                         mounted (e.g. "native")
    """
    mountpoint = f"/mnt/{suffix_rootfs}"
    pmb.helpers.mount.bind(args, f"{args.work}/chroot_{suffix_rootfs}",
                           f"{args.work}/chroot_{suffix_mount}{mountpoint}")
    return mountpoint


def get_subpartitions_size(args, suffix):
    """
    Calculate the size of the boot and root subpartition.

    :param suffix: the chroot suffix, e.g. "rootfs_qemu-amd64"
    :returns: (boot, root) the size of the boot and root
              partition as integer in MiB
    """
    boot = int(args.boot_size)

    # Estimate root partition size, then add some free space. The size
    # calculation is not as trivial as one may think, and depending on the
    # file system etc it seems to be just impossible to get it right.
    chroot = f"{args.work}/chroot_{suffix}"
    root = pmb.helpers.other.folder_size(args, chroot) / 1024
    root *= 1.20
    root += 50 + int(args.extra_space)
    return (boot, root)


def get_nonfree_packages(args, device):
    """
    Get the non-free packages based on user's choice in "pmbootstrap init" and
    based on whether there are non-free packages in the APKBUILD or not.

    :returns: list of non-free packages to be installed. Example:
              ["device-nokia-n900-nonfree-firmware"]
    """
    # Read subpackages
    apkbuild = pmb.parse.apkbuild(pmb.helpers.devices.find_path(args, device,
                                                                'APKBUILD'))
    subpackages = apkbuild["subpackages"]

    # Check for firmware and userland
    ret = []
    prefix = "device-" + device + "-nonfree-"
    if args.nonfree_firmware and prefix + "firmware" in subpackages:
        ret += [prefix + "firmware"]
    if args.nonfree_userland and prefix + "userland" in subpackages:
        ret += [prefix + "userland"]
    return ret


def get_kernel_package(args, device):
    """
    Get the device's kernel subpackage based on the user's choice in
    "pmbootstrap init".

    :param device: code name, e.g. "sony-amami"
    :returns: [] or the package in a list, e.g.
              ["device-sony-amami-kernel-mainline"]
    """
    # Empty list: single kernel devices / "none" selected
    kernels = pmb.parse._apkbuild.kernels(args, device)
    if not kernels or args.kernel == "none":
        return []

    # Sanity check
    if args.kernel not in kernels:
        raise RuntimeError("Selected kernel (" + args.kernel + ") is not"
                           " valid for device " + device + ". Please"
                           " run 'pmbootstrap init' to select a valid kernel.")

    # Selected kernel subpackage
    return ["device-" + device + "-kernel-" + args.kernel]


def copy_files_from_chroot(args, suffix):
    """
    Copy all files from the rootfs chroot to /mnt/install, except
    for the home folder (because /home will contain some empty
    mountpoint folders).

    :param suffix: the chroot suffix, e.g. "rootfs_qemu-amd64"
    """
    # Mount the device rootfs
    logging.info(f"(native) copy {suffix} to /mnt/install/")
    mountpoint = mount_device_rootfs(args, suffix)
    mountpoint_outside = args.work + "/chroot_native" + mountpoint

    # Remove empty qemu-user binary stub (where the binary was bind-mounted)
    arch_qemu = pmb.parse.arch.alpine_to_qemu(args.deviceinfo["arch"])
    qemu_binary = mountpoint_outside + "/usr/bin/qemu-" + arch_qemu + "-static"
    if os.path.exists(qemu_binary):
        pmb.helpers.run.root(args, ["rm", qemu_binary])

    # Remove apk progress fifo
    fifo = f"{args.work}/chroot_{suffix}/tmp/apk_progress_fifo"
    if os.path.exists(fifo):
        pmb.helpers.run.root(args, ["rm", fifo])

    # Get all folders inside the device rootfs (except for home)
    folders = []
    for path in glob.glob(mountpoint_outside + "/*"):
        if path.endswith("/home"):
            continue
        folders += [os.path.basename(path)]

    # Update or copy all files
    if args.rsync:
        pmb.chroot.apk.install(args, ["rsync"])
        rsync_flags = "-a"
        if args.verbose:
            rsync_flags += "vP"
        pmb.chroot.root(args, ["rsync", rsync_flags, "--delete"] + folders +
                        ["/mnt/install/"], working_dir=mountpoint)
        pmb.chroot.root(args, ["rm", "-rf", "/mnt/install/home"])
    else:
        pmb.chroot.root(args, ["cp", "-a"] + folders + ["/mnt/install/"],
                        working_dir=mountpoint)


def create_home_from_skel(args):
    """
    Create /home/{user} from /etc/skel
    """
    rootfs = args.work + "/chroot_native/mnt/install"
    homedir = rootfs + "/home/" + args.user
    pmb.helpers.run.root(args, ["mkdir", rootfs + "/home"])
    if os.path.exists(f"{rootfs}/etc/skel"):
        pmb.helpers.run.root(args, ["cp", "-a", f"{rootfs}/etc/skel", homedir])
    else:
        pmb.helpers.run.root(args, ["mkdir", homedir])
    pmb.helpers.run.root(args, ["chown", "-R", "10000", homedir])


def configure_apk(args):
    """
    Copy over all official keys, and the keys used to compile local packages
    (unless --no-local-pkgs is set). Then disable the /mnt/pmbootstrap-packages
    repository.
    """
    # Official keys
    pattern = f"{pmb.config.apk_keys_path}/*.pub"

    # Official keys + local keys
    if args.install_local_pkgs:
        pattern = f"{args.work}/config_apk_keys/*.pub"

    # Copy over keys
    rootfs = args.work + "/chroot_native/mnt/install"
    for key in glob.glob(pattern):
        pmb.helpers.run.root(args, ["cp", key, rootfs + "/etc/apk/keys/"])

    # Disable pmbootstrap repository
    pmb.helpers.run.root(args, ["sed", "-i", r"/\/mnt\/pmbootstrap-packages/d",
                                rootfs + "/etc/apk/repositories"])
    pmb.helpers.run.user(args, ["cat", rootfs + "/etc/apk/repositories"])


def set_user(args):
    """
    Create user with UID 10000 if it doesn't exist.
    Usually the ID for the first user created is 1000, but higher ID is
    chosen here to not cause issues with existing installations. Historically,
    this was done to avoid conflict with Android UIDs/GIDs, but pmOS has since
    dropped support for hybris/Halium.
    """
    suffix = "rootfs_" + args.device
    if not pmb.chroot.user_exists(args, args.user, suffix):
        pmb.chroot.root(args, ["adduser", "-D", "-u", "10000", args.user],
                        suffix)
    groups = pmb.install.ui.get_groups(args) + pmb.config.install_user_groups
    for group in groups:
        pmb.chroot.root(args, ["addgroup", "-S", group], suffix,
                        check=False)
        pmb.chroot.root(args, ["addgroup", args.user, group], suffix)


def setup_login_chpasswd_user_from_arg(args, suffix):
    """
    Set the user's password from what the user passed as --password. Make an
    effort to not have the password end up in the log file by writing it to
    a temp file, instead of "echo user:$pass | chpasswd". The user should of
    course only use this with a test password anyway, but let's be nice and try
    to have the user protected from accidentally posting their password in
    any case.

    :param suffix: of the chroot, where passwd will be execute (either the
                   f"rootfs_{args.device}", or f"installer_{args.device}")
    """
    path = "/tmp/pmbootstrap_chpasswd_in"
    path_outside = f"{args.work}/chroot_{suffix}{path}"

    with open(path_outside, "w", encoding="utf-8") as handle:
        handle.write(f"{args.user}:{args.password}")

    pmb.chroot.root(args, ["sh", "-c", f"cat {shlex.quote(path)} | chpasswd"],
                    suffix)

    os.unlink(path_outside)


def is_root_locked(args, suffix):
    """
    Figure out from /etc/shadow if root is already locked. The output of this
    is stored in the log, so use grep to only log the line for root, not the
    line for the user which contains a hash of the user's password.

    :param suffix: either rootfs_{args.device} or installer_{args.device}
    """
    shadow_root = pmb.chroot.root(args, ["grep", "^root:!:", "/etc/shadow"],
                                  suffix, output_return=True, check=False)
    return shadow_root.startswith("root:!:")


def setup_login(args, suffix):
    """
    Loop until the password for user has been set successfully, and disable
    root login.

    :param suffix: of the chroot, where passwd will be execute (either the
                   f"rootfs_{args.device}", or f"installer_{args.device}")
    """
    if not args.on_device_installer:
        # User password
        logging.info(f" *** SET LOGIN PASSWORD FOR: '{args.user}' ***")
        if args.password:
            setup_login_chpasswd_user_from_arg(args, suffix)
        else:
            while True:
                try:
                    pmb.chroot.root(args, ["passwd", args.user], suffix,
                                    output="interactive")
                    break
                except RuntimeError:
                    logging.info("WARNING: Failed to set the password. Try it"
                                 " one more time.")

    # Disable root login
    if is_root_locked(args, suffix):
        logging.debug(f"({suffix}) root is already locked")
    else:
        logging.debug(f"({suffix}) locking root")
        pmb.chroot.root(args, ["passwd", "-l", "root"], suffix)


def copy_ssh_keys(args):
    """
    If requested, copy user's SSH public keys to the device if they exist
    """
    if not args.ssh_keys:
        return
    keys = []
    for key in glob.glob(os.path.expanduser(args.ssh_key_glob)):
        with open(key, "r") as infile:
            keys += infile.readlines()

    if not len(keys):
        logging.info("NOTE: Public SSH keys not found. Since no SSH keys "
                     "were copied, you will need to use SSH password "
                     "authentication!")
        return

    authorized_keys = args.work + "/chroot_native/tmp/authorized_keys"
    outfile = open(authorized_keys, "w")
    for key in keys:
        outfile.write("%s" % key)
    outfile.close()

    target = f"{args.work}/chroot_native/mnt/install/home/{args.user}/.ssh"
    pmb.helpers.run.root(args, ["mkdir", target])
    pmb.helpers.run.root(args, ["chmod", "700", target])
    pmb.helpers.run.root(args, ["cp", authorized_keys, target +
                                "/authorized_keys"])
    pmb.helpers.run.root(args, ["rm", authorized_keys])
    pmb.helpers.run.root(args, ["chown", "-R", "10000:10000", target])


def setup_keymap(args):
    """
    Set the keymap with the setup-keymap utility if the device requires it
    """
    suffix = "rootfs_" + args.device
    info = pmb.parse.deviceinfo(args, device=args.device)
    if "keymaps" not in info or info["keymaps"].strip() == "":
        logging.info("NOTE: No valid keymap specified for device")
        return
    options = info["keymaps"].split(' ')
    if (args.keymap != "" and
            args.keymap is not None and
            args.keymap in options):
        layout, variant = args.keymap.split("/")
        pmb.chroot.root(args, ["setup-keymap", layout, variant], suffix,
                        output="interactive")

        # Check xorg config
        config = None
        if os.path.exists(f"{args.work}/chroot_{suffix}/etc/X11/xorg.conf.d"):
            config = pmb.chroot.root(args, ["grep", "-rl", "XkbLayout",
                                            "/etc/X11/xorg.conf.d/"],
                                     suffix, check=False, output_return=True)
        if config:
            # Nokia n900 (RX-51) randomly merges some keymaps so we
            # have to specify a composite keymap for a few countries. See:
            # https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/blob/master/symbols/nokia_vndr/rx-51
            if variant == "rx51_fi" or variant == "rx51_se":
                layout = "fise"
            if variant == "rx51_da" or variant == "rx51_no":
                layout = "dano"
            if variant == "rx51_pt" or variant == "rx51_es":
                layout = "ptes"
            # Multiple files can contain the keyboard layout, take last
            config = config.splitlines()[-1]
            old_text = "Option *\\\"XkbLayout\\\" *\\\".*\\\""
            new_text = "Option \\\"XkbLayout\\\" \\\"" + layout + "\\\""
            pmb.chroot.root(args, ["sed", "-i", "s/" + old_text + "/" +
                            new_text + "/", config], suffix)
    else:
        logging.info("NOTE: No valid keymap specified for device")


def setup_hostname(args):
    """
    Set the hostname and update localhost address in /etc/hosts
    """
    # Default to device name
    hostname = args.hostname
    if not hostname:
        hostname = args.device

    if not pmb.helpers.other.validate_hostname(hostname):
        raise RuntimeError("Hostname '" + hostname + "' is not valid, please"
                           " run 'pmbootstrap init' to configure it.")

    suffix = "rootfs_" + args.device
    # Generate /etc/hostname
    pmb.chroot.root(args, ["sh", "-c", "echo " + shlex.quote(hostname) +
                           " > /etc/hostname"], suffix)
    # Update /etc/hosts
    regex = (r"s/^127\.0\.0\.1.*/127.0.0.1\t" + re.escape(hostname) +
             " localhost.localdomain localhost/")
    pmb.chroot.root(args, ["sed", "-i", "-e", regex, "/etc/hosts"], suffix)


def disable_sshd(args):
    if not args.no_sshd:
        return

    # check=False: rc-update doesn't exit with 0 if already disabled
    suffix = f"rootfs_{args.device}"
    pmb.chroot.root(args, ["rc-update", "del", "sshd", "default"], suffix,
                    check=False)

    # Verify that it's gone
    sshd_files = pmb.helpers.run.root(
        args, ["find", "-name", "sshd"], output_return=True,
        working_dir=f"{args.work}/chroot_{suffix}/etc/runlevels")
    if sshd_files:
        raise RuntimeError(f"Failed to disable sshd service: {sshd_files}")


def print_sshd_info(args):
    logging.info("")  # make the note stand out
    logging.info("*** SSH DAEMON INFORMATION ***")

    if not args.ondev_no_rootfs:
        if args.no_sshd:
            logging.info("SSH daemon is disabled (--no-sshd).")
        else:
            logging.info("SSH daemon is enabled (disable with --no-sshd).")
            logging.info(f"Login as '{args.user}' with the password given"
                         " during installation.")

    if args.on_device_installer:
        # We don't disable sshd in the installer OS. If the device is reachable
        # on the network by default (e.g. Raspberry Pi), one can lock down the
        # installer OS down by disabling the debug user (see wiki page).
        logging.info("SSH daemon is enabled in the installer OS, to allow"
                     " debugging the installer image.")
        logging.info("More info: https://postmarketos.org/ondev-debug")


def disable_firewall(args):
    if not args.no_firewall:
        return

    # check=False: rc-update doesn't exit with 0 if already disabled
    suffix = f"rootfs_{args.device}"
    pmb.chroot.root(args, ["rc-update", "del", "nftables", "default"], suffix,
                    check=False)

    # Verify that it's gone
    nftables_files = pmb.helpers.run.root(
        args, ["find", "-name", "nftables"], output_return=True,
        working_dir=f"{args.work}/chroot_{suffix}/etc/runlevels")
    if nftables_files:
        raise RuntimeError(f"Failed to disable firewall: {nftables_files}")


def print_firewall_info(args):
    pmaports_cfg = pmb.config.pmaports.read_config(args)
    pmaports_ok = pmaports_cfg.get("supported_firewall", None) == "nftables"

    # Find kernel pmaport (will not be found if Alpine kernel is used)
    apkbuild_found = False
    apkbuild_has_opt = False

    arch = args.deviceinfo["arch"]
    kernel = get_kernel_package(args, args.device)
    if kernel:
        kernel_apkbuild = pmb.build._package.get_apkbuild(args, kernel[0],
                                                          arch)
        if kernel_apkbuild:
            opts = kernel_apkbuild["options"]
            apkbuild_has_opt = "pmb:kconfigcheck-nftables" in opts
            apkbuild_found = True

    # Print the note and make it stand out
    logging.info("")
    logging.info("*** FIREWALL INFORMATION ***")

    if not pmaports_ok:
        logging.info("Firewall is not supported in checked out pmaports"
                     " branch.")
    elif args.no_firewall:
        logging.info("Firewall is disabled (--no-firewall).")
    elif not apkbuild_found:
        logging.info("Firewall is enabled, but may not work (couldn't"
                     " determine if kernel supports nftables).")
    elif apkbuild_has_opt:
        logging.info("Firewall is enabled and supported by kernel.")
    else:
        logging.info("Firewall is enabled, but will not work (no support in"
                     " kernel config for nftables).")
        logging.info("If/when the kernel supports it in the future, it"
                     " will work automatically.")

    logging.info("For more information: https://postmarketos.org/firewall")


def generate_binary_list(args, suffix, step):
    """
    Perform three checks prior to writing binaries to disk: 1) that binaries
    exist, 2) that binaries do not extend into the first partition, 3) that
    binaries do not overlap each other.

    :param suffix: of the chroot, which holds the firmware files (either the
                   f"rootfs_{args.device}", or f"installer_{args.device}")
    :param step: partition step size in bytes
    """
    binary_ranges = {}
    binary_list = []
    binaries = args.deviceinfo["sd_embed_firmware"].split(",")

    for binary_offset in binaries:
        binary, offset = binary_offset.split(':')
        try:
            offset = int(offset)
        except ValueError:
            raise RuntimeError("Value for firmware binary offset is "
                               f"not valid: {offset}")
        binary_path = os.path.join(args.work, f"chroot_{suffix}", "usr/share",
                                   binary)
        if not os.path.exists(binary_path):
            raise RuntimeError("The following firmware binary does not "
                               f"exist in the {suffix} chroot: "
                               f"/usr/share/{binary}")
        # Insure that embedding the firmware will not overrun the
        # first partition
        boot_part_start = args.deviceinfo["boot_part_start"] or "2048"
        max_size = (int(boot_part_start) * 512) - (offset * step)
        binary_size = os.path.getsize(binary_path)
        if binary_size > max_size:
            raise RuntimeError("The firmware is too big to embed in the "
                               f"disk image {binary_size}B > {max_size}B")
        # Insure that the firmware does not conflict with any other firmware
        # that will be embedded
        binary_start = offset * step
        binary_end = binary_start + binary_size
        for start, end in binary_ranges.items():
            if ((binary_start >= start and binary_start < end) or
                    (binary_end > start and binary_end <= end)):
                raise RuntimeError("The firmware overlaps with at least one "
                                   f"other firmware image: {binary}")

        binary_ranges[binary_start] = binary_end
        binary_list.append((binary, offset))

    return binary_list


def embed_firmware(args, suffix):
    """
    This method will embed firmware, located at /usr/share, that are specified
    by the "sd_embed_firmware" deviceinfo parameter into the SD card image
    (e.g. u-boot). Binaries that would overwrite the first partition are not
    accepted, and if multiple binaries are specified then they will be checked
    for collisions with each other.

    :param suffix: of the chroot, which holds the firmware files (either the
                   f"rootfs_{args.device}", or f"installer_{args.device}")
    """
    if not args.deviceinfo["sd_embed_firmware"]:
        return

    step = 1024
    if args.deviceinfo["sd_embed_firmware_step_size"]:
        try:
            step = int(args.deviceinfo["sd_embed_firmware_step_size"])
        except ValueError:
            raise RuntimeError("Value for "
                               "deviceinfo_sd_embed_firmware_step_size "
                               "is not valid: {}".format(step))

    device_rootfs = mount_device_rootfs(args, suffix)
    binary_list = generate_binary_list(args, suffix, step)

    # Write binaries to disk
    for binary, offset in binary_list:
        binary_file = os.path.join("/usr/share", binary)
        logging.info("Embed firmware {} in the SD card image at offset {} with"
                     " step size {}".format(binary, offset, step))
        filename = os.path.join(device_rootfs, binary_file.lstrip("/"))
        pmb.chroot.root(args, ["dd", "if=" + filename, "of=/dev/install",
                               "bs=" + str(step), "seek=" + str(offset)])


def write_cgpt_kpart(args, layout, suffix):
    """
    Write the kernel to the ChromeOS kernel partition.

    :param layout: partition layout from get_partition_layout()
    :param suffix: of the chroot, which holds the image file to be flashed
    """
    if not args.deviceinfo["cgpt_kpart"]:
        return

    device_rootfs = mount_device_rootfs(args, suffix)
    filename = f"{device_rootfs}{args.deviceinfo['cgpt_kpart']}"
    pmb.chroot.root(
        args, ["dd", f"if={filename}", f"of=/dev/installp{layout['kernel']}"])


def sanity_check_sdcard(args):
    device = args.sdcard
    device_name = os.path.basename(device)
    if not os.path.exists(device):
        raise RuntimeError(f"{device} doesn't exist, is the sdcard plugged?")
    if os.path.isdir('/sys/class/block/{}'.format(device_name)):
        with open('/sys/class/block/{}/ro'.format(device_name), 'r') as handle:
            ro = handle.read()
        if ro == '1\n':
            raise RuntimeError(f"{device} is read-only, is the sdcard locked?")


def sanity_check_sdcard_size(args):
    device = args.sdcard
    devpath = os.path.realpath(device)
    sysfs = '/sys/class/block/{}/size'.format(devpath.replace('/dev/', ''))
    if not os.path.isfile(sysfs):
        # This is a best-effort sanity check, continue if it's not checkable
        return

    with open(sysfs) as handle:
        raw = handle.read()

    # Size is in 512-byte blocks
    size = int(raw.strip())
    human = "{:.2f} GiB".format(size / 2 / 1024 / 1024)

    # Warn if the size is larger than 100GiB
    if size > (100 * 2 * 1024 * 1024):
        if not pmb.helpers.cli.confirm(args,
                                       f"WARNING: The target disk ({devpath}) "
                                       "is larger than a usual SD card "
                                       "(>100GiB). Are you sure you want to "
                                       f"overwrite this {human} disk?",
                                       no_assumptions=True):
            raise RuntimeError("Aborted.")


def get_ondev_pkgver(args):
    arch = args.deviceinfo["arch"]
    package = pmb.helpers.package.get(args, "postmarketos-ondev", arch)
    return package["version"].split("-r")[0]


def sanity_check_ondev_version(args):
    ver_pkg = get_ondev_pkgver(args)
    ver_min = pmb.config.ondev_min_version
    if pmb.parse.version.compare(ver_pkg, ver_min) == -1:
        raise RuntimeError("This version of pmbootstrap requires"
                           f" postmarketos-ondev version {ver_min} or"
                           " higher. The postmarketos-ondev found in pmaports"
                           f" / in the binary packages has version {ver_pkg}.")


def get_partition_layout(reserve, kernel):
    """
    :param reserve: create an empty partition between root and boot (pma#463)
    :param kernel: create a separate kernel partition before all other
                   partitions, e.g. for the ChromeOS devices with cgpt
    :returns: the partition layout, e.g. without reserve and kernel:
              {"kernel": None, "boot": 1, "reserve": None, "root": 2}
    """
    ret = {}
    ret["kernel"] = None
    ret["boot"] = 1
    ret["reserve"] = None
    ret["root"] = 2

    if kernel:
        ret["kernel"] = 1
        ret["boot"] += 1
        ret["root"] += 1

    if reserve:
        ret["reserve"] = ret["root"]
        ret["root"] += 1
    return ret


def install_system_image(args, size_reserve, suffix, step, steps,
                         boot_label="pmOS_boot", root_label="pmOS_root",
                         split=False, sdcard=None):
    """
    :param size_reserve: empty partition between root and boot in MiB (pma#463)
    :param suffix: the chroot suffix, where the rootfs that will be installed
                   on the device has been created (e.g. "rootfs_qemu-amd64")
    :param step: next installation step
    :param steps: total installation steps
    :param boot_label: label of the boot partition (e.g. "pmOS_boot")
    :param root_label: label of the root partition (e.g. "pmOS_root")
    :param split: create separate images for boot and root partitions
    :param sdcard: path to sdcard device (e.g. /dev/mmcblk0) or None
    """
    # Partition and fill image/sdcard
    logging.info(f"*** ({step}/{steps}) PREPARE INSTALL BLOCKDEVICE ***")
    pmb.chroot.shutdown(args, True)
    (size_boot, size_root) = get_subpartitions_size(args, suffix)
    layout = get_partition_layout(size_reserve, args.deviceinfo["cgpt_kpart"])
    if not args.rsync:
        pmb.install.blockdevice.create(args, size_boot, size_root,
                                       size_reserve, split, sdcard)
        if not split:
            if args.deviceinfo["cgpt_kpart"]:
                pmb.install.partition_cgpt(
                    args, layout, size_boot, size_reserve)
            else:
                pmb.install.partition(args, layout, size_boot, size_reserve)
    if not split:
        pmb.install.partitions_mount(args, layout, sdcard)

    pmb.install.format(args, layout, boot_label, root_label, sdcard)

    # Just copy all the files
    logging.info(f"*** ({step + 1}/{steps}) FILL INSTALL BLOCKDEVICE ***")
    copy_files_from_chroot(args, suffix)
    create_home_from_skel(args)
    configure_apk(args)
    copy_ssh_keys(args)

    # Don't try to embed firmware and cgpt on split images since there's no
    # place to put it and it will end up in /dev of the chroot instead
    if not split:
        embed_firmware(args, suffix)
        write_cgpt_kpart(args, layout, suffix)

    if sdcard:
        logging.info("Unmounting SD card (this may take a while "
                     "to sync, please wait)")
    pmb.chroot.shutdown(args, True)

    # Convert rootfs to sparse using img2simg
    sparse = args.sparse
    if sparse is None:
        sparse = args.deviceinfo["flash_sparse"] == "true"

    if sparse and not split and not sdcard:
        logging.info("(native) make sparse rootfs")
        pmb.chroot.apk.install(args, ["android-tools"])
        sys_image = args.device + ".img"
        sys_image_sparse = args.device + "-sparse.img"
        pmb.chroot.user(args, ["img2simg", sys_image, sys_image_sparse],
                        working_dir="/home/pmos/rootfs/")
        pmb.chroot.user(args, ["mv", "-f", sys_image_sparse, sys_image],
                        working_dir="/home/pmos/rootfs/")

        # patch sparse image for Samsung devices if specified
        samsungify_strategy = args.deviceinfo["flash_sparse_samsung_format"]
        if samsungify_strategy:
            logging.info("(native) convert sparse image into Samsung's sparse image format")
            pmb.chroot.apk.install(args, ["sm-sparse-image-tool"])
            sys_image = f"{args.device}.img"
            sys_image_patched = f"{args.device}-patched.img"
            pmb.chroot.user(args, ["sm_sparse_image_tool", "samsungify", "--strategy",
                                   samsungify_strategy, sys_image, sys_image_patched],
                            working_dir="/home/pmos/rootfs/")
            pmb.chroot.user(args, ["mv", "-f", sys_image_patched, sys_image],
                            working_dir="/home/pmos/rootfs/")


def print_flash_info(args):
    """ Print flashing information, based on the deviceinfo data and the
        pmbootstrap arguments. """
    logging.info("")  # make the note stand out
    logging.info("*** FLASHING INFORMATION ***")

    # System flash information
    method = args.deviceinfo["flash_method"]
    flasher = pmb.config.flashers.get(method, {})
    flasher_actions = flasher.get("actions", {})
    requires_split = flasher.get("split", False)

    if method == "none":
        logging.info("Refer to the installation instructions of your device,"
                     " or the generic install instructions in the wiki.")
        logging.info("https://wiki.postmarketos.org/wiki/Installation_guide"
                     "#pmbootstrap_flash")
        return

    logging.info("Run the following to flash your installation to the"
                 " target device:")

    if "flash_rootfs" in flasher_actions and not args.sdcard and \
            bool(args.split) == requires_split:
        logging.info("* pmbootstrap flasher flash_rootfs")
        logging.info("  Flashes the generated rootfs image to your device:")
        if args.split:
            logging.info(f"  {args.work}/chroot_native/home/pmos/rootfs/"
                         f"{args.device}-rootfs.img")
        else:
            logging.info(f"  {args.work}/chroot_native/home/pmos/rootfs/"
                         f"{args.device}.img")
            logging.info("  (NOTE: This file has a partition table, which"
                         " contains /boot and / subpartitions. That way we"
                         " don't need to change the partition layout on your"
                         " device.)")

    # if current flasher supports vbmeta and partition is explicitly specified
    # in deviceinfo
    if "flash_vbmeta" in flasher_actions and \
            (args.deviceinfo["flash_fastboot_partition_vbmeta"] or
             args.deviceinfo["flash_heimdall_partition_vbmeta"]):
        logging.info("* pmbootstrap flasher flash_vbmeta")
        logging.info("  Flashes vbmeta image with verification disabled flag.")

    # if current flasher supports dtbo and partition is explicitly specified
    # in deviceinfo
    if "flash_dtbo" in flasher_actions and \
            (args.deviceinfo["flash_fastboot_partition_dtbo"] or
             args.deviceinfo["flash_heimdall_partition_dtbo"]):
        logging.info("* pmbootstrap flasher flash_dtbo")
        logging.info("  Flashes dtbo image.")

    # Most flash methods operate independently of the boot partition.
    # (e.g. an Android boot image is generated). In that case, "flash_kernel"
    # works even when partitions are split or installing for sdcard.
    # This is not possible if the flash method requires split partitions.
    if "flash_kernel" in flasher_actions and \
            (not requires_split or args.split):
        logging.info("* pmbootstrap flasher flash_kernel")
        logging.info("  Flashes the kernel + initramfs to your device:")
        if requires_split:
            logging.info(f"  {args.work}/chroot_native/home/pmos/rootfs/"
                         f"{args.device}-boot.img")
        else:
            logging.info(f"  {args.work}/chroot_rootfs_{args.device}/boot")

    if "boot" in flasher_actions:
        logging.info("  (NOTE: " + method + " also supports booting"
                     " the kernel/initramfs directly without flashing."
                     " Use 'pmbootstrap flasher boot' to do that.)")

    if "flash_lk2nd" in flasher_actions and \
            os.path.exists(args.work + "/chroot_rootfs_" + args.device +
                           "/boot/lk2nd.img"):
        logging.info("* Your device supports and may even require"
                     " flashing lk2nd. You should flash it before"
                     " flashing anything else. Use 'pmbootstrap flasher"
                     " flash_lk2nd' to do that.")

    # Export information
    logging.info("* If the above steps do not work, you can also create"
                 " symlinks to the generated files with 'pmbootstrap export'"
                 " and flash outside of pmbootstrap.")


def install_recovery_zip(args, steps):
    logging.info(f"*** ({steps}/{steps}) CREATING RECOVERY-FLASHABLE ZIP ***")
    suffix = "buildroot_" + args.deviceinfo["arch"]
    mount_device_rootfs(args, f"rootfs_{args.device}", suffix)
    pmb.install.recovery.create_zip(args, suffix)

    # Flash information
    logging.info("*** FLASHING INFORMATION ***")
    logging.info("Flashing with the recovery zip is explained here:")
    logging.info("https://postmarketos.org/recoveryzip")


def install_on_device_installer(args, step, steps):
    # Generate the rootfs image
    if not args.ondev_no_rootfs:
        suffix_rootfs = f"rootfs_{args.device}"
        install_system_image(args, 0, suffix_rootfs, step=step, steps=steps,
                             split=True)
        step += 2

    # Prepare the installer chroot
    logging.info(f"*** ({step}/{steps}) CREATE ON-DEVICE INSTALLER ROOTFS ***")
    step += 1
    packages = ([f"device-{args.device}",
                 "postmarketos-ondev"] +
                get_kernel_package(args, args.device) +
                get_nonfree_packages(args, args.device))

    suffix_installer = f"installer_{args.device}"
    pmb.chroot.apk.install(args, packages, suffix_installer)

    # Move rootfs image into installer chroot
    img_path_dest = f"{args.work}/chroot_{suffix_installer}/var/lib/rootfs.img"
    if not args.ondev_no_rootfs:
        img = f"{args.device}-root.img"
        img_path_src = f"{args.work}/chroot_native/home/pmos/rootfs/{img}"
        logging.info(f"({suffix_installer}) add {img} as /var/lib/rootfs.img")
        pmb.install.losetup.umount(args, img_path_src)
        pmb.helpers.run.root(args, ["mv", img_path_src, img_path_dest])

    # Run ondev-prepare, so it may generate nice configs from the channel
    # properties (e.g. to display the version number), or transform the image
    # file into another format. This can all be done without pmbootstrap
    # changes in the postmarketos-ondev package.
    logging.info(f"({suffix_installer}) ondev-prepare")
    channel = pmb.config.pmaports.read_config(args)["channel"]
    channel_cfg = pmb.config.pmaports.read_config_channel(args)
    env = {"ONDEV_CHANNEL": channel,
           "ONDEV_CHANNEL_BRANCH_APORTS": channel_cfg["branch_aports"],
           "ONDEV_CHANNEL_BRANCH_PMAPORTS": channel_cfg["branch_pmaports"],
           "ONDEV_CHANNEL_DESCRIPTION": channel_cfg["description"],
           "ONDEV_CHANNEL_MIRRORDIR_ALPINE": channel_cfg["mirrordir_alpine"],
           "ONDEV_CIPHER": args.cipher,
           "ONDEV_PMBOOTSTRAP_VERSION": pmb.config.version,
           "ONDEV_UI": args.ui}
    pmb.chroot.root(args, ["ondev-prepare"], suffix_installer, env=env)

    # Copy files specified with 'pmbootstrap install --ondev --cp'
    if args.ondev_cp:
        for host_src, chroot_dest in args.ondev_cp:
            host_dest = f"{args.work}/chroot_{suffix_installer}/{chroot_dest}"
            logging.info(f"({suffix_installer}) add {host_src} as"
                         f" {chroot_dest}")
            pmb.helpers.run.root(args, ["install", "-Dm644", host_src,
                                        host_dest])

    # Remove $DEVICE-boot.img (we will generate a new one if --split was
    # specified, otherwise the separate boot image is not needed)
    if not args.ondev_no_rootfs:
        img_boot = f"{args.device}-boot.img"
        logging.info(f"(native) rm {img_boot}")
        pmb.chroot.root(args, ["rm", f"/home/pmos/rootfs/{img_boot}"])

    # Disable root login
    setup_login(args, suffix_installer)

    # Generate installer image
    size_reserve = round(os.path.getsize(img_path_dest) / 1024 / 1024) + 200
    pmaports_cfg = pmb.config.pmaports.read_config(args)
    boot_label = pmaports_cfg.get("supported_install_boot_label",
                                  "pmOS_inst_boot")
    install_system_image(args, size_reserve, suffix_installer, step, steps,
                         boot_label, "pmOS_install", args.split, args.sdcard)


def get_selected_providers(args, packages):
    """
    Look through the specified packages and see which providers were selected
    in "pmbootstrap init". Install those as extra packages to select them
    instead of the default provider.

    :param packages: the packages that have selectable providers (_pmb_select)
    :return: additional provider packages to install
    """
    providers = []
    for p in packages:
        apkbuild = pmb.helpers.pmaports.get(args, p, subpackages=False)
        for select in apkbuild['_pmb_select']:
            if select in args.selected_providers:
                providers.append(args.selected_providers[select])
    return providers


def create_device_rootfs(args, step, steps):
    # List all packages to be installed (including the ones specified by --add)
    # and upgrade the installed packages/apkindexes
    logging.info(f'*** ({step}/{steps}) CREATE DEVICE ROOTFS ("{args.device}")'
                 ' ***')

    suffix = f"rootfs_{args.device}"
    # Create user before installing packages, so post-install scripts of
    # pmaports can figure out the username (legacy reasons: pmaports#820)
    set_user(args)

    # Fill install_packages
    install_packages = (pmb.config.install_device_packages +
                        ["device-" + args.device])
    if not args.install_base:
        install_packages = [p for p in install_packages
                            if p != "postmarketos-base"]
    if args.ui.lower() != "none":
        install_packages += ["postmarketos-ui-" + args.ui]

    # Add additional providers of base/device/UI package
    install_packages += get_selected_providers(args, install_packages)

    install_packages += get_kernel_package(args, args.device)
    install_packages += get_nonfree_packages(args, args.device)
    if args.ui.lower() != "none":
        if args.ui_extras:
            install_packages += ["postmarketos-ui-" + args.ui + "-extras"]
        if args.install_recommends:
            install_packages += pmb.install.ui.get_recommends(args)
    if args.extra_packages.lower() != "none":
        install_packages += args.extra_packages.split(",")
    if args.add:
        install_packages += args.add.split(",")
    locale_is_set = (args.locale != pmb.config.defaults["locale"])
    if locale_is_set:
        install_packages += ["lang", "musl-locales"]

    pmaports_cfg = pmb.config.pmaports.read_config(args)
    # postmarketos-base supports a dummy package for blocking osk-sdl install
    # when not required
    if pmaports_cfg.get("supported_base_nofde", None):
        # The ondev installer *could* enable fde at runtime, so include it
        # explicitly in the rootfs until there's a mechanism to selectively
        # install it when the ondev installer is running.
        # Always install it when --fde is specified.
        if args.full_disk_encryption or args.on_device_installer:
            # Pick the most suitable unlocker depending on the packages
            # selected for installation
            unlocker = pmb.parse.depends.package_provider(
                args, "postmarketos-fde-unlocker", install_packages, suffix)
            if unlocker["pkgname"] not in install_packages:
                install_packages += [unlocker["pkgname"]]
        else:
            install_packages += ["postmarketos-base-nofde"]

    pmb.helpers.repo.update(args, args.deviceinfo["arch"])

    # Explicitly call build on the install packages, to re-build them or any
    # dependency, in case the version increased
    if args.build_pkgs_on_install:
        for pkgname in install_packages:
            pmb.build.package(args, pkgname, args.deviceinfo["arch"])

    # Install all packages to device rootfs chroot (and rebuild the initramfs,
    # because that doesn't always happen automatically yet, e.g. when the user
    # installed a hook without pmbootstrap - see #69 for more info)
    pmb.chroot.apk.install(args, install_packages, suffix)
    flavor = pmb.chroot.other.kernel_flavor_installed(args, suffix)
    pmb.chroot.initfs.build(args, flavor, suffix)

    # Set the user password
    setup_login(args, suffix)

    # Set the keymap if the device requires it
    setup_keymap(args)

    # Set timezone
    arch = args.deviceinfo["arch"]
    package = pmb.helpers.package.get(args, "alpine-conf", arch)
    version = package["version"].split("-r")[0]

    if not pmb.parse.version.check_string(version, ">=3.14.0"):
        pmb.chroot.root(args, ["setup-timezone", "-z", args.timezone], suffix)
    else:
        pmb.chroot.root(args, ["setup-timezone", args.timezone], suffix)

    # Set locale
    if locale_is_set:
        pmb.chroot.root(args, ["sed", "-i",
                               f"s/LANG=C.UTF-8/LANG={args.locale}/",
                               "/etc/profile.d/locale.sh"], suffix)

    # Set the hostname as the device name
    setup_hostname(args)

    disable_sshd(args)
    disable_firewall(args)


def install(args):
    # Sanity checks
    if not args.android_recovery_zip and args.sdcard:
        sanity_check_sdcard(args)
        sanity_check_sdcard_size(args)
    if args.on_device_installer:
        sanity_check_ondev_version(args)

    # Number of steps for the different installation methods.
    if args.no_image:
        steps = 2
    elif args.android_recovery_zip:
        steps = 3
    elif args.on_device_installer:
        steps = 4 if args.ondev_no_rootfs else 7
    else:
        steps = 4

    # Install required programs in native chroot
    step = 1
    logging.info(f"*** ({step}/{steps}) PREPARE NATIVE CHROOT ***")
    pmb.chroot.apk.install(args, pmb.config.install_native_packages,
                           build=False)
    step += 1

    if not args.ondev_no_rootfs:
        create_device_rootfs(args, step, steps)
        step += 1

    if args.no_image:
        return
    elif args.android_recovery_zip:
        return install_recovery_zip(args, steps)

    if args.on_device_installer:
        # Runs install_system_image twice
        install_on_device_installer(args, step, steps)
    else:
        install_system_image(args, 0, f"rootfs_{args.device}", step, steps,
                             split=args.split, sdcard=args.sdcard)

    print_flash_info(args)
    print_sshd_info(args)
    print_firewall_info(args)

    # Leave space before 'chroot still active' note
    logging.info("")
