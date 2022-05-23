"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2017 Laurent Labatut / Laurent Champagnac
#
#
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


class Assert(object):
    """
    Assert helpers
    """

    @classmethod
    def check(cls, exception_class, condition, message, *args, **kwargs):
        """
        Check a condition and, if false, raise provided exception with provided message.
        :param exception_class: Exception class to raise if condition is False.
        :type exception_class: callable
        :param condition: Condition to evaluate. If false, will raise. If dict|tuple|list is empty, will raise.
        :type condition: bool,list,tuple,dict
        :param message: Exception message
        :type message: basestring
        """

        if condition:
            return

        raise exception_class(message, *args, **kwargs)
