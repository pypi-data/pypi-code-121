import collections
import re
import json
import copy
VERSION_RX = re.compile(r"^(?P<major_version>\d+)[_|\.]?")


def _link_plugin_packages(packages):
    """
    Linking code ripped from legacy_sidecar.
    """
    products = collections.defaultdict(dict)
    for package in packages:
        products[package["product"]][package["package_id"]] = package

    for plugin_package in packages:
        plugin_host_product = plugin_package["plugin_host_product"]
        if not plugin_host_product:
            continue
        for host_package_id in products[plugin_host_product]:
            host_package = products[plugin_host_product][host_package_id]
            if _should_link(plugin_package, host_package):
                host_package["plugins"].append(plugin_package["package_id"])
                plugin_package["plugin_hosts"].append(host_package_id)

    return packages


def _should_link(plugin_package, candidate_host):
    """
    Linking code ripped from legacy_sidecar.
    """
    plugin_host_version = plugin_package["plugin_host_version"]
    plugin_host_product = plugin_package["plugin_host_product"]
    if not plugin_host_version and plugin_host_product:
        return False

    match = VERSION_RX.match(plugin_host_version)
    host_major_version = match.groupdict()["major_version"]

    same_platform = candidate_host["platform"] == plugin_package["platform"]
    same_major_version = candidate_host["major_version"] == host_major_version
    return same_platform and same_major_version


def _pad_defaults(packages):
    """
    Add fields if they are missing.
    """
    keys = {
        "plugin_host_product": "",
        "plugin_host_version": "",
        "minor_version": "",
        "release_version": "",
        "build_version": "",
        "plugin_hosts": [],
        "plugins": [],
        "platform": "linux",
    }

    for package in packages:
        for key in keys:
            if not key in package:
                package[key] = copy.copy(keys[key])

        version = [
            package.get("major_version"),
            package.get("minor_version"),
            package.get("release_version"),
            package.get("build_version"),
        ]
        version = "v{}".format(".".join([v for v in version if v]))
        # Generate a package name
        package["package"] = "{}-{}-{}".format(package["product"], version, package["package_id"])


MAYA_DATA = [
    {"product": "maya", "major_version": "1", "minor_version": "0", "package_id": "id_0"},
    {"product": "maya", "major_version": "1", "minor_version": "1", "package_id": "id_1"},
    {"product": "maya", "major_version": "2", "minor_version": "0", "package_id": "id_2"},
]


REDSHIFT_DATA = [
    {
        "product": "redshift",
        "major_version": "1",
        "plugin_host_version": "1",
        "plugin_host_product": "maya",
        "package_id": "id_3",
    },
    {
        "product": "redshift",
        "major_version": "2",
        "plugin_host_version": "1",
        "plugin_host_product": "maya",
        "package_id": "id_4",
    },
    {
        "product": "redshift",
        "platform": "windows",
        "major_version": "2",
        "plugin_host_version": "2",
        "plugin_host_product": "maya",
        "package_id": "id_5",
    },
    {
        "product": "redshift",
        "platform": "windows",
        "major_version": "2",
        "plugin_host_version": "1",
        "plugin_host_product": "maya",
        "package_id": "id_6",
    },
]

MAX_DATA = [
    {
        "product": "max",
        "platform": "windows",
        "major_version": "1",
        "minor_version": "0",
        "package_id": "id_7",
    },
    {
        "product": "max",
        "platform": "windows",
        "major_version": "1",
        "minor_version": "1",
        "package_id": "id_8",
    },
]


C4D_DATA = [
    {
        "product": "c4d",
        "major_version": "1",
        "minor_version": "0",
        "package_id": "id_9",
    },
    {
        "product": "c4d",
        "platform": "windows",
        "major_version": "1",
        "minor_version": "0",
        "package_id": "id_10",
    },
]

BLENDER_DATA = [
    {
        "product": "blender",
        "major_version": "1",
        "package_id": "id_11",
    },
    {
        "product": "blender",
        "major_version": "1",
        "minor_version": "0",
        "package_id": "id_12",
    },
    {
        "product": "blender",
        "major_version": "1",
        "minor_version": "0",
        "release_version": "2",
        "package_id": "id_13",
    },
    {
        "product": "blender",
        "major_version": "1",
        "minor_version": "0",
        "release_version": "2",
        "build_version": "3",
        "package_id": "id_14",
    },
]


HOST_DATA = MAYA_DATA + MAX_DATA + C4D_DATA + BLENDER_DATA

PLUGIN_DATA = REDSHIFT_DATA

SOFTWARE_DATA = HOST_DATA + PLUGIN_DATA

_pad_defaults(SOFTWARE_DATA)

_link_plugin_packages(SOFTWARE_DATA)

# This is useful for printing out the resolved package fixture data. 
# print(json.dumps(SOFTWARE_DATA, indent=2))
