# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import pathlib
import platform
import psutil
import time
from os import path

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def make_sure_path_exists(log_path):
    directory = path.dirname(log_path)

    # log_path is not a dir, just a file path
    if directory in ("", "/"):
        return

    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)


def sleep(seconds):
    """
    Wrapper around time.sleep that makes testing less complicated
    """
    time.sleep(seconds)


class ServiceUtil(object):
    SERVICE_EXE_NAME = "contrast-service"
    BASE_SERVICE_DIRECTORY = "service_executables"

    LINUX_PLATFORM = "linux"
    MAC_PLATFORM = "darwin"

    LINUX_SERVICE_DIRECTORY = LINUX_PLATFORM
    MAC_SERVICE_DIRECTORY = "mac"

    SUPPORTED_PLATFORM_DIRECTORIES = {
        LINUX_PLATFORM: LINUX_SERVICE_DIRECTORY,
        MAC_PLATFORM: MAC_SERVICE_DIRECTORY,
    }

    def __init__(self, service_log_path):
        self.service_log_path = service_log_path
        self.service_path = ServiceUtil.generate_service_path()

    def start_bundled_service(self):
        """
        Start a new Contrast Service. If one is already running on the host (bundled or external),
        for now we accept that there will be multiple services.

        :return: bool of success
        """
        return self._start_service()

    @property
    def service_exists(self):
        return self.service_path and path.exists(self.service_path)

    def _start_service(self):
        """
        Based on the operating system architecture, start the correct type of service.
        :return: bool of success
        """
        if self.service_exists:
            if not self.service_log_path or self.service_log_path == "STDOUT":
                psutil.Popen(self.service_path)
            else:
                make_sure_path_exists(self.service_log_path)
                with open(self.service_log_path, "wb") as out:
                    psutil.Popen(self.service_path, stdout=out, stderr=out)

            logger.debug("Started up %s", self.SERVICE_EXE_NAME)
            return True

        logger.error("Failed to find service executable at %s", self.service_path)
        return False

    @staticmethod
    def generate_service_path():
        """
        Gets the absolute path to the appropriate service, depending on the current system architecture.
        """
        current_file_path = path.dirname(path.realpath(__file__))
        parent_directory = path.dirname(current_file_path)
        base_service_directory = path.realpath(
            path.join(parent_directory, ServiceUtil.BASE_SERVICE_DIRECTORY)
        )
        platform_directory = ServiceUtil.get_platform_directory()
        exe_name = ServiceUtil.SERVICE_EXE_NAME
        return path.join(base_service_directory, platform_directory, exe_name)

    @staticmethod
    def get_platform_directory():
        """
        Gets the platform directory name corresponding to the current system architecture.
        For an unknown system, default to Linux.
        :return: A string of the directory name
        """
        platform_directory = ServiceUtil.SUPPORTED_PLATFORM_DIRECTORIES.get(
            platform.system().lower()
        )
        if platform_directory is None:
            logger.debug(
                "Unknown/unsupported host platform; will attempt to use %s %s"
                " executable",
                ServiceUtil.LINUX_PLATFORM,
                ServiceUtil.SERVICE_EXE_NAME,
            )
            return ServiceUtil.LINUX_SERVICE_DIRECTORY
        return platform_directory
