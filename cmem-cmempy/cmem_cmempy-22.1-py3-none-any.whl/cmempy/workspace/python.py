"""python package and plugin management."""
from json import loads
from os.path import basename

from requests_toolbelt.multipart import encoder

from cmem.cmempy import config
from cmem.cmempy.api import request, send_request


def install_package_by_name(package_name):
    """Install a python package by name."""
    uri = config.get_di_api_endpoint() + "/api/python/installPackageByName"
    install_request = send_request(
        uri,
        method="POST",
        params={
            "name": package_name
        }
    )
    return loads(install_request)


def install_package_by_file(package_file):
    """Install a python package by source tar.gz or wheel file."""
    uri = config.get_di_api_endpoint() + "/api/python/installPackage"
    file_name = basename(package_file)
    with open(package_file, 'rb') as file:
        files = [('file', (file_name, file))]
        # https://stackoverflow.com/questions/42281387/
        multipart_encoder = encoder.MultipartEncoder(
            fields=files,
            boundary="xxx---------------xxx",
        )
        install_request = request(
            uri,
            method="POST",
            data=multipart_encoder,
            headers={'Content-Type': multipart_encoder.content_type},
            stream=True
        )
        return loads(install_request.content.decode())


def uninstall_package(package_name: str):
    """Uninstall a python package."""
    uri = config.get_di_api_endpoint() + "/api/python/uninstallPackage"
    uninstall_request = send_request(
        uri,
        method="POST",
        params={
            "name": package_name
        }
    )
    return loads(uninstall_request)


def list_packages():
    """List installed python packages."""
    uri = config.get_di_api_endpoint() + "/api/python/listPackages"
    list_request = send_request(
        uri,
        method="GET",
    )
    return loads(list_request)


def update_plugins():
    """Discover plugins installed in packages."""
    uri = config.get_di_api_endpoint() + "/api/python/updatePlugins"
    update_request = send_request(
        uri,
        method="GET",
    )
    return loads(update_request)


def list_plugins():
    """List installed python packages."""
    uri = config.get_di_api_endpoint() + "/api/python/listPlugins"
    list_request = send_request(
        uri,
        method="GET",
    )
    return loads(list_request)
