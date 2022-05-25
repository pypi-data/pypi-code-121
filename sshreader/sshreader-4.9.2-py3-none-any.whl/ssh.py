#!/usr/bin/env python
# coding=utf-8
"""A wrapper for Paramiko that attempts to make ssh sessions easier to work with.  It also contains the
shell_command function for running local shell scripts!
"""
# Copyright (C) 2015-2022 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
from collections import namedtuple, OrderedDict
from getpass import getuser
import logging
import os
import paramiko
import socket
import sys

# Privates
__author__ = 'Jesse Almanrode (jesse@almanrode.com)'

if sys.version_info[0] < 3:
    raise Exception('Python2.x is no longer supported in this version of sshreader')
elif sys.version_info[1] < 6:
    raise Exception('Only Python 3.6 and later is supported in this version of sshreader')

# Globals
Command = namedtuple('Command', ['cmd', 'stdout', 'stderr', 'return_code'])


def envvars():
    """ Attempt to determine the current username and location of any ssh private keys.
    If any value is unable to be determined it is returned as 'None'.

    This method also checks for any private keys loaded into the SSH Agent.

    :return: NamedTuple of (username, agent_keys, rsa_key, dsa_key, ecdsa_key)
    """
    env = OrderedDict(username=None, agent_keys=None, rsa_key=None, dsa_key=None, ecdsa_key=None)
    EnvVars = namedtuple('EnvVars', env.keys())
    if os.getlogin() == getuser():
        env['username'] = getuser()
    userhome = os.path.expanduser('~')
    if os.path.exists(userhome + "/.ssh"):
        keyfiles = os.listdir(userhome + "/.ssh")
        if "id_rsa" in keyfiles:
            env['rsa_key'] = userhome + "/.ssh/id_rsa"
        if "id_dsa" in keyfiles:
            env['dsa_key'] = userhome + "/.ssh/id_dsa"
        if 'id_ecdsa' in keyfiles:
            env['ecdsa_key'] = userhome + '/.ssh/id_ecdsa'
    env['agent_keys'] = paramiko.Agent().get_keys()
    return EnvVars(**env)


class SSH(object):
    """SSH Session object

    :param fqdn: Fully qualified domain name or IP address
    :param username: SSH username
    :param password: SSH password
    :param keyfile: SSH private key file
    :param keypass: SSH private key password
    :param port: SSH port
    :param connect: Initiate the connect
    :return: SSH connection object
    :raises: SSHException
    """
    def __init__(self, fqdn, username=None, password=None, keyfile=None, keypass=None, port=22, connect=True):
        if not keyfile:
            if len(paramiko.Agent().get_keys()) == 0:
                if not all((username, password)):
                    paramiko.SSHException('username and password or keyfile not provided')
        self.host = fqdn
        self.username = username
        self.password = password
        if keyfile:
            if not isinstance(keyfile, str):
                raise TypeError('expected %s for keyfile, got %s' % (str(str), str(type(keyfile))))
            self.keyfile = os.path.abspath(os.path.expanduser(keyfile))
        else:
            self.keyfile = keyfile
        self.rsa_sha2 = False  # Enable RSA w/SHA2 hashes (OpenSSH 8.8 and later)
        self.keypass = keypass
        self.port = port
        self._connection = paramiko.SSHClient()
        self._connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if connect:
            self.__connect()

    def __str__(self):
        return str(self.__dict__)

    def __enter__(self):
        if self.__alive() is False:
            self.__connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__close()

    def sftp_put(self, srcfile, dstfile):
        """ Use the SFTP subsystem of OpenSSH to copy a local file to a remote host

        :param srcfile: Path to the local file
        :param dstfile: Path to the remote file
        :return: Result of paramiko.SFTPClient.put()
        """
        if not self.__alive():
            raise paramiko.SSHException("connection to %s not established" % (self.host,))
        sftp = paramiko.SFTPClient.from_transport(self._connection.get_transport())
        try:
            result = sftp.put(os.path.expanduser(srcfile), os.path.expanduser(dstfile), confirm=True)
        finally:
            sftp.close()
        return result

    def sftp_get(self, srcfile, dstfile):
        """ Use the SFTP subsystem of OpenSSH to copy a remote file to the localhost

        :param srcfile: Path to the remote file
        :param dstfile: Path to the local file
        :return: Result of paramiko.SFTPClient.get()
        """
        if not self.__alive():
            raise paramiko.SSHException("connection to %s not established" % (self.host,))
        sftp = paramiko.SFTPClient.from_transport(self._connection.get_transport())
        try:
            sftp.get(os.path.expanduser(srcfile), os.path.expanduser(dstfile))
        finally:
            sftp.close()

    def ssh_command(self, command, timeout=30, combine=False, decodebytes=True):
        """Run a command over an ssh connection

        :param command: The command to run
        :param timeout: Timeout for the command
        :param combine: Combine stderr and stdout (pseudo TTY)
        :param decodebytes: Decode bytes objects to unicode strings
        :return: Namedtuple of (cmd, stdout, stderr, return_code) or (cmd, stdout, return_code)
        :raises: SSHException
        """
        if self.__alive() is False:
            raise paramiko.SSHException("connection to %s not established" % (self.host, ))
        if combine:
            try:
                stdin, stdout, stderr = self._connection.exec_command(command, timeout=timeout, get_pty=True)
                if decodebytes:
                    result = Command(cmd=command, stdout=stdout.read().decode().strip(), stderr=None,
                                     return_code=stdout.channel.recv_exit_status())
                else:
                    result = Command(cmd=command, stdout=stdout.read().strip(), stderr=None,
                                     return_code=stdout.channel.recv_exit_status())
            except (paramiko.buffered_pipe.PipeTimeout, socket.timeout):
                result = Command(cmd=command, stdout='command timed out', stderr=None, return_code=124)
        else:
            try:
                stdin, stdout, stderr = self._connection.exec_command(command, timeout=timeout)
                if decodebytes:
                    result = Command(cmd=command, stdout=stdout.read().decode().strip(),
                                     stderr=stderr.read().decode().strip(), return_code=stdout.channel.recv_exit_status())
                else:
                    result = Command(cmd=command, stdout=stdout.read().strip(), stderr=stderr.read().strip(),
                                     return_code=stdout.channel.recv_exit_status())
            except (paramiko.buffered_pipe.PipeTimeout, socket.timeout):
                result = Command(cmd=command, stdout='', stderr='command timed out', return_code=124)
        return result

    def close(self):
        """Closes an established ssh connection

        :return: None
        """
        return self._connection.close()

    def alive(self):
        """Is an SSH connection alive

        :return: True or False
        :raises: SSHException
        """
        if self._connection.get_transport() is None:
            return False
        else:
            if self._connection.get_transport().is_alive():
                return True
            else:
                raise paramiko.SSHException("unable to determine state of ssh connection")

    def reconnect(self):
        """Alias to connect
        """
        return self.__connect()

    def connect(self, failfast=True, timeout=30):
        """Opens an SSH Connection

        :param failfast: Test socket connection before attempting to connect
        :param timeout: SSH connection timeout in seconds
        :return: True
        :raises: SSHException
        """
        if self.__alive():
            raise paramiko.SSHException("connection to % already established" % (self.host, ))
        # Fail Fast for unreachable host:port
        if failfast:
            try:
                s = socket.socket()
                s.settimeout(1)
                s.connect((self.host, self.port))
            except socket.timeout:
                raise paramiko.SSHException('connect to host %s port %d: Operation timed out' % (self.host, self.port))
            else:
                s.close()
        paramiko.util.logging.getLogger().setLevel(logging.CRITICAL)  # Keeping paramiko from logging errors to stdout
        if not self.keyfile:
            if len(paramiko.Agent().get_keys()) == 0:
                if not all((self.username, self.password)):
                    paramiko.SSHException('username and password or keyfile not provided')
        if self.keyfile:
            if self.rsa_sha2:
                self._connection.connect(self.host, port=self.port, username=self.username, password=self.keypass,
                                        key_filename=self.keyfile, timeout=timeout, look_for_keys=False)
            else:
                # While this is more insecure, it is required for pre-OpenSSH 8.8 servers
                # For more info, visit: https://www.paramiko.org/changelog.html#2.9.0
                self._connection.connect(self.host, port=self.port, username=self.username, password=self.keypass,
                                        key_filename=self.keyfile, timeout=timeout, look_for_keys=False, 
                                        disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
        else:
            self._connection.connect(self.host, port=self.port, username=self.username, password=self.password,
                                     timeout=timeout, look_for_keys=False)
        return True

    # Privatizing some of the functions so SSH can be subclassed
    __alive = alive
    __connect = connect
    __close = close
