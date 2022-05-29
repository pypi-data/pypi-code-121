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

from collections import OrderedDict
import datetime
import enum
import sqlite3

from turberfield.utils.db import Insertion
from turberfield.utils.db import SQLOperation
from turberfield.utils.db import Table
from turberfield.utils.logger import LogManager


class SchemaBase:

    tables = OrderedDict(
        (table.name, table) for table in [
            Table(
                "entity",
                cols=[
                    Table.Column("id", int, True, False, False, None, None),
                    Table.Column("name", str, False, False, True, None, None),
                ]
            ),
            Table(
                "state",
                cols=[
                    Table.Column("id", int, True, False, False, None, None),
                    Table.Column("class", str, False, False, True, None, None),
                    Table.Column("name", str, False, False, True, None, None),
                    Table.Column("value", int, False, False, False, None, None),
                ]
            ),
            Table(
                "touch",
                cols=[
                    Table.Column("id", int, True, False, False, None, None),
                    Table.Column("ts", datetime.datetime, False, False, False, None, None),
                    Table.Column("sbjct", int, False, False, False, None, "entity"),
                    Table.Column("state", int, False, False, False, None, "state"),
                    Table.Column("objct", int, False, True, False, None, "entity"),
                ]
            ),
            Table(
                "note",
                cols=[
                    Table.Column("touch", int, False, False, False, None, "touch"),
                    Table.Column("text", str, False, True, False, None, None),
                    Table.Column("html", str, False, True, False, None, None),
                ]
            )]
    )

    @classmethod
    def populate(cls, con, items, log=None):
        log = log or LogManager().get_logger("turberfield.dialogue.schema.populate")
        states = [i for i in items if type(i) is enum.EnumMeta]
        entities = [i for i in items if i not in states]
        rv = 0
        for state in states:
            for defn in state:
                try:
                    Insertion(
                        cls.tables["state"],
                        data={
                            "class": defn.__objclass__.__name__,
                            "name": defn.name,
                            "value": defn.value
                        }
                    ).run(con)
                except sqlite3.IntegrityError as e:
                    log.warning(e)
                    con.rollback()
                except Exception as e:
                    log.error(e)
                    con.rollback()
                else:
                    rv += 1

        for entity in entities:
            try:
                Insertion(
                    cls.tables["entity"],
                    data={
                        "name": getattr(
                            entity, "_name", getattr(
                                entity,
                                "name",
                                entity.__class__.__name__
                            )
                        )
                    }
                ).run(con)
            except sqlite3.IntegrityError as e:
                log.warning(e)
                con.rollback()
            except Exception as e:
                log.error(e)
                con.rollback()
            else:
                rv += 1
        return rv

    @classmethod
    def reference(cls, con, items):
        cur = con.cursor()
        for item in items:
            if isinstance(item, enum.Enum):
                cur.execute(
                    "select * from state where class=:cls and name=:name",
                    {"cls": item.__objclass__.__name__, "name": item.name}
                )
                yield cur.fetchone()

            else:
                cur.execute(
                    "select * from entity where name=:name",
                    dict(
                        name=getattr(
                            item,
                            "_name",
                            getattr(
                                item,
                                "name",
                                item.__class__.__name__
                            )
                        )
                    )
                )
                yield cur.fetchone()
        cur.close()

    @classmethod
    def touch(
        cls, con, sbjct, state,
        objct=None, ts=None,
        text="", html="",
        log=None
    ):
        refs = list(cls.reference(con, [sbjct, state, objct]))
        op = Insertion(
            cls.tables["touch"],
            data={
                "ts": ts or datetime.datetime.utcnow(),
                "sbjct": refs[0]["id"],
                "state": refs[1]["id"],
                "objct": refs[2] and refs[2]["id"]
            }
        )
        if log is not None:
            log.debug(op.sql)
        cur = op.run(con)
        rv = cur.lastrowid
        cur.close()
        return rv

    @classmethod
    def note(
        cls, con, sbjct, state,
        objct=None, ts=None,
        text="", html="",
        log=None
    ):
        rv = cls.touch(con, sbjct, state, objct, ts, log=log)

        op = Insertion(
            cls.tables["note"],
            data={
                "touch": rv,
                "text": text,
                "html": html,
            }
        )
        if log is not None:
            log.debug(op.sql)
        cur = op.run(con)
        rv = cur.lastrowid
        cur.close()
        return rv

class Selection(SQLOperation):

    @property
    def sql(self):
        lines = []
        for table in self.tables:
            lines.append(
                "select {columns} from {table.name}".format(
                    table=table,
                    columns=", ".join(i.name for i in table.cols),
                )
            )
        return (";\n".join(lines), {})

    def run(self, con, log=None):
        cur = super().run(con)
        return cur.fetchall()
