# Copyright 2022 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import logging
import pmb


def is_dtb(path):
    if not os.path.isfile(path):
        return False
    with open(path, 'rb') as f:
        # Check FDT magic identifier (0xd00dfeed)
        return f.read(4) == b'\xd0\x0d\xfe\xed'


def get_mtk_label(path):
    """ Read the label of a mediatek header of kernel or ramdisk inside an
        extracted boot.img.
        :param path: to either the kernel or ramdisk file extracted from
                     boot.img
        :returns: * None: file does not exist or does not have Mediatek header
                  * Label string (e.g. "ROOTFS", "RECOVERY", "KERNEL") """
    if not os.path.exists(path):
        return None

    with open(path, 'rb') as f:
        # Check Mediatek header (0x88168858)
        if not f.read(4) == b'\x88\x16\x88\x58':
            return None
        f.seek(8)
        label = f.read(32).decode("utf-8").rstrip('\0')
        return label


def check_mtk_bootimg(bootimg_path):
    """ Check if a boot.img contains a kernel and ramdisk with Mediatek
        headers, and verify that these headers have labels we expect in
        boot-deploy.
        :param bootimg_path: path to boot.img, with extracted files in the same
                             directory
        :returns: * True: has Mediatek headers
                  * False: has no Mediatek headers """
    label_kernel = get_mtk_label(f"{bootimg_path}-kernel")
    label_ramdisk = get_mtk_label(f"{bootimg_path}-ramdisk")

    # Doesn't have Mediatek headers
    if label_kernel is None and label_ramdisk is None:
        return False

    # Verify that the kernel and ramdisk have the labels we expect and have
    # hardcoded in boot-deploy.git's add_mtk_header() function. We don't know
    # if there are devices out there with different labels, but if there are,
    # our code in boot-deploy needs to be adjusted to use the proper labels
    # (store the label in deviceinfo and use it).
    err_start = "This boot.img has Mediatek headers."
    err_end = ("Please create an issue and attach your boot.img:"
               " https://postmarketos.org/issues")
    if label_kernel != "KERNEL":
        raise RuntimeError(f"{err_start} Expected the kernel inside the"
                           " boot.img to have a 'KERNEL' label instead of"
                           f" '{label_kernel}'. {err_end}")
    if label_ramdisk == "RECOVERY":
        logging.warning(
            f"WARNING: {err_start} But since you apparently passed a recovery"
            " image instead of a regular boot.img, we can't tell if it has the"
            " expected label 'ROOTFS' inside the ramdisk (found 'RECOVERY')."
            " So there is a slight chance that it may not boot, in that case"
            " run bootimg_analyze again with a regular boot.img. It will fail"
            " if the label is different from 'ROOTFS'.")
    elif label_ramdisk != "ROOTFS":
        raise RuntimeError(f"{err_start} Expected the ramdisk inside the"
                           " boot.img to have a 'ROOTFS' label instead of"
                           f" '{label_ramdisk}'. {err_end}")

    return True


def bootimg(args, path):
    if not os.path.exists(path):
        raise RuntimeError("Could not find file '" + path + "'")

    logging.info("NOTE: You will be prompted for your sudo/doas password, so"
                 " we can set up a chroot to extract and analyze your"
                 " boot.img file")
    pmb.chroot.apk.install(args, ["file", "unpackbootimg"])

    temp_path = pmb.chroot.other.tempfolder(args, "/tmp/bootimg_parser")
    bootimg_path = f"{args.work}/chroot_native{temp_path}/boot.img"

    # Copy the boot.img into the chroot temporary folder
    # and make it world readable
    pmb.helpers.run.root(args, ["cp", path, bootimg_path])
    pmb.helpers.run.root(args, ["chmod", "a+r", bootimg_path])

    file_output = pmb.chroot.user(args, ["file", "-b", "boot.img"],
                                  working_dir=temp_path,
                                  output_return=True).rstrip()
    if "android bootimg" not in file_output.lower():
        if "force" in args and args.force:
            logging.warning("WARNING: boot.img file seems to be invalid, but"
                            " proceeding anyway (-f specified)")
        else:
            logging.info("NOTE: If you are sure that your file is a valid"
                         " boot.img file, you could force the analysis"
                         " with: 'pmbootstrap bootimg_analyze " + path +
                         " -f'")
            if ("linux kernel" in file_output.lower() or
                    "ARM OpenFirmware FORTH Dictionary" in file_output):
                raise RuntimeError("File is a Kernel image, you might need the"
                                   " 'heimdall-isorec' flash method. See also:"
                                   " <https://wiki.postmarketos.org/wiki/"
                                   "Deviceinfo_flash_methods>")
            else:
                raise RuntimeError("File is not an Android boot.img. (" +
                                   file_output + ")")

    # Extract all the files
    pmb.chroot.user(args, ["unpackbootimg", "-i", "boot.img"],
                    working_dir=temp_path)

    output = {}
    header_version = None
    # Get base, offsets, pagesize, cmdline and qcdt info
    # This file does not exist for example for qcdt images
    if os.path.isfile(f"{bootimg_path}-header_version"):
        with open(f"{bootimg_path}-header_version", 'r') as f:
            header_version = int(f.read().replace('\n', ''))

    if header_version is not None and header_version >= 3:
        output["header_version"] = str(header_version)
        output["pagesize"] = "4096"
    else:
        with open(f"{bootimg_path}-base", 'r') as f:
            output["base"] = ("0x%08x" % int(f.read().replace('\n', ''), 16))
        with open(f"{bootimg_path}-kernel_offset", 'r') as f:
            output["kernel_offset"] = ("0x%08x"
                                       % int(f.read().replace('\n', ''), 16))
        with open(f"{bootimg_path}-ramdisk_offset", 'r') as f:
            output["ramdisk_offset"] = ("0x%08x"
                                        % int(f.read().replace('\n', ''), 16))
        with open(f"{bootimg_path}-second_offset", 'r') as f:
            output["second_offset"] = ("0x%08x"
                                       % int(f.read().replace('\n', ''), 16))
        with open(f"{bootimg_path}-tags_offset", 'r') as f:
            output["tags_offset"] = ("0x%08x"
                                     % int(f.read().replace('\n', ''), 16))
        with open(f"{bootimg_path}-pagesize", 'r') as f:
            output["pagesize"] = f.read().replace('\n', '')

    output["qcdt"] = ("true" if os.path.isfile(f"{bootimg_path}-dt") and
                      os.path.getsize(f"{bootimg_path}-dt") > 0 else "false")
    output["mtk_mkimage"] = ("true" if check_mtk_bootimg(bootimg_path)
                             else "false")
    output["dtb_second"] = ("true" if is_dtb(f"{bootimg_path}-second")
                            else "false")

    with open(f"{bootimg_path}-cmdline", 'r') as f:
        output["cmdline"] = f.read().replace('\n', '')

    # Cleanup
    pmb.chroot.root(args, ["rm", "-r", temp_path])

    return output
