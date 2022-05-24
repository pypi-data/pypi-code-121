# Copyright 2022 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import pmb.flasher
import pmb.chroot.initfs


def check_partition_blacklist(args, key, value):
    if not key.startswith("$PARTITION_"):
        return

    name = args.deviceinfo["name"]
    if value in args.deviceinfo["partition_blacklist"].split(","):
        raise RuntimeError("'" + value + "'" + " partition is blacklisted " +
                           "from being flashed! See the " + name + " device " +
                           "wiki page for more information.")


def run(args, action, flavor=None):
    pmb.flasher.init(args)

    # Verify action
    method = args.flash_method or args.deviceinfo["flash_method"]
    cfg = pmb.config.flashers[method]
    if action not in cfg["actions"]:
        raise RuntimeError("action " + action + " is not"
                           " configured for method " + method + "!"
                           " You can use the '--method' option to specify a"
                           " different flash method. See also:"
                           " <https://wiki.postmarketos.org/wiki/"
                           "Deviceinfo_flash_methods>")

    # Variable setup
    vars = pmb.flasher.variables(args, flavor, method)

    # vbmeta flasher requires vbmeta partition to be explicitly specified
    if action == "flash_vbmeta" and not vars["$PARTITION_VBMETA"]:
        raise RuntimeError("Your device does not have 'vbmeta' partition"
                           " specified; set"
                           " 'deviceinfo_flash_fastboot_partition_vbmeta'"
                           " or 'deviceinfo_flash_heimdall_partition_vbmeta'"
                           " in deviceinfo file. See also:"
                           " <https://wiki.postmarketos.org/wiki/"
                           "Deviceinfo_reference>")

    # dtbo flasher requires dtbo partition to be explicitly specified
    if action == "flash_dtbo" and not vars["$PARTITION_DTBO"]:
        raise RuntimeError("Your device does not have 'dtbo' partition"
                           " specified; set"
                           " 'deviceinfo_flash_fastboot_partition_dtbo'"
                           " in deviceinfo file. See also:"
                           " <https://wiki.postmarketos.org/wiki/"
                           "Deviceinfo_reference>")

    # Run the commands of each action
    for command in cfg["actions"][action]:
        # Variable replacement
        for key, value in vars.items():
            for i in range(len(command)):
                if key in command[i]:
                    if value is None:
                        raise RuntimeError(f"Variable {key} found in action"
                                           f" {action} for method {method},"
                                           " but the value for this variable"
                                           " is None! Is that missing in your"
                                           " deviceinfo?")
                    check_partition_blacklist(args, key, value)
                    command[i] = command[i].replace(key, value)

        # Run the action
        pmb.chroot.root(args, command, output="interactive")
