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

import argparse
import collections.abc
from collections import namedtuple
import datetime
import enum
import io
import logging
import os
import sys
import textwrap
import tempfile
import unittest
import uuid

from turberfield.dialogue.model import Model
from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.sequences.battle.logic import Animal
from turberfield.dialogue.sequences.battle.logic import Tool
try:
    import turberfield.dialogue.viewer as viewer
except ImportError:
    viewer = None

import pkg_resources


class LoaderTests(unittest.TestCase):

    def test_scripts(self):
        folder = SceneScript.Folder(
            "turberfield.dialogue.sequences.battle.logic", "test", None,
            ["combat.rst"], None
        )
        rv = list(SceneScript.scripts(**folder._asdict()))
        self.assertEqual(1, len(rv))
        self.assertIsInstance(rv[0], SceneScript)

    def test_scripts_bad_pkg(self):
        folder = SceneScript.Folder(
            "turberfield.dialogue.sequences.not_there", "test", None,
            ["combat.rst"], None
        )
        rv = list(SceneScript.scripts(**folder._asdict()))
        self.assertFalse(rv)

    def test_scripts_bad_scenefile(self):
        folder = SceneScript.Folder(
            "turberfield.dialogue.sequences.battle.logic", "test", None,
            ["not_there.rst"], None
        )
        rv = list(SceneScript.scripts(**folder._asdict()))
        self.assertFalse(rv)


class CastingTests(unittest.TestCase):

    Persona = namedtuple("Persona", ["uuid", "title", "names"])
    Location = namedtuple("Location", ["name", "capacity"])

    def setUp(self):
        self.personae = {
            Animal(name="Itchy").set_state(1),
            Animal(name="Scratchy").set_state(1),
            Tool(name="Rusty Chopper").set_state(1),
        }
        folder = SceneScript.Folder(
            "turberfield.dialogue.sequences.battle.logic", "test", None,
            ["combat.rst"], None
        )
        self.script = next(SceneScript.scripts(**folder._asdict()))

    def test_casting_adds_citation_definition(self):
        with self.script as script:
            self.assertFalse(script.doc.citations)
            self.assertEqual(3, len(script.doc.citation_refs))
            casting = script.select(self.personae)
            self.assertIsInstance(casting, collections.abc.Mapping, casting)
            script.cast(casting)
            self.assertEqual(3, len(script.doc.citations))
            self.assertEqual(3, len(script.doc.citation_refs))

    def test_casting_respects_type(self):
        for n in range(16):
            self.setUp()
            with self.subTest(n=n), self.script as script:
                casting = script.select(self.personae)
                c, p = next((c, p) for c, p in casting.items() if "fighter_2" in c["names"])
                self.assertIsInstance(p, Animal, p)

    @unittest.skipUnless(viewer, "Could not import viewer")
    def test_cgi(self):
        p = viewer.parser()
        fd, fp = tempfile.mkstemp(suffix=".db")
        try:
            ns = p.parse_args([
                "--references", "turberfield.dialogue.sequences.battle.logic:references",
                "--folder", "turberfield.dialogue.sequences.battle.logic:folder",
                "--db", fp,
                "--pause", "0.5", "--dwell", "0.1",
                "--repeat", "1", "--roles", "2", "--strict"
            ])
            stream = io.StringIO()
            then = datetime.datetime.now()
            rv = list(viewer.cgi_producer(ns, stream))
            elapsed = datetime.datetime.now() - then
            self.assertTrue(5 <= elapsed.seconds <= 7, elapsed.seconds)

            lines = stream.getvalue().splitlines()
            self.assertEqual("Content-type:text/event-stream", lines[0])
            self.assertEqual("", lines[1])
            seq = iter(lines[2:])
            for i in range(6):
                with self.subTest(i=i):
                    line = next(seq)
                    self.assertTrue(line.startswith("event:"))
                    line = next(seq)
                    self.assertTrue(line.startswith("data:"))
                    line = next(seq)
                    self.assertFalse(line)
        finally:
            os.close(fd)
            os.remove(fp)

    def test_run(self):
        #self.assertTrue(all(i.state for i in self.personae))
        with self.script as script:
            model = script.cast(script.select(self.personae)).run()
            for n, (shot, item) in enumerate(model):
                self.assertIsInstance(shot, Model.Shot)
                self.assertIsInstance(
                    item,
                    (Model.Audio, Model.Property, Model.Line, Model.Memory)
                )
