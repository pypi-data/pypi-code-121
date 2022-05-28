#!/usr/bin/env python
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from turberfield.utils.orders import Orders

class TestOrders(unittest.TestCase):

    class StandingOrders(Orders):

        @Orders.register()
        def do_first(self):
            pass

        @Orders.register()
        def do_second(self):
            pass

        @Orders.register()
        def do_last(self):
            pass

    class EmergencyOrders(StandingOrders):

        @Orders.register()
        def do_second(self):
            pass

    class CancelledOrders(StandingOrders):

        def do_second(self):
            pass

    def test_simple_class(self):
        o = TestOrders.StandingOrders()
        self.assertEqual(
            ["do_first", "do_second", "do_last"],
            [i[1] for i in o.sequence]
        )

    def test_subclass(self):
        o = TestOrders.EmergencyOrders()
        self.assertEqual(
            ["do_first", "do_second", "do_last"],
            [i[1] for i in o.sequence]
        )

    def test_override(self):
        o = TestOrders.CancelledOrders()
        self.assertEqual(
            ["do_first", "do_last"],
            [i[1] for i in o.sequence]
        )
