#
# This file is part of the python-openocd project.
#
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
This module contains a Formatter for Tcl commands.
"""

from string import Formatter


class TclFormatter(Formatter):
    """
    A Formatter for convenient generation of Tcl commands.
    """
    def format_field(self, value, format_spec):
        if value is None:
            return ''

        if format_spec in ['x', 'X']:
            return '0x' + super().format_field(value, format_spec)

        return super().format_field(value, format_spec)
