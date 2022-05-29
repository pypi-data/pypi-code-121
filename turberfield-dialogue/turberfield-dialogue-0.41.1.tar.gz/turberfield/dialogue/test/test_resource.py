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

from collections import namedtuple
import copy
import enum
import sys
import textwrap
import unittest
import uuid

from turberfield.dialogue.model import Model
from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.types import Persona
from turberfield.dialogue.types import Player

class ResourceTests(unittest.TestCase):
    """This code provides an example of scripted resource discovery.

    In other words, you can write dialogue which introduces a player to
    a new ability or game artifact. You can make that resource available
    to the player from within the dialogue and at the point specified in the
    story.

    """

    phrases = [
        "Explicit is better than implicit",
        "Simple is better than complex",
        "Complex is better than complicated",
        "Readability counts",
        "Special cases aren't special enough to break the rules",
        "Practicality beats purity",
        "Errors should never pass silently"
    ]

    class Session:

        def __init__(self, host="localhost", id=None):
            self.host = host
            self.id = id or uuid.uuid4()
            self.resources = []

        @property
        def addition(self):
            return next(reversed(self.resources), None)

        @addition.setter
        def addition(self, item):
            self.resources.append(item)

    class Guru(Persona):
        pass

    Player = Player
    Resource = namedtuple("Resource", ["id", "label", "path"])

    def test_session(self):
        s = ResourceTests.Session()
        self.assertTrue(s.host)
        self.assertTrue(s.id)
        self.assertFalse(s.resources)

    def test_session_addition(self):
        s = ResourceTests.Session()
        self.assertIsNone(s.addition)
        s.addition = 1
        self.assertEqual(1, s.addition)
        self.assertTrue(s.resources)
        self.assertEqual([1], s.resources)

    def test_resource_activation(self):

        references = [
            ResourceTests.Resource(uuid.uuid4(), p, "phrases/{0}".format(n + 1))
            for n, p in enumerate(ResourceTests.phrases)
        ]
        references.extend([
            ResourceTests.Guru(name="Mr Tim Peters"),
            Player(name="tundish"),
            ResourceTests.Session()
        ])

        content = textwrap.dedent("""
            .. entity:: GURU
               :types: turberfield.dialogue.test.test_resource.ResourceTests.Guru

            .. entity:: SESSION
               :types: turberfield.dialogue.test.test_resource.ResourceTests.Session

            .. entity:: STUDENT
               :types: turberfield.dialogue.test.test_resource.ResourceTests.Player

            .. entity:: PHRASE
               :types: turberfield.dialogue.test.test_resource.ResourceTests.Resource

            Scene
            ~~~~~

            Shot
            ----

            [GURU]_

                Remember, |S_FIRSTNAME|. |PHRASE_LABEL|.

            .. Property attributes accept only integers and importable objects
            .. property:: SESSION.addition |PHRASE_ID|

            .. Use a Memory directive to generate an event containing formatted strings.
            .. Here, an integer state is used for 'learned'. A 0 could signify 'forgot'.
            .. memory:: 1
               :subject: SESSION
               :object: PHRASE

               |S_FIRSTNAME| learned phrase
               /|SESSION_ID|/|PHRASE_PATH|
               (|PHRASE_LABEL|).

            .. |S_FIRSTNAME| property:: STUDENT.name.firstname
            .. |SESSION_ID| property:: SESSION.id.hex
            .. |PHRASE_ID| property:: PHRASE.id.int
            .. |PHRASE_LABEL| property:: PHRASE.label
            .. |PHRASE_PATH| property:: PHRASE.path
            """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        cast = script.select(references, relative=True)
        self.assertTrue(all(cast.values()))
        script.cast(cast)
        model = script.run()
        items = list(model)
        p = [l for s, l in model if isinstance(l, Model.Property)][-1]
        self.assertEqual(references[0].id.int, p.val)
