"""
This is a simple class to get command from Cisco devices

"""
from typing import Optional, List, Union
import ipaddress
import socket
import netmiko
from netmiko import ConnectHandler


class FailedDnsLookup(Exception):
    """
    Exception for DNS Exceptions
    """

    def __init__(self, value):
        super().__init__(value)
        self.value = f'{value}'

    def __str__(self):  # pragma: no cover
        return repr(self.value)


class BadProtocol(Exception):
    """
    Exception for Protocol Exceptions
    """

    def __init__(self, value):
        super().__init__(value)
        self.value = f'{value}'

    def __str__(self):  # pragma: no cover
        return repr(self.value)


class BadSshDeviceType(Exception):
    """
    Exception for a bad ssh device type Exceptions
    """

    def __init__(self, value):
        super().__init__(value)
        self.value = f'{value}'

    def __str__(self):  # pragma: no cover
        return repr(self.value)


class BadTelnetDeviceType(Exception):
    """
    Exception for a bad telnet device type Exceptions
    """

    def __init__(self, value):
        super().__init__(value)
        self.value = f'{value}'

    def __str__(self):  # pragma: no cover
        return repr(self.value)


class QuickNetmiko:
    """
    Class to run commands and get output

    :type device_ip_name: String
    :param device_ip_name: The device name or ip address
    :type device_type: String
    :param device_type: The device type see ssh_connections, and telnet_connections
    :type username: String
    :param username: The username to use
    :type password: String
    :param password: The password to use
    :type protocol: String
    :param protocol: One of the following {'ssh', 'telnet'} default: ssh

    :rtype: None
    :returns: None

    :raises BadProtocol: If protocol is not one of the following {'ssh', 'telnet'}
    :raises BadSshDeviceType: If protocol is ssh and device_type is not one in ssh_connections
    :raises BadTelnetDeviceType: If protocol is telnet and device_type is not one in telnet_connections
    :raises FailedDnsLookup: If a hostname is not able to be looked up via DNS
    :raises FailedDnsLookup: If there is a timeout when looking up a hostname

    """
    # Dictionary to correlate ssh device_type
    ssh_connections = {
        'aruba_os': 'aruba_os_ssh',
        'aruba_os_ssh': 'aruba_os_ssh',
        'eos': 'arista_eos_ssh',
        'arista_eos': 'arista_eos_ssh',
        'arista_eos_ssh': 'arista_eos_ssh',
        'ios': 'cisco_ios_ssh',
        'cisco_ios_ssh': 'cisco_ios_ssh',
        'cisco_ios': 'cisco_ios_ssh',
        'iosxe': 'cisco_ios_ssh',
        'iosxr': 'cisco_xr_ssh',
        'cisco_xr_ssh': 'cisco_xr_ssh',
        'cisco_xr': 'cisco_xr_ssh',
        'nxos': 'cisco_nxos_ssh',
        'cisco_nxos_ssh': 'cisco_nxos_ssh',
        'cisco_nxos': 'cisco_nxos_ssh',
    }
    # Dictionary to correlate telnet device_type
    telnet_connections = {
        'eos': 'arista_eos_telnet',
        'arista_eos': 'arista_eos_telnet',
        'arista_eos_telnet': 'arista_eos_telnet',
        'ios': 'cisco_ios_telnet',
        'cisco_ios_telnet': 'cisco_ios_telnet',
        'cisco_ios': 'cisco_ios_telnet',
        'iosxe': 'cisco_ios_telnet',
        'iosxr': 'cisco_xr_telnet',
        'cisco_xr_telnet': 'cisco_xr_telnet',
        'cisco_xr': 'cisco_xr_telnet',
        'nxos': 'cisco_nxos_telnet',
        'cisco_nxos_telnet': 'cisco_nxos_telnet',
        'cisco_nxos': 'cisco_nxos_telnet',
    }
    # Set of supported protocols
    protocols = {'ssh', 'telnet'}

    def __init__(self, device_ip_name: str, device_type: str, username: str,   # pylint: disable=too-many-arguments
                 password: str, protocol: Optional[str] = 'ssh') -> None:
        if protocol not in self.protocols:
            raise BadProtocol(f'protocol must be one of the following {self.protocols}')

        if protocol == 'ssh':
            if not self.ssh_connections.get(device_type):  # pylint: disable=no-else-raise
                raise BadSshDeviceType(f'device_type must be one of the following {self.ssh_connections.keys()} when'
                                       f'protocol is ssh')

            else:
                self.device_type = self.ssh_connections.get(device_type)

        else:
            if not self.telnet_connections.get(device_type):  # pylint: disable=no-else-raise
                raise BadTelnetDeviceType(f'device_type must be one of the following {self.telnet_connections.keys()} '
                                          f'when protocol is telnet')

            else:
                self.device_type = self.telnet_connections.get(device_type)

        try:
            self.device_ip = str(ipaddress.ip_address(device_ip_name))

        except ValueError:
            try:
                self.device_ip = socket.gethostbyname(device_ip_name)

            except socket.gaierror as e:
                raise FailedDnsLookup(f'DNS lookup failed while looking up {device_ip_name}') from e

            except socket.timeout as e:
                raise FailedDnsLookup(f'DNS timed out while looking up {device_ip_name}') from e

        self.username = username
        self.password = password
        self.device_ip_name = device_ip_name

    def __str__(self) -> str:  # pragma: no cover
        return f'{type(self)} device_name = {self.device_ip_name}'

    def __get_params(self) -> dict:
        """
        Private method to get the Netmiko connection parameters

        :rtype: Dict
        :returns: A dictionary of connection params

        """
        params = {'device_type': self.device_type,
                  'host': self.device_ip,
                  'username': self.username,
                  'password': self.password}

        return params

    @staticmethod
    def __send_single_command(net_con: netmiko.ConnectHandler, command: str) -> str:
        """
        Private method to send a command to a device and get the results

        :type net_con: <class 'netmiko.ConnectHandler'>
        :param net_con: The netmiko connection handler object
        :type command: String
        :param command: The command to get data for

        :rtype: String
        :returns: The results from the command

        """
        data = str()

        data += net_con.send_command(command)
        net_con.disconnect()

        return data

    def __send_list_of_commands(self, net_con: netmiko.ConnectHandler, commands: List[str]) -> str:
        """
        Private method to send a list of commands to a device and get the results

        :type net_con: <class 'netmiko.ConnectHandler'>
        :param net_con: The netmiko connection handler object
        :type commands: List[str]
        :param commands: The list of commands to get data for

        :rtype: String
        :returns: The results from the command

        """
        data = str()
        for command in commands:
            data += self.__send_single_command(net_con, command)

        return data

    def send_commands(self, commands: Union[List[str], str]) -> str:
        """
        Method to send a list of commands or single command to a device and get the results

        :type commands: List or String
        :param commands: The list of commands or single command to get data for

        :rtype: String
        :returns: The results from the commands

        :raises TypeError: If commands is not a list or string

        """
        net_con = ConnectHandler(**self.__get_params())

        data = str()

        if isinstance(commands, list):
            data += self.__send_list_of_commands(net_con, commands)

        elif isinstance(commands, str):
            data += self.__send_single_command(net_con, commands)

        else:
            raise TypeError(f'commands must be a list, or a string but received a {type(commands)}')

        return data
