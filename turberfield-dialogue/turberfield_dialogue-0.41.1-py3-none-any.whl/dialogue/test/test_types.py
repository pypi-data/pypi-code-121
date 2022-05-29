#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from turberfield.dialogue.types import Name
from turberfield.dialogue.types import Player
from turberfield.dialogue.types import Stateful

from turberfield.utils.assembly import Assembly

class TestStateful(unittest.TestCase):

    def test_state_as_int(self):
        s = Stateful()
        s.set_state(3)
        self.assertEqual(3, s.get_state())
        self.assertEqual(3, s.state)

    def test_state_as_int_twice(self):
        s = Stateful()
        s.set_state(3).set_state(4)
        self.assertEqual(4, s.get_state())
        self.assertEqual(4, s.state)

    def test_state_as_int_args(self):
        s = Stateful()
        s.set_state(3, 4)
        self.assertEqual(4, s.get_state())
        self.assertEqual(4, s.state)


class TestPlayer(unittest.TestCase):

    def test_no_name(self):
        player = Player(name=None)
        self.assertIsNone(player._name)
        self.assertIsNone(player.name)

    def test_round_trip_assembly(self):
        Assembly.register(Player)
        player = Player(name="Mr Dick Turpin").set_state(12)
        text = Assembly.dumps(player)
        clone = Assembly.loads(text)
        self.assertEqual(player.id, clone.id)
        self.assertEqual(player.name, clone.name)
        self.assertEqual(player.state, clone.state)
