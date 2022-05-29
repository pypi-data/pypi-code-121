#
# This file is part of the python-openocd project.
#
# Copyright (C) 2014 Andreas Ortmann <ortmann@finf.uni-hannover.de>
# Copyright (C) 2020-2021 Marc Schink <dev@zapb.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
This module provides an OpenOCD Tcl interface class.
"""

import socket
from enum import Enum
from openocd.tclformatter import TclFormatter


class ResetType(Enum):
    """Target reset type."""

    RUN = 'run'
    """Start target code execution after reset."""
    HALT = 'halt'
    """Halt the target after reset."""
    INIT = 'init'
    """Halt the target after reset and execute the ``reset-init`` script."""


class OpenOcd:
    """
    An OpenOCD Tcl interface class.

    Parameters
    ----------
    host : str
        Hostname of the OpenOCD server.
    port : int
        Port of the OpenOCD Tcl interface.
    """
    COMMAND_TOKEN = '\x1a'

    def __init__(self, host='localhost', port=6666):
        self._host = host
        self._port = port
        self._buffer_size = 4096

        self._fmt = TclFormatter().format

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, _type, value, traceback):
        try:
            self._exit()
        finally:
            self.close()

    def _exit(self):
        self.execute('exit')

    @property
    def host(self):
        """Hostname of the OpenOCD server."""
        return self._host

    @property
    def port(self):
        """Port number of the OpenOCD Tcl interface."""
        return self._port

    def connect(self):
        """Establish a connection to the OpenOCD server."""
        self._socket.connect((self._host, self._port))

    def close(self):
        """Close the connection."""
        self._socket.close()

    def execute(self, command):
        """
        Execute an arbitrary OpenOCD command.

        Parameters
        ----------
        command : str
            Command string.

        Returns
        -------
        str
            Result of the executed command.
        """
        data = (command + OpenOcd.COMMAND_TOKEN).encode('utf-8')
        self._socket.send(data)

        try:
            result = self._recv()
        except socket.timeout:
            result = None

        return result

    def _recv(self):
        data = bytes()

        while True:
            tmp = self._socket.recv(self._buffer_size)
            data += tmp

            if bytes(OpenOcd.COMMAND_TOKEN, encoding='utf-8') in tmp:
                break

        data = data.decode('utf-8').strip()

        # Strip trailing command token.
        data = data[:-1]

        return data

    def reset(self, reset_type=None):
        """
        Perform a target reset

        Parameters
        ----------
        reset_type : openocd.ResetType, optional
            Determines what should happen after the target reset. If not
            provided or ``None``, target code execution is started after reset.
        """
        if reset_type is not None:
            reset_type = reset_type.value

        self.execute(self._fmt('reset {:s}', reset_type))

    def resume(self, address=None):
        """
        Resume the target execution.

        Parameters
        ----------
        address : int, optional
            If provided, resume the target execution at `address` instead of
            the current code position.
        """
        self.execute(self._fmt('resume {:x}', address))

    def halt(self):
        """Halt the target execution."""
        self.execute('halt')

    def shutdown(self):
        """Shutdown the OpenOCD server."""
        self.execute('shutdown')

    def step(self, address=None):
        """
        Perform a single-step on the target.

        Parameters
        ----------
        address : int, optional
            If provided, perform the single-step at `address` instead of the
            current code position.
        """
        self.execute(self._fmt('step {:x}', address))

    def targets(self):
        """
        Get the names of all available targets.

        Returns
        -------
        list of str
            Names of all available targets.
        """
        return self.execute('target names').split(' ')

    def target_types(self):
        """
        Get all supported target types.

        Returns
        -------
        list of str
            Types of all supported targets.
        """
        return self.execute('target types').split(' ')

    def current_target(self):
        """
        Get the name of the current target.

        Returns
        -------
        str
            Name of the current target.
        """
        return self.execute('target current')

    def read_memory(self, address, count, width, phys=False):
        """
        Read from target memory.

        Parameters
        ----------
        address : int
            Target memory address.
        count : int
            Number of words to read.
        width : int
            Memory access bit size.
        phys : bool, optional
            If this is set to True, treat the memory address as physical
            instead of virtual.

        Returns
        -------
        list of int
            List of words read from target memory.
        """

        if phys:
            phys = 'phys'
        else:
            phys = None

        response = self.execute(self._fmt('read_memory {:x} {:d} {:d} {:s}',
                                address, width, count, phys))
        return [int(x, 0) for x in response.split(' ')]

    def write_memory(self, address, data, width, phys=False):
        """
        Write to target memory.

        Parameters
        ----------
        address : int
            Target memory address.
        data : list of int
            List of words to write to the target memory.
        width : int
            Memory access bit size.
        phys : bool, optional
            If this is set to True, treat the memory address as physical
            instead of virtual.
        """

        if phys:
            phys = 'phys'
        else:
            phys = None

        tcl_list = '{' + ' '.join([hex(x) for x in data]) + '}'
        response = self.execute(self._fmt('write_memory {:x} {:d} {:s} {:s}',
                                address, width, tcl_list, phys))

        if response != '':
            raise Exception(response)

    def read_registers(self, registers, force=False):
        """
        Read target registers.

        Parameters
        ----------
        registers : list of str
            Register names.
        force : bool
            If set to True, register values are read directly from the target,
            bypassing any caching.

        Returns
        -------
        dict
            Dictionary containing the read register names and corresponding
            values.
        """

        if force:
            force = '-force'
        else:
            force = None

        tcl_list = '{' + ' '.join(registers) + '}'
        response = self.execute(self._fmt('get_reg {:s} {:s}',
                                force, tcl_list)).split(' ')

        registers = response[::2]
        values = [int(x, 0) for x in response[1::2]]

        return dict(zip(registers, values))

    def write_registers(self, values):
        """
        Write target registers.

        Parameters
        ----------
        values : dict
            Dictionary with register names and the corresponding values.
        """

        tcl_dict = ' '.join([self._fmt('{:s} {:x}', register, value) for
                            (register, value) in values.items()])
        response = self.execute(self._fmt('set_reg {{{:s}}}', tcl_dict))

        if response != '':
            raise Exception(response)
