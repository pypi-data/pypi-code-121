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
from collections import OrderedDict
import datetime
import enum
import unittest

from turberfield.dialogue.schema import SchemaBase
from turberfield.utils.db import Connection
from turberfield.utils.db import Creation
from turberfield.utils.db import Insertion
from turberfield.utils.db import Table
from turberfield.utils.misc import gather_installed
from turberfield.utils.test.test_db import DBTests


class SQLTests(unittest.TestCase):

    def test_create_entity(self):
        expected = "\n".join((
            "create table if not exists entity(",
            "id INTEGER PRIMARY KEY NOT NULL,",
            "name TEXT  NOT NULL UNIQUE",
            ")"
        ))
        rv = Creation(SchemaBase.tables["entity"]).sql
        self.assertEqual(2, len(rv))
        self.assertEqual(expected, rv[0])

    def test_insert_entity(self):
        expected = (
            "insert into entity (name) values (:name)",
            {"name": "qwerty"}
        )
        rv = Insertion(
            SchemaBase.tables["entity"],
            data=dict(
                name="qwerty"
            )
        ).sql
        self.assertEqual(expected, rv)

    def test_create_touch(self):
        expected = "\n".join((
            "create table if not exists touch(",
            "id INTEGER PRIMARY KEY NOT NULL,",
            "ts timestamp  NOT NULL,",
            "sbjct INTEGER  NOT NULL,",
            "state INTEGER  NOT NULL,",
            "objct INTEGER,",
            "FOREIGN KEY (sbjct) REFERENCES entity(id)",
            "FOREIGN KEY (state) REFERENCES state(id)",
            "FOREIGN KEY (objct) REFERENCES entity(id)",
            ")"
        ))
        rv = Creation(SchemaBase.tables["touch"]).sql
        self.assertEqual(2, len(rv))
        self.assertEqual(expected, rv[0])

class DBTests:

    @staticmethod
    def get_tables(con):
        cur = con.cursor()
        try:
            cur.execute("select * from sqlite_master where type='table'")
            return [
                OrderedDict([(k, v)
                for k, v in zip(i.keys(), i)])
                for i in cur.fetchall()
            ]
        finally:
            cur.close()

class TableTests(DBTests, unittest.TestCase):

    def test_creation_sql(self):
        table = Table(
            "records",
            cols=[
              Table.Column("id", int, True, False, None, None, None),
              Table.Column("ts", datetime.datetime, False, False, None, None, None),
              Table.Column("valid", bool, False, True, None, None, None),
              Table.Column("data", str, False, True, None, None, None),
            ]
        )
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(table).run(db)
            n = len(self.get_tables(db))
            self.assertEqual(1, n)

    def test_state_tables(self):
        states = dict(gather_installed("turberfield.dialogue.states"))
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(
                *SchemaBase.tables.values()
            ).run(db)
            tables = self.get_tables(db)
            self.assertIn("state", [t.get("name") for t in tables])

class SchemaBaseTests(DBTests, unittest.TestCase):

    @enum.unique
    class Ownership(enum.IntEnum):
        lost = 0
        acquired = 1


    @enum.unique
    class Visibility(enum.IntEnum):
        invisible = 0
        visible = 1

    def setUp(self):
        self.db = Connection(**Connection.options())
        with self.db as con:
            with con as change:
                rv = Creation(
                    *SchemaBase.tables.values()
                ).run(change)

    def tearDown(self):
        with self.db as con:
            con.close()

    def test_populate_states(self):

        with self.db as con:
            rv = SchemaBase.populate(
                con,
                [SchemaBaseTests.Ownership, SchemaBaseTests.Visibility]
            )
            self.assertEqual(4, rv)

            cur = con.cursor()
            cur.execute("select count(*) from state")
            rv = tuple(cur.fetchone())[0]
            self.assertEqual(4, rv)

            cur.execute("select * from state")
            self.assertEqual(
                {"Ownership", "Visibility"},
                {row["class"] for row in cur.fetchall()}
            )

    def test_reference_states(self):

        with self.db as con:
            SchemaBase.populate(
                con,
                [SchemaBaseTests.Ownership, SchemaBaseTests.Visibility]
            )

            rv = list(SchemaBase.reference(
                con,
                [SchemaBaseTests.Ownership.lost, SchemaBaseTests.Visibility.visible]
            ))
            self.assertEqual(2, len(rv))
            self.assertEqual(SchemaBaseTests.Ownership.lost.value, rv[0]["value"])
            self.assertEqual(SchemaBaseTests.Visibility.visible.value, rv[1]["value"])

    def test_populate(self):

        Thing = namedtuple("Thing", ["name"])
        with self.db as con:
            rv = SchemaBase.populate(
                con, [
                    SchemaBaseTests.Ownership, SchemaBaseTests.Visibility,
                    Thing("apple"), Thing("ball"), Thing("cat")
                ]
            )
            self.assertEqual(7, rv)

            cur = con.cursor()
            cur.execute("select count(*) from entity")
            rv = tuple(cur.fetchone())[0]
            self.assertEqual(3, rv)

            cur.execute("select * from entity")
            self.assertEqual(
                {"apple", "ball", "cat"},
                {row["name"] for row in cur.fetchall()}
            )

    def test_reference_entity(self):

        Thing = namedtuple("Thing", ["name"])
        with self.db as con:
            rv = SchemaBase.populate(
                con, [
                    Thing("apple"), Thing("ball"), Thing("cat")
                ]
            )
            rv = list(SchemaBase.reference(
                con,
                [Thing("ball"), Thing("dog")]
            ))
            self.assertEqual(2, len(rv))
            self.assertEqual("ball", rv[0]["name"])
            self.assertIs(None, rv[1])

    def test_populate_duplicates(self):

        with self.db as con:
            rv = SchemaBase.populate(
                con, [
                    SchemaBaseTests.Ownership, SchemaBaseTests.Visibility,
                    SchemaBaseTests.Visibility
                ]
            )
            self.assertEqual(4, rv)

            cur = con.cursor()
            cur.execute("select count(*) from state")
            rv = tuple(cur.fetchone())[0]
            self.assertEqual(4, rv)

            cur.execute("select * from state")
            self.assertEqual(
                {"Ownership", "Visibility"},
                {row["class"] for row in cur.fetchall()}
            )

    def test_touch_intransitive(self):

        Thing = namedtuple("Thing", ["name"])
        with self.db as con:
            rv = SchemaBase.populate(
                con, [
                    SchemaBaseTests.Visibility,
                    Thing("cat")
                ]
            )

            rv = SchemaBase.touch(
                con,
                Thing("cat"),
                SchemaBaseTests.Visibility.visible
            )

            cur = con.cursor()
            cur.execute("select count(*) from touch")
            rv = tuple(cur.fetchone())[0]
            self.assertEqual(1, rv)

            cur.execute(
                "select s.name, state.name, o.name "
                "from state join touch on state.id = touch.state "
                "join entity as s on touch.sbjct = s.id "
                "left outer join entity as o on touch.objct = o.id"
            )
            self.assertEqual(("cat", "visible", None), tuple(cur.fetchone()))

    def test_touch_transitive(self):

        Thing = namedtuple("Thing", ["name"])
        with self.db as con:
            rv = SchemaBase.populate(
                con, [
                    SchemaBaseTests.Ownership,
                    Thing("cat"),
                    Thing("hat")
                ]
            )

            rv = SchemaBase.touch(
                con,
                Thing("cat"),
                SchemaBaseTests.Ownership.acquired,
                Thing("hat"),
            )

            cur = con.cursor()
            cur.execute("select count(*) from touch")
            rv = tuple(cur.fetchone())[0]
            self.assertEqual(1, rv)

            cur.execute(
                "select s.name, state.name, o.name "
                "from state join touch on state.id = touch.state "
                "join entity as s on touch.sbjct = s.id "
                "left outer join entity as o on touch.objct = o.id"
            )
            self.assertEqual(("cat", "acquired", "hat"), tuple(cur.fetchone()))

    def test_note_transitive(self):

        Thing = namedtuple("Thing", ["name"])
        with self.db as con:
            rv = SchemaBase.populate(
                con, [
                    SchemaBaseTests.Ownership,
                    Thing("cat"),
                    Thing("hat")
                ]
            )

            rv = SchemaBase.note(
                con,
                Thing("cat"),
                SchemaBaseTests.Ownership.acquired,
                Thing("hat"),
                text="A cat in a hat!"
            )

            cur = con.cursor()
            cur.execute("select count(*) from touch")
            rv = tuple(cur.fetchone())[0]
            self.assertEqual(1, rv)

            cur.execute(
                "select s.name, state.name, o.name, note.text "
                "from state join touch on state.id = touch.state "
                "join entity as s on touch.sbjct = s.id "
                "left outer join entity as o on touch.objct = o.id "
                "left outer join note on note.touch = touch.id"
            )
            self.assertEqual(("cat", "acquired", "hat", "A cat in a hat!"), tuple(cur.fetchone()))
