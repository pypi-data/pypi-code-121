#!/usr/bin/python
# -*- coding: utf8 -*-

from platform import system as system_name  # Returns the system/OS name
from os import system as system_call  # Execute a shell command
import sys


class Ping(object):

    @staticmethod
    def ping(ip):
        try:
            parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"
            # return system_call("ping " + parameters + " " + ip) == 0
            return system_call("ping " + parameters + " " + ip + " > log.txt") == 0
        except:
            return False
