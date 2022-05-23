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
from logging import Filter

from gevent.local import local

from pysolbase.Assert import Assert


class ContextFilter(Filter):
    """
    Context filter
    DOC : https://docs.python.org/3/howto/logging-cookbook.html#adding-contextual-information-to-your-logging-output
    """

    # CAUTION : We must target local here as global (otherwise its a variable local to functions)
    LOC = local()

    @classmethod
    def set_value(cls, k, v):
        """
        Set context value
        :param k: key name
        :type k: basestring
        :param v: value
        :type v: object
        """

        Assert.check(Exception, k is not None, "Need k, got None")
        Assert.check(Exception, len(k) > 0, "Need k, got empty")

        setattr(cls.LOC, k, v)

    def filter(self, record):
        """
        Record filter.
        This will push thread context (using LOC) toward logger item "kfilter", as an OrderedDict, formatted as "key0:value0 keyN:valueN"
        :param record: logging.LogRecord
        :type record: logging.LogRecord
        :return: bool
        :rtype bool
        """

        # Prepare
        s = u""
        for k in sorted(self.LOC.__dict__.keys()):
            v = self.LOC.__dict__[k]
            s += u" %s:%s" % (k, v)
        s += u" "

        # Push to record in a single shot
        setattr(record, "kfilter", s)

        return True
