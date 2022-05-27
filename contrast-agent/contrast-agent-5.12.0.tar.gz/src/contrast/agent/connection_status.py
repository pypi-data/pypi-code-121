# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.


class ConnectionStatus(object):
    """
    Stores the connection information between the agent and the service
    """

    def __init__(self):
        self._connected = False

        self._success = 0
        self._failed = 0

    @property
    def failure_count(self):
        return self._failed

    @property
    def success_count(self):
        return self._success

    @property
    def connected(self):
        return self._connected

    @property
    def resend_startup(self):
        return bool(self._success) and not self.connected

    def success(self):
        self._connected = True
        self._success += 1

    def failure(self):
        self._connected = False
        self._failed += 1
