#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> arg = ScapyArguments()
>>> arg.parse_args().iface
<NetworkInterface ...>
>>> arg.parse_args(["-i", "eth0"]).iface
<NetworkInterface ...>
>>> arg.parse_args(["--interface", "eth"]).iface
<NetworkInterface ...>

>>> arg = ScapyArguments(interface_args=["++custom", "|c"], prefix_chars="+|")
>>> arg.parse_args().iface
<NetworkInterface ...>
>>> arg.parse_args(["|c", "127.0.0"]).iface
<NetworkInterface ...>
>>> arg.parse_args(["++custom", "00:00:00:"]).iface
<NetworkInterface ...>

>>> arg = ScapyArguments(interface_kwargs={"required", True}, description="My program description")
>>> arg.parse_args(["-i", "172.16.10."]).iface
<NetworkInterface ...>
>>> arg.parse_args(["--interface", "0A:00:34:"]).iface
<NetworkInterface ...>
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["ScapyArguments"]

from argparse import ArgumentParser, Namespace
from sys import executable
from typing import List

try:
    from scapy.all import IFACES, conf
except ImportError:
    raise ImportError(
        "Scapy should be installed to use this module.\n"
        f"You can install it with: {executable} -m pip install scapy"
    )


class ScapyArguments(ArgumentParser):

    """
    This class implements ArgumentsParser with
    interface argument and iface research.
    """

    interface_args: list = ["--interface", "-i"]
    interface_kwargs: dict = {
        "help": "Part of the IP, MAC or name of the interface",
    }

    def __init__(
        self,
        *args,
        interface_args=interface_args,
        interface_kwargs=interface_kwargs,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.interface_args = interface_args
        self.interface_kwargs = interface_kwargs
        self.add_argument(*interface_args, **interface_kwargs)

    def parse_args(
        self, args: List[str] = None, namespace: Namespace = None
    ) -> Namespace:

        """
        This function implements the iface
        research from interface arguments.
        """

        namespace: Namespace = ArgumentParser.parse_args(self, args, namespace)

        argument_name: str = max(self.interface_args, key=len)
        for char in self.prefix_chars:
            if char == argument_name[0]:
                argument_name = argument_name.lstrip(char)
                break

        interface = getattr(namespace, argument_name, None)

        if interface is not None:
            interface = interface.casefold()

            for temp_iface in IFACES.values():

                ip = temp_iface.ip
                mac = temp_iface.mac or ""
                name = temp_iface.name or ""
                network_name = temp_iface.network_name or ""

                mac = mac.casefold()
                name = name.casefold()
                network_name = network_name.casefold()

                if (
                    (ip and interface in ip)
                    or (mac and interface in mac)
                    or (name and interface in name)
                    or (network_name and interface in network_name)
                ):
                    namespace.iface = temp_iface
                    return namespace

        namespace.iface = conf.iface
        return namespace
