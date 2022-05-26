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
import glob
import os.path
import sqlite3
import tempfile
import unittest
import uuid

from turberfield.utils.db import Connection
from turberfield.utils.db import Creation
from turberfield.utils.db import Insertion
from turberfield.utils.db import SQLOperation
from turberfield.utils.db import Table
from turberfield.utils.misc import gather_installed


schema = OrderedDict([])
lookup = OrderedDict([])

schema.update(dict(
    (table.name, table) for table in [
    Table(
        "entity",
        cols=[
          Table.Column("id", int, True, False, False, None, None),
          Table.Column("session", str, False, False, True, None, None),
          Table.Column("name", str, False, False, True, None, None),
        ],
        lookup=lookup
    ),
    Table(
        "state",
        cols=[
          Table.Column("id", int, True, False, False, None, None),
          Table.Column("class", str, False, False, True, None, None),
          Table.Column("name", str, False, False, True, None, None),
          Table.Column("value", int, False, False, False, None, None),
        ],
        lookup=lookup
    ),
    Table(
        "touch",
        cols=[
          Table.Column("sbjct", int, False, False, False, None, "entity"),
          Table.Column("objct", int, False, True, False, None, "entity"),
        ],
        lookup=lookup
    )
]))

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

class NeedsTempDirectory:

    def setUp(self):
        self.drcty = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.drcty.name):
            self.drcty.cleanup()
        self.assertFalse(os.path.isdir(self.drcty.name))
        self.drcty = None

class InsertionTests(NeedsTempDirectory, unittest.TestCase):

    def test_one_db_in_memory(self):
        con = Connection(**Connection.options())
        self.assertIsNone(con.db)
        with con as db:
            self.assertTrue(con.db)

    def test_not_null(self):
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(schema["entity"]).run(db)
            self.assertRaises(
                sqlite3.IntegrityError,
                Insertion(
                    schema["entity"],
                    data=dict(
                        session=uuid.uuid4().hex
                    )
                ).run,
                db
            )

    def test_primary_keys(self):
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(schema["entity"]).run(db)
            session=uuid.uuid4().hex
            rv = Insertion(
                schema["entity"],
                data=dict(
                    name="test",
                    session=session
                )
            ).run(db)
            self.assertRaises(
                sqlite3.IntegrityError,
                Insertion(
                    schema["entity"],
                    data=dict(
                        session=session
                    )
                ).run,
                db
            )

    def test_foreign_keys(self):
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(schema["touch"]).run(db)
            session=uuid.uuid4().hex
            self.assertRaises(
                sqlite3.OperationalError,
                Insertion(
                    schema["touch"],
                    data=dict(
                        sbjct=1,
                        objct=1
                    )
                ).run,
                db
            )

    def test_insertion_keys(self):
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(schema["touch"]).run(db)
            session=uuid.uuid4().hex
            self.assertRaises(
                sqlite3.OperationalError,
                Insertion(
                    schema["touch"],
                    data=dict(
                        sbjct=1,
                        objct=1
                    )
                ).run,
                db
            )

    def test_insertion_entity(self):
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(schema["entity"]).run(db)
            session=uuid.uuid4().hex
            Insertion(
                schema["entity"],
                data=dict(
                    session=session,
                    name="test"
                )
            ).run(db)
            cur = db.cursor()
            cur.execute("select * from entity")
            rv = cur.fetchall()
            self.assertEqual(1, len(rv))
            self.assertEqual(rv[0]["id"], 1)
            self.assertEqual(rv[0]["name"], "test")

    def test_insertion_entities(self):
        con = Connection(**Connection.options())
        session = uuid.uuid4().hex
        with con as db:
            rv = Creation(schema["entity"]).run(db)
            Insertion(
                schema["entity"],
                data=[
                    {"name": "test_one", "session": session},
                    {"name": "test_two", "session": session}
                ]
            ).run(db)
            cur = db.cursor()
            cur.execute("select * from entity")
            rv = cur.fetchall()
            self.assertEqual(2, len(rv))
            self.assertEqual(rv[0]["id"], 1)
            self.assertEqual(rv[0]["name"], "test_one")
            self.assertEqual(rv[1]["id"], 2)
            self.assertEqual(rv[1]["name"], "test_two")

    def test_selection_entity(self):
        class Selection(SQLOperation):

            @property
            def sql(self):
                return ("select * from {0.name}".format(self.tables[0]) , {})

        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(schema["entity"]).run(db)
            session = uuid.uuid4().hex
            cur = Insertion(
                schema["entity"],
                data=dict(
                    session=session,
                    name="test"
                )
            ).run(db)

            rv = Selection(schema["entity"]).run(db)
            rows = rv.fetchall()
            self.assertEqual(1, len(rows))
            self.assertEqual(rows[0]["id"], 1)
            self.assertEqual(rows[0]["name"], "test")

class SQLTests(unittest.TestCase):

    def test_create_entity(self):
        expected = "\n".join((
            "create table if not exists entity(",
            "id INTEGER PRIMARY KEY NOT NULL,",
            "session TEXT  NOT NULL,",
            "name TEXT  NOT NULL,",
            "UNIQUE(session, name)",
            ")"
        ))
        rv = Creation(schema["entity"]).sql
        self.assertEqual(2, len(rv))
        self.assertEqual(expected, rv[0])

    def test_insert_entity(self):
        expected = (
            "insert into entity (session, name) values (:session, :name)",
            {"session": "1234567890", "name": "qwerty"}
        )
        rv = Insertion(
            schema["entity"],
            data=dict(
                session="1234567890",
                name="qwerty"
            )
        ).sql
        self.assertEqual(expected, rv)

    def test_create_touch(self):
        expected = "\n".join((
            "create table if not exists touch(",
            "sbjct INTEGER  NOT NULL,",
            "objct INTEGER,",
            "FOREIGN KEY (sbjct) REFERENCES entity(id)",
            "FOREIGN KEY (objct) REFERENCES entity(id)",
            ")"
        ))
        rv = Creation(schema["touch"]).sql
        self.assertEqual(2, len(rv))
        self.assertEqual(expected, rv[0])

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
        states = dict(gather_installed("turberfield.utils.states"))
        con = Connection(**Connection.options())
        with con as db:
            rv = Creation(*schema.values()).run(db)
            tables = self.get_tables(db)
            self.assertIn("state", [t.get("name") for t in tables])

class OptionTests(NeedsTempDirectory, unittest.TestCase):

    @staticmethod
    def make_db_files(tempdir, n):
        for i in range(n):
            fd, path = tempfile.mkstemp(
                dir=tempdir.name,
                suffix=".db"
            )
            yield fd, path

    @staticmethod
    def close_db_files(*items):
        for fd, path in items:
            os.close(fd)

    def test_one_db_in_memory(self):
        rv = Connection.options()
        self.assertIsInstance(rv, dict)
        self.assertEqual(1, len(rv["attach"]))
        self.assertIn(
            Connection.CacheOptions.shared,
            list(rv["attach"].values())[0]
        )

    def test_one_db_from_file(self):
        fd, path = next(OptionTests.make_db_files(self.drcty, 1))
        paths = glob.glob(os.path.join(self.drcty.name, "*.db"))
        self.assertEqual(1, len(paths)) 
        OptionTests.close_db_files((fd, path))
        rv = Connection.options(paths=paths)
        self.assertIsInstance(rv, dict)
        self.assertEqual(1, len(rv["attach"]))
        self.assertIn(
            Connection.ModeOptions.read_write_create,
            list(rv["attach"].values())[0]
        )

    def test_ten_db_from_file(self):
        items = list(OptionTests.make_db_files(self.drcty, 10))
        paths = glob.glob(os.path.join(self.drcty.name, "*.db"))
        self.assertEqual(10, len(paths)) 
        OptionTests.close_db_files(*items)
        rv = Connection.options(paths=paths)
        self.assertIsInstance(rv, dict)
        self.assertEqual(11, len(rv["attach"]))
        name, options = rv["attach"].popitem(last=False)
        self.assertEqual(":memory:", name)
        self.assertIn(Connection.ModeOptions.memory, options)
        self.assertTrue(all(
            Connection.ModeOptions.read in i
            for i in rv["attach"].values())
        )
