# Copyright 2022 Attila Szollosi
# SPDX-License-Identifier: GPL-3.0-or-later
import glob
import logging
import re
import os

import pmb.build
import pmb.config
import pmb.parse
import pmb.helpers.pmaports


def is_set(config, option):
    """
    Check, whether a boolean or tristate option is enabled
    either as builtin or module.
    """
    return re.search("^CONFIG_" + option + "=[ym]$", config, re.M) is not None


def is_set_str(config, option, string):
    """
    Check, whether a config option contains a string as value.
    """
    match = re.search("^CONFIG_" + option + "=\"(.*)\"$", config, re.M)
    if match:
        return string == match.group(1)
    else:
        return False


def is_in_array(config, option, string):
    """
    Check, whether a config option contains string as an array element
    """
    match = re.search("^CONFIG_" + option + "=\"(.*)\"$", config, re.M)
    if match:
        values = match.group(1).split(",")
        return string in values
    else:
        return False


def check_option(component, details, config, config_path_pretty, option,
                 option_value):
    link = (f"https://wiki.postmarketos.org/wiki/kconfig#CONFIG_{option}")
    warning_no_details = (f"WARNING: {config_path_pretty} isn't"
                          f" configured properly for {component}, run"
                          f" 'pmbootstrap kconfig check' for details!")
    if isinstance(option_value, list):
        for string in option_value:
            if not is_in_array(config, option, string):
                if details:
                    logging.info(f"WARNING: {config_path_pretty}:"
                                 f' CONFIG_{option} should contain "{string}".'
                                 f" See <{link}> for details.")
                else:
                    logging.warning(warning_no_details)
                return False
    elif isinstance(option_value, str):
        if not is_set_str(config, option, option_value):
            if details:
                logging.info(f"WARNING: {config_path_pretty}: CONFIG_{option}"
                             f' should be set to "{option_value}".'
                             f" See <{link}> for details.")
            else:
                logging.warning(warning_no_details)
            return False
    elif option_value in [True, False]:
        if option_value != is_set(config, option):
            if details:
                should = "should" if option_value else "should *not*"
                logging.info(f"WARNING: {config_path_pretty}: CONFIG_{option}"
                             f" {should} be set. See <{link}> for details.")
            else:
                logging.warning(warning_no_details)
            return False
    else:
        raise RuntimeError("kconfig check code can only handle booleans,"
                           f" strings and arrays. Given value {option_value}"
                           " is not supported. If you need this, please patch"
                           " pmbootstrap or open an issue.")
    return True


def check_config(config_path, config_path_pretty, config_arch, pkgver,
                 anbox=False,
                 apparmor=False,
                 iwd=False,
                 nftables=False,
                 containers=False,
                 zram=False,
                 netboot=False,
                 uefi=False,
                 details=False):
    logging.debug(f"Check kconfig: {config_path}")
    with open(config_path) as handle:
        config = handle.read()

    components = {"postmarketOS": pmb.config.necessary_kconfig_options}
    if anbox:
        components["anbox"] = pmb.config.necessary_kconfig_options_anbox
    if apparmor:
        components["apparmor"] = pmb.config.necessary_kconfig_options_apparmor
    if iwd:
        components["iwd"] = pmb.config.necessary_kconfig_options_iwd
    if nftables:
        components["nftables"] = pmb.config.necessary_kconfig_options_nftables
    if containers:
        components["containers"] = \
            pmb.config.necessary_kconfig_options_containers
    if zram:
        components["zram"] = pmb.config.necessary_kconfig_options_zram
    if netboot:
        components["netboot"] = pmb.config.necessary_kconfig_options_netboot
    if uefi:
        components["uefi"] = pmb.config.necessary_kconfig_options_uefi

    results = [check_config_options_set(config, config_path_pretty,
                                        config_arch, options, component,
                                        pkgver, details)
               for component, options in components.items()]
    return all(results)


def check_config_options_set(config, config_path_pretty, config_arch, options,
                             component, pkgver, details=False):
    # Loop through necessary config options, and print a warning,
    # if any is missing
    ret = True
    for rules, archs_options in options.items():
        # Skip options irrelevant for the current kernel's version
        # Example rules: ">=4.0 <5.0"
        skip = False
        for rule in rules.split(" "):
            if not pmb.parse.version.check_string(pkgver, rule):
                skip = True
                break
        if skip:
            continue

        for archs, options in archs_options.items():
            if archs != "all":
                # Split and check if the device's architecture architecture has
                # special config options. If option does not contain the
                # architecture of the device kernel, then just skip the option.
                architectures = archs.split(" ")
                if config_arch not in architectures:
                    continue

            for option, option_value in options.items():
                if not check_option(component, details, config,
                                    config_path_pretty, option, option_value):
                    ret = False
                    if not details:
                        break  # do not give too much error messages
    return ret


def check(args, pkgname,
          force_anbox_check=False,
          force_apparmor_check=False,
          force_iwd_check=False,
          force_nftables_check=False,
          force_containers_check=False,
          force_zram_check=False,
          force_netboot_check=False,
          force_uefi_check=False,
          details=False):
    """
    Check for necessary kernel config options in a package.

    :returns: True when the check was successful, False otherwise
    """
    # Pkgname: allow omitting "linux-" prefix
    if pkgname.startswith("linux-"):
        flavor = pkgname.split("linux-")[1]
    else:
        flavor = pkgname

    # Read all kernel configs in the aport
    ret = True
    aport = pmb.helpers.pmaports.find(args, "linux-" + flavor)
    apkbuild = pmb.parse.apkbuild(f"{aport}/APKBUILD")
    pkgver = apkbuild["pkgver"]
    check_anbox = force_anbox_check or (
        "pmb:kconfigcheck-anbox" in apkbuild["options"])
    check_apparmor = force_apparmor_check or (
        "pmb:kconfigcheck-apparmor" in apkbuild["options"])
    check_iwd = force_iwd_check or (
        "pmb:kconfigcheck-iwd" in apkbuild["options"])
    check_nftables = force_nftables_check or (
        "pmb:kconfigcheck-nftables" in apkbuild["options"])
    check_containers = force_containers_check or (
        "pmb:kconfigcheck-containers" in apkbuild["options"])
    check_zram = force_zram_check or (
        "pmb:kconfigcheck-zram" in apkbuild["options"])
    check_netboot = force_netboot_check or (
        "pmb:kconfigcheck-netboot" in apkbuild["options"])
    check_uefi = force_uefi_check or (
        "pmb:kconfigcheck-uefi" in apkbuild["options"])
    for config_path in glob.glob(aport + "/config-*"):
        # The architecture of the config is in the name, so it just needs to be
        # extracted
        config_name = os.path.basename(config_path)
        config_name_split = config_name.split(".")

        if len(config_name_split) != 2:
            raise RuntimeError(f"{config_name} is not a valid kernel config "
                               "name. Ensure that the _config property in your "
                               "kernel APKBUILD has a . before the "
                               "architecture name, e.g. .aarch64 or .armv7, "
                               "and that there is no excess punctuation "
                               "elsewhere in the name.")

        config_arch = config_name_split[1]
        config_path_pretty = f"linux-{flavor}/{os.path.basename(config_path)}"
        ret &= check_config(config_path, config_path_pretty, config_arch,
                            pkgver,
                            anbox=check_anbox,
                            apparmor=check_apparmor,
                            iwd=check_iwd,
                            nftables=check_nftables,
                            containers=check_containers,
                            zram=check_zram,
                            netboot=check_netboot,
                            uefi=check_uefi,
                            details=details)
    return ret


def extract_arch(config_file):
    # Extract the architecture out of the config
    with open(config_file) as f:
        config = f.read()
    if is_set(config, "ARM"):
        return "armv7"
    elif is_set(config, "ARM64"):
        return "aarch64"
    elif is_set(config, "X86_32"):
        return "x86"
    elif is_set(config, "X86_64"):
        return "x86_64"

    # No match
    logging.info("WARNING: failed to extract arch from kernel config")
    return "unknown"


def extract_version(config_file):
    # Try to extract the version string out of the comment header
    with open(config_file) as f:
        # Read the first 3 lines of the file and get the third line only
        text = [next(f) for x in range(3)][2]
    ver_match = re.match(r"# Linux/\S+ (\S+) Kernel Configuration", text)
    if ver_match:
        return ver_match.group(1)

    # No match
    logging.info("WARNING: failed to extract version from kernel config")
    return "unknown"


def check_file(config_file, anbox=False, nftables=False,
               containers=False, zram=False, netboot=False, uefi=False,
               details=False):
    """
    Check for necessary kernel config options in a kconfig file.

    :returns: True when the check was successful, False otherwise
    """
    arch = extract_arch(config_file)
    version = extract_version(config_file)
    logging.debug(f"Check kconfig: parsed arch={arch}, version={version} from "
                  f"file: {config_file}")
    return check_config(config_file, config_file, arch, version,
                        anbox=anbox,
                        nftables=nftables,
                        containers=containers,
                        zram=zram,
                        netboot=netboot,
                        uefi=uefi,
                        details=details)
