import os
import platform
from typing import List

import pkg_resources

from .helpers import download_file
from .logger import get_logger

ALLURECTL_VERSION = '1.21.2'
LOGGER = get_logger()

allure_executables = {
    'Darwin': {
        'x86_64': 'allurectl_darwin_amd64'
    },
    'Linux': {
        'arm': 'allurectl_linux_arm64',
        'i386': 'allurectl_linux_386',
        'x86_64': 'allurectl_linux_amd64'
    },
    'Windows': {
        'x86_64': 'allurectl_windows_amd64.exe',
        'arm': 'allurectl_windows_arm64.exe',
    }
}


def get_allure_executable(platform_name: str) -> str:
    platform_name = platform_name or 'auto'

    system = platform.system() if platform_name == 'auto' \
        else platform_name.split('.')[0]
    machine = platform.machine() if platform_name == 'auto' \
        else platform_name.split('.')[1]

    full_platform_name = '{}.{}'.format(system, machine)
    supported_platforms = get_platforms()
    if full_platform_name not in supported_platforms:
        raise OSError('Failed to find executable for your platform - '
                      '{}, supported platforms are {}'
                      .format(full_platform_name, supported_platforms))
    return allure_executables[system][machine]


def download_allurectl(dest_dir: str, platform_name: str = None) -> None:
    executable_name = get_allure_executable(platform_name)
    file_url = 'https://github.com/allure-framework/allurectl/'\
               'releases/download/{}/{}'\
               .format(ALLURECTL_VERSION, executable_name)
    LOGGER.debug('Downloading allurectl from {}'.format(file_url))
    download_file(file_url, dest_dir, executable_name)


def install_allurectl(platform_name: str = None) -> str:
    bin_dir = pkg_resources.resource_filename('easy_allure', '/bin/')
    path = os.path.join(bin_dir, get_allure_executable(platform_name))
    if not os.path.exists(path):
        download_allurectl(bin_dir, platform_name)
    return path


def get_platforms() -> List:
    platforms = []
    for operation_sys, executables in allure_executables.items():
        for platform_name in executables.keys():
            platforms.append('{}.{}'.format(operation_sys, platform_name))
    return platforms
