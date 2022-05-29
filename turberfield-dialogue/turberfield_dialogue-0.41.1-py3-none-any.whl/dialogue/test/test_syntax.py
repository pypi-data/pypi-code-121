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


import textwrap
import unittest

from turberfield.dialogue.model import SceneScript


class CitationTests(unittest.TestCase):

    def test_regular_citations(self):
        content = textwrap.dedent("""
        .. [NARRATOR]   Dialogue under development. No entities yet.

        [NARRATOR]_

            And they lived happily ever after.
        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([]))
        model = list(script.run())
        items = list(model)
        self.assertEqual(1, len(items), items)
        shot, line = items[0]
        self.assertIs(None, shot.scene)
        self.assertIs(None, shot.name)
        self.assertEqual("narrator", line.persona)

    def test_missing_citations(self):
        content = textwrap.dedent("""
        [NARRATOR]_

            And they lived happily ever after.
        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([]))
        model = list(script.run())
        items = list(model)
        self.assertEqual(1, len(items), items)
        shot, line = items[0]
        self.assertIs(None, shot.scene)
        self.assertIs(None, shot.name)
        self.assertEqual("narrator", line.persona)
