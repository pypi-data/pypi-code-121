# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import socket
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)


class ServiceConfig(object):

    LOCALHOST_NAMES = ("127.0.0.1", "localhost")

    def __init__(self, config):
        self.socket = config.get("agent.service.socket")
        self.host = config.get("agent.service.host")
        self.port = config.get("agent.service.port")

        self._validate_config()

        self.is_unix = False
        self.socket_type = self.determine_socket_type()
        self.address = self.determine_address()

    def _validate_config(self):
        """
        This should throw an exception two scenarios:

        1. socket and tcp are configured
        2. socket is not configured and tcp is improperly configured
        """
        if self.has_socket() and self.has_tcp():
            raise ContrastServiceException(
                "Invalid service config, cannot have both socket + host/port."
            )

        if not self.has_socket() and not self.has_tcp():
            raise ContrastServiceException(
                "Invalid service config, must have host and port."
            )

    def has_socket(self):
        return bool(self.socket)

    def has_tcp(self):
        return bool(self.host and not self.host.isspace() and self.port)

    @property
    def uses_localhost(self):
        return self.host in self.LOCALHOST_NAMES

    @property
    def uses_unix_socket(self):
        return self.socket_type == socket.AF_UNIX

    @property
    def local_service_configured(self):
        return self.uses_localhost or self.uses_unix_socket

    def determine_socket_type(self):
        if self.socket:
            self.socket_type = socket.AF_UNIX
            self.is_unix = True
        else:
            self.socket_type = socket.AF_INET
        return self.socket_type

    def determine_address(self):
        if self.is_unix:
            self.address = self.socket
        else:
            self.address = (self.host, self.port)

        return self.address
