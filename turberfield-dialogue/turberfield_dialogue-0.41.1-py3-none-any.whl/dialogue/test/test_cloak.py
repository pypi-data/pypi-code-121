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


from collections import Counter
from collections.abc import Callable
import copy
import itertools
import unittest

from turberfield.dialogue.model import Model
from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.player import rehearse
from turberfield.dialogue.sequences.cloak.logic import references
from turberfield.dialogue.sequences.cloak.logic import game
from turberfield.dialogue.sequences.cloak.logic import Garment
from turberfield.dialogue.sequences.cloak.logic import Location
from turberfield.dialogue.sequences.cloak.logic import Narrator


class CastingTests(unittest.TestCase):

    def setUp(self):
        self.references = references
        self.folder = copy.deepcopy(game)

    def test_foyer_scenescript(self):
        script = next(SceneScript.scripts(**self.folder._asdict()))
        with script as scene:
            model = scene.cast(scene.select(self.references)).run()
            for n, (shot, item) in enumerate(model):
                self.assertIsInstance(shot, Model.Shot)
                self.assertIsInstance(
                    item,
                    (Model.Audio, Model.Property, Model.Line, Model.Memory)
                )

                if isinstance(item, Model.Memory):
                    self.assertEqual(Location.foyer, item.state)
                    self.assertTrue(item.text)
                    self.assertFalse("|" in item.text)
                    self.assertTrue(item.html)
                    self.assertFalse("|" in item.html)

class SceneTests(unittest.TestCase):

    def setUp(self):
        self.references = references
        self.folder = copy.deepcopy(game)

    def test_locations(self):
        narrator = next(i for i in self.references if isinstance(i, Narrator))
        cloak = next(i for i in self.references if isinstance(i, Garment))

        class MockHandler:

            def __init__(self, parent, folder, references):
                self.parent = parent
                self.folder = folder
                self.references = references
                self.calls = 0
                self.visits = Counter()

            def __call__(self, obj, *args, **kwargs):
                if isinstance(obj, Callable):
                    self.calls += 1
                    interlude = obj
                    folder, index, ensemble = args
                    rv = None
                    if folder.paths[index] == "foyer.rst":
                        self.visits["foyer"] += 1
                        self.parent.assertEqual(Location.foyer, narrator.get_state(Location))
                        if self.visits["foyer"] == 1:
                            rv = interlude(folder, index, self.references, cmd="south")
                            self.parent.assertEqual({}, rv)
                            self.parent.assertEqual(Location.bar, narrator.get_state(Location))
                        elif self.visits["foyer"] == 2:
                            rv = interlude(folder, index, self.references, cmd="west")
                            self.parent.assertEqual({}, rv)
                            self.parent.assertEqual(Location.cloakroom_space, narrator.get_state(Location))
                        else:
                            self.parent.assertEqual(3, self.visits["foyer"])

                    elif folder.paths[index] == "bar.rst":
                        self.visits["bar"] += 1
                        self.parent.assertEqual(1, self.visits["foyer"])
                        self.parent.assertEqual(Location.bar, narrator.get_state(Location))
                        rv = interlude(folder, index, self.references, cmd="north")
                        self.parent.assertEqual({}, rv)
                        self.parent.assertEqual(Location.foyer, narrator.get_state(Location))

                    elif folder.paths[index] == "cloakroom.rst":
                        self.visits["cloakroom"] += 1
                        if self.visits["cloakroom"] == 1:
                            self.parent.assertEqual(Location.cloakroom_space, narrator.get_state(Location))
                            rv = interlude(folder, index, self.references, cmd="drop cloak")
                            self.parent.assertEqual({}, rv)
                            self.parent.assertEqual(Location.cloakroom_floor, cloak.get_state(Location))

                        elif self.visits["cloakroom"] == 2:
                            rv = interlude(folder, index, self.references, cmd="get cloak")
                            self.parent.assertEqual({}, rv)
                            self.parent.assertEqual(Location.cloakroom_space, cloak.get_state(Location))

                        elif self.visits["cloakroom"] == 3:
                            rv = interlude(folder, index, self.references, cmd="put cloak on hook")
                            self.parent.assertEqual({}, rv)
                            self.parent.assertEqual(Location.cloakroom_hook, cloak.get_state(Location))

                        elif self.visits["cloakroom"] == 4:
                            rv = interlude(self.folder, index, self.references, cmd="east")
                            self.parent.assertEqual({}, rv)
                            self.parent.assertEqual(Location.foyer, narrator.get_state(Location))
                            self.parent.assertEqual(Location.cloakroom_hook, cloak.get_state(Location))
                            self.parent.assertEqual(Location.foyer, narrator.get_state(Location))

                    yield rv
                else:
                    yield obj

        test_handler = MockHandler(self, self.folder, self.references)
        rv = list(rehearse(
            self.folder, self.references, test_handler, repeat=8, roles=1
        ))
        #self.assertEqual(137, len(rv), rv)
        self.assertEqual(8, test_handler.calls)
        self.assertEqual(3, test_handler.visits["foyer"])
        self.assertEqual(1, test_handler.visits["bar"])
        self.assertEqual(4, test_handler.visits["cloakroom"])
