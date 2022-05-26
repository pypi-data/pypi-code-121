#!/usr/bin/env python3
#   encoding: UTF-8

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
import datetime
import io
import itertools
import logging
import textwrap
import unittest
import uuid

from turberfield.utils.misc import config_parser
from turberfield.utils.misc import ConfiguredSettings
from turberfield.utils.misc import clone_config_section
from turberfield.utils.misc import group_by_type
from turberfield.utils.misc import log_setup
from turberfield.utils.misc import reference_config_section
from turberfield.utils.misc import Singleton


class HelperTests(unittest.TestCase):

    def test_group_by_type(self):
        items = [1, 0, "b", 0.8, "a", 0.3, 4]
        rv = group_by_type(items)
        self.assertEqual([1, 0, 4], rv[int])
        self.assertEqual(["b", "a"], rv[str])
        self.assertEqual([0.8, 0.3], rv[float])

    def test_log_setup(self):
        args = argparse.Namespace(
            log_level=logging.DEBUG,
            log_path=None
        )
        log_name = log_setup(args)
        log = logging.getLogger(log_name)
        log.debug("Test message")

class ConfigTests(unittest.TestCase):

    def test_defaults(self):
        defaults = {"a": 1, "b": "two", "c": None}
        cfg = config_parser(**defaults)
        witness = io.StringIO()
        cfg.write(witness)
        for check in ["[DEFAULT]", "a = 1", "b = two", "c"]:
            with self.subTest(check=check):
                self.assertIn(check, witness.getvalue().splitlines())

    def test_section(self):
        section = textwrap.dedent("""
        [section.one]
        root = /home

        [section.two]
        path = ${section.one:root}/tmp
        """)
        cfg = config_parser(section)
        self.assertEqual("/home/tmp", cfg["section.two"]["path"])

    def test_sections(self):
        sections = [
            "[section.one]\nroot = /home",
            "[section.two]\npath = ${section.one:root}/tmp"
        ]
        cfg = config_parser(*sections)
        self.assertEqual("/home/tmp", cfg["section.two"]["path"])

    def test_defaults_and_sections(self):
        defaults = {"a": 1, "b": "two", "c": None}
        sections = [
            "[section.one]\nroot = /home",
            "[section.two]\npath = ${section.one:root}/tmp",
            "[section.three]\npath = ${section.two:path}.${b}"
        ]
        cfg = config_parser(*sections, **defaults)
        self.assertEqual("/home/tmp.two", cfg["section.three"]["path"])

    def test_clone_config_section(self):
        cfg = config_parser()
        cfg.read_string(textwrap.dedent(
        """
        [DEFAULT]
        a = 1

        [unittest]
        b = 2
        c =
        listen_addr = 127.0.0.1
        """
        ))

        guid = uuid.uuid4().hex
        expected = textwrap.dedent(
        """
        [{guid}]
        b = ${{unittest:b}}
        c = ${{unittest:c}}
        listen_addr = ${{unittest:listen_addr}}
        listen_port = 8081""").format(guid=guid)

        rv = "\n".join(clone_config_section(cfg, "unittest", guid, listen_port=8081))
        self.assertEqual(expected, rv)
        cfg.read_string(rv)

        self.assertEqual("1", cfg[guid]["a"])
        self.assertEqual("2", cfg[guid]["b"])
        self.assertEqual("", cfg[guid]["c"])
        self.assertEqual("127.0.0.1", cfg[guid]["listen_addr"])
        self.assertEqual("8081", cfg[guid]["listen_port"])

    def test_reference_config_section(self):
        cfg = config_parser()
        cfg.read_string(textwrap.dedent(
        """
        [DEFAULT]
        hash = #

        [unittest]
        listen_addr = 127.0.0.1

        [d6c047b17e9a4bb3b4a658ff0e4029c6]
        extern_addr = 0.0.0.0
        extern_port = 8080
        listen_addr = 127.0.0.1
        listen_port = 15151
        """
        ))

        guid = uuid.uuid4().hex
        expected = textwrap.dedent(
        """
        [{guid}]
        listen_addr = ${{unittest:listen_addr}}
        listen_port = 15151
        parent_addr = ${{d6c047b17e9a4bb3b4a658ff0e4029c6:listen_addr}}
        parent_port = ${{d6c047b17e9a4bb3b4a658ff0e4029c6:listen_port}}""").format(guid=guid)

        rv = "\n".join(itertools.chain(
            clone_config_section(cfg, "unittest", guid, listen_port=15151),
            reference_config_section(
                cfg, "d6c047b17e9a4bb3b4a658ff0e4029c6", guid,
                parent_addr="listen_addr", parent_port="listen_port"),
        ))
        self.assertEqual(set(expected.splitlines()), set(rv.splitlines()))

class MixinTests(unittest.TestCase):

    class Expert(Singleton, ConfiguredSettings):
        pass

    def tearDown(self):
        MixinTests.Expert._instance = None

    def test_singleton(self):
        a = MixinTests.Expert(cfg=ConfiguredSettings.config_parser())
        b = MixinTests.Expert.instance()
        self.assertIs(b, a)

    def test_settings_bad(self):

        class Invalid(MixinTests.Expert):
            @classmethod
            def check_config(cls, cfg):
                return None

        rv = Invalid(cfg=Invalid.config_parser())
        self.assertIsNone(rv.settings)

    def test_settings_good(self):
        cfg = MixinTests.Expert.config_parser()
        rv = MixinTests.Expert(cfg=cfg)
        self.assertTrue(hasattr(rv, "settings"))
        self.assertIs(cfg, rv.settings)

    def test_events(self):

        class Clock(MixinTests.Expert):

            @property
            @classmethod
            def value(cls):
                return cls._instance.val

            def __init__(self, *args, start=None, **kwargs):
                self.val = start

            def advance(self):
                self.val += datetime.timedelta(seconds=30)

        a = Clock(start=datetime.datetime.now(), cfg=Clock.config_parser())
        start = a.val
        a.advance()
        self.assertGreater(a.val, start)

        b = Clock.instance()
        self.assertGreater(b.val, start)
