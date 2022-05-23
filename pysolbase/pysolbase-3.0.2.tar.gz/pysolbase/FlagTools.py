"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2017 Laurent Labatut / Laurent Champagnac
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""


class FlagTools(object):
    """
    Flag tools
    """

    @classmethod
    def is_set(cls, val, flags):
        """
        Check if all bit in flags are set in val
        :param val: int
        :type val: int
        :param flags: int
        :type flags: int
        :return bool
        :rtype bool
        """

        if (val & flags) == flags:
            return True
        else:
            return False

    @classmethod
    def set(cls, val, flags):
        """
        Add all bits in flags inside val, return new val
        :param val: int
        :type val: int
        :param flags: int
        :type flags: int
        :return int
        :rtype int
        """

        return val | flags

    @classmethod
    def clear(cls, val, flags):
        """
        Clear all bits in flags inside val, return new val
        :param val: int
        :type val: int
        :param flags: int
        :type flags: int
        :return int
        :rtype int
        """
        return val & ~flags
